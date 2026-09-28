#!/usr/bin/env python3
"""Private retail pack bookkeeping. No network, AI, messaging or publication calls."""
import argparse
import base64
import hashlib
import html
import json
import math
import mimetypes
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
    tmp.replace(path)


def fresh(business):
    return {'version': 1, 'business': business, 'products': {}, 'deliveries': []}


def product(m, pid):
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,79}', pid):
        raise ValueError('Use a stable lowercase product ID')
    return m['products'].setdefault(pid, {
        'id': pid, 'subject': '', 'subject_status': 'unresolved', 'sources': [],
        'price': {'amount': None, 'currency': '', 'status': 'missing', 'evidence': [],
                  'tax_status': 'unknown', 'tax_note': ''},
        'assets': {}, 'copy': {}, 'unresolved': [], 'stock_quantity': None,
        'reel_decision': {'selected': False, 'reason': 'Not assessed'}, 'approval': None,
    })


def ingest(m, root, pid, path, source, timestamp, amount=None, currency='', evidence=''):
    p = product(m, pid)
    if amount is not None and (not math.isfinite(amount) or amount < 0):
        raise ValueError('Price must be a finite nonnegative number')
    path = Path(path)
    sha = digest(path)
    if not any(s['sha256'] == sha for s in p['sources']):
        relative = Path('originals') / (pid + '-' + sha[:16] + path.suffix.lower())
        dest = Path(root) / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.resolve() != path.resolve():
            shutil.copy2(path, dest)
        p['sources'].append({'path': str(relative), 'sha256': sha,
                             'source': source, 'timestamp': timestamp})
    if amount is not None:
        price = p['price']
        item = {'amount': amount, 'currency': currency, 'evidence': evidence,
                'source_sha256': sha, 'timestamp': timestamp}
        if item not in price['evidence']:
            price['evidence'].append(item)
        if price['amount'] is not None and (price['amount'], price['currency']) != (amount, currency):
            price['status'] = 'conflict'
        elif price['status'] != 'conflict':
            price.update(amount=amount, currency=currency,
                         status='confirmed' if evidence.strip() and re.fullmatch('[A-Z]{3}', currency) else 'unresolved')
    return p


def fingerprint(m, p):
    # Storage URLs arrive after approved images are uploaded. Their binding to the
    # approved file hashes must be verified by the channel operator before release.
    content = {k: v for k, v in p.items() if k not in ('approval', 'public_media')}
    return hashlib.sha256(json.dumps({'business': m['business'], 'product': content},
                                    sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def issues(m, p, root, stage='review'):
    errors = []
    if p.get('subject_status') != 'selected' or not p.get('subject', '').strip():
        errors.append('subject unresolved')
    if not p['sources']:
        errors.append('originals missing')
    price = p['price']
    if price.get('status') != 'confirmed' or not price.get('evidence'):
        errors.append('selling price missing or conflicting')
    amount = price.get('amount')
    if isinstance(amount, bool) or not isinstance(amount, (int, float)) or not math.isfinite(amount) or amount < 0:
        errors.append('invalid price amount')
    if not re.fullmatch('[A-Z]{3}', price.get('currency', '')):
        errors.append('currency missing')
    for item in p['sources'] + list(p['assets'].values()):
        file = Path(root) / item['path']
        if not file.is_file() or digest(file) != item['sha256']:
            errors.append('missing or changed file: ' + item['path'])
    if stage != 'intake':
        stills = [a for a in p['assets'].values() if a.get('kind', 'photo') == 'photo']
        passed = [a for a in stills if a.get('qa') == 'pass' and a.get('qa_notes', '').strip()]
        if not 3 <= len(passed) <= 4:
            errors.append('need three to four QA-passing stills')
        if len({a['sha256'] for a in passed}) != len(passed):
            errors.append('same photo reused as multiple outputs')
        if any(a.get('qa') != 'pass' for a in p['assets'].values()):
            errors.append('selected assets include failed or unreviewed output')
        for field in ('name', 'description', 'caption', 'hashtags'):
            if not p['copy'].get(field):
                errors.append('copy missing: ' + field)
        if p.get('reel_decision', {}).get('selected') and not any(
                a.get('kind') == 'video' and a.get('qa') == 'pass' for a in p['assets'].values()):
            errors.append('selected reel missing or not verified')
    if stage == 'publish':
        if p.get('unresolved'):
            errors.append('unresolved product facts')
        if price.get('tax_status') not in ('inclusive', 'exclusive', 'not_applicable'):
            errors.append('tax treatment unresolved')
        approval = p.get('approval') or {}
        if approval.get('fingerprint') != fingerprint(m, p) or not approval.get('evidence'):
            errors.append('exact pack has no current owner approval')
    return errors


def record_asset(p, root, slot, path, qa, notes, prompt=None, attempt=1, kind='photo'):
    if not re.fullmatch(r'[a-z0-9_-]+', slot):
        raise ValueError('Invalid asset slot')
    if attempt not in (1, 2, 3):
        raise ValueError('Maximum initial generation plus two revisions')
    if qa == 'pass' and not notes.strip():
        raise ValueError('Passing QA needs concrete observations')
    if prompt and not Path(prompt).is_file():
        raise ValueError('Prompt file missing')
    path = Path(path).resolve()
    # Versioned content paths preserve prior approval snapshots and rejected attempts.
    sha = digest(path)
    relative = Path('assets') / (p['id'] + '-' + slot + '-' + sha[:16] + path.suffix)
    dest = Path(root) / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.resolve() != path:
        shutil.copy2(path, dest)
    p['assets'][slot] = {'path': str(relative), 'sha256': sha, 'kind': kind,
                        'qa': qa, 'qa_notes': notes, 'attempt': attempt,
                        'prompt': Path(prompt).read_text() if prompt else '',
                        'source_hashes': [s['sha256'] for s in p['sources']]}


def approve(m, p, root, evidence):
    errors = issues(m, p, root)
    if errors or not evidence.strip():
        raise ValueError('; '.join(errors) or 'Actual owner approval evidence required')
    p['approval'] = {'fingerprint': fingerprint(m, p), 'evidence': evidence, 'at': now()}


def intent(m, p, root, channel, target, authorization):
    errors = issues(m, p, root, 'review' if channel == 'whatsapp' else 'publish')
    if errors:
        raise ValueError('; '.join(errors))
    if not target.strip() or not authorization.strip():
        raise ValueError('Exact destination and request authorization required')
    fp = fingerprint(m, p)
    key = hashlib.sha256((fp + channel + target).encode()).hexdigest()[:24]
    prior = next((d for d in m['deliveries'] if d['key'] == key), None)
    if prior and prior['state'] != 'not_submitted':
        raise ValueError('Already attempted; inspect/reconcile the existing destination receipt')
    entry = {'key': key, 'product': p['id'], 'fingerprint': fp, 'channel': channel,
             'target': target, 'authorization': authorization, 'state': 'intent', 'at': now()}
    if prior:
        prior.setdefault('history', []).append({k: v for k, v in prior.items() if k != 'history'})
        prior.update(entry)
    else:
        m['deliveries'].append(entry)
    return key


def receipt(m, key, state, evidence):
    if not evidence.strip():
        raise ValueError('Observed evidence required')
    row = next(d for d in m['deliveries'] if d['key'] == key)
    if row['state'] == 'verified':
        raise ValueError('Verified receipts are immutable')
    row.update(state=state, receipt=evidence, checked_at=now())


def catalog_patch(p, existing=None):
    """Never write inventory for existing products. Caller separately checks release approval."""
    copy_fields = p['copy']
    media = p.get('public_media', [])
    if not media or not all(isinstance(u, str) and u.startswith('https://') for u in media):
        raise ValueError('Verified public HTTPS media URLs required')
    if not copy_fields.get('name') or not copy_fields.get('description') or not p.get('category'):
        raise ValueError('Name, description and category required')
    patch = {k: copy_fields[k] for k in ('name', 'description')}
    patch.update(category=p['category'], price=p['price']['amount'], images=media,
                 image_labels=p.get('image_labels', {}))
    if existing is not None:
        if not p.get('catalog_id') or existing.get('id') != p['catalog_id']:
            raise ValueError('Existing catalog ID must match explicitly')
        if existing.get('sale_price') is not None:
            raise ValueError('Existing sale price needs explicit resolution before price replacement')
        return {'id': existing['id'], 'operation': 'update', 'fields': patch}
    stock = p.get('stock_quantity')
    if isinstance(stock, bool) or not isinstance(stock, int) or stock < 0:
        raise ValueError('Confirmed new-product stock required')
    patch.update(stock_quantity=stock, is_active=True, publication_status='published')
    return {'id': p['id'], 'operation': 'create_if_absent', 'fields': patch}


def review_html(m, root):
    esc = lambda value: html.escape(str(value))
    out = ['<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">',
           '<title>Private product review</title><style>body{font:16px/1.6 system-ui;background:#f5f1ea;color:#242321;max-width:1200px;margin:auto;padding:32px}h1,h2{line-height:1.2}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}figure{margin:0;background:white;padding:12px}img,video{width:100%;max-height:560px;object-fit:contain}pre{white-space:pre-wrap;background:white;padding:20px}small{color:#666}</style>',
           '<h1>' + esc(m['business'].get('business', 'Product')) + ' · private review</h1><p>Drafts for review. No public publication implied.</p>']
    for p in m['products'].values():
        price = p['price']
        out += ['<section><h2>' + esc(p['copy'].get('name') or p['id']) + '</h2>',
                '<p>' + esc(f"{price['currency']} {price['amount']} · {price.get('tax_note') or 'Tax treatment unresolved'}") + '</p><div class="grid">']
        for label, a in [("Original", s) for s in p['sources']] + list(p['assets'].items()):
            path = Path(root) / a['path']
            if not path.is_file():
                out.append('<p>Missing: ' + esc(a['path']) + '</p>')
                continue
            mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
            url = 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode()
            tag = '<video controls src="' + url + '"></video>' if mime.startswith('video/') else '<img src="' + url + '" alt="' + esc(label) + '">'
            out.append('<figure>' + tag + '<figcaption>' + esc(label) + '<br><small>' + esc(a.get('qa_notes', 'Source photograph')) + '</small></figcaption></figure>')
        out += ['</div><h3>Copy and open questions</h3><pre>' + esc(json.dumps({'copy': p['copy'], 'unresolved': p['unresolved'], 'reel': p['reel_decision'], 'checks': issues(m, p, root)}, ensure_ascii=False, indent=2)) + '</pre></section>']
    return '\n'.join(out) + '</html>'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    sub = parser.add_subparsers(dest='cmd', required=True)
    init = sub.add_parser('init'); init.add_argument('--business', required=True, type=Path)
    add = sub.add_parser('ingest')
    add.add_argument('product'); add.add_argument('file', type=Path)
    add.add_argument('--source', required=True); add.add_argument('--timestamp', required=True)
    add.add_argument('--price', type=float); add.add_argument('--currency', default=''); add.add_argument('--evidence', default='')
    asset = sub.add_parser('asset'); asset.add_argument('product'); asset.add_argument('slot'); asset.add_argument('file', type=Path)
    asset.add_argument('--qa', choices=['pass', 'fail', 'uncertain'], required=True); asset.add_argument('--notes', required=True)
    asset.add_argument('--prompt', type=Path); asset.add_argument('--attempt', type=int, default=1); asset.add_argument('--kind', choices=['photo', 'video'], default='photo')
    check = sub.add_parser('check'); check.add_argument('--stage', choices=['intake', 'review', 'publish'], default='review')
    rev = sub.add_parser('review'); rev.add_argument('--output', type=Path, required=True)
    ap = sub.add_parser('approve'); ap.add_argument('product'); ap.add_argument('--evidence', required=True)
    it = sub.add_parser('intent'); it.add_argument('product'); it.add_argument('--channel', choices=['whatsapp', 'instagram', 'website'], required=True)
    it.add_argument('--target', required=True); it.add_argument('--authorization', required=True)
    rc = sub.add_parser('receipt'); rc.add_argument('key'); rc.add_argument('--state', choices=['verified', 'uncertain', 'not_submitted'], required=True); rc.add_argument('--evidence', required=True)
    cp = sub.add_parser('catalog-patch'); cp.add_argument('product'); cp.add_argument('--existing', type=Path)
    a = parser.parse_args(); root = a.manifest.parent
    if a.cmd == 'init':
        if a.manifest.exists():
            raise ValueError('Manifest already exists; resume it')
        save(a.manifest, fresh(json.loads(a.business.read_text())))
        return
    m = json.loads(a.manifest.read_text())
    if a.cmd == 'ingest':
        ingest(m, root, a.product, a.file, a.source, a.timestamp, a.price, a.currency, a.evidence)
    elif a.cmd == 'asset':
        record_asset(m['products'][a.product], root, a.slot, a.file, a.qa, a.notes, a.prompt, a.attempt, a.kind)
    elif a.cmd == 'check':
        report = {pid: issues(m, p, root, a.stage) for pid, p in m['products'].items()}
        print(json.dumps(report, indent=2)); raise SystemExit(1 if any(report.values()) or not report else 0)
    elif a.cmd == 'review':
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(review_html(m, root)); print(a.output); return
    elif a.cmd == 'approve':
        approve(m, m['products'][a.product], root, a.evidence)
    elif a.cmd == 'intent':
        print(intent(m, m['products'][a.product], root, a.channel, a.target, a.authorization))
    elif a.cmd == 'receipt':
        receipt(m, a.key, a.state, a.evidence)
    elif a.cmd == 'catalog-patch':
        p = m['products'][a.product]
        errors = issues(m, p, root, 'publish')
        if errors: raise ValueError('; '.join(errors))
        print(json.dumps(catalog_patch(p, json.loads(a.existing.read_text()) if a.existing else None), indent=2)); return
    save(a.manifest, m)


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, StopIteration) as exc:
        raise SystemExit(str(exc))
