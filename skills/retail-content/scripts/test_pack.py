#!/usr/bin/env python3
"""Synthetic, offline regression tests; no live clients, sessions or providers."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
import pack


class PackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.m = pack.fresh({'business': 'Example Studio', 'website': 'https://shop.example.org'})
        source = self.root / 'source.jpg'
        source.write_bytes(b'synthetic fixture source, not real media')
        self.source = source
        self.p = pack.ingest(self.m, self.root, 'lamp-a', source, 'Example caption',
                             '2026-01-02T10:00:00Z', 240, 'USD', 'Synthetic confirmed selling price')

    def ready(self):
        self.p.update(subject='Single fictional desk lamp', subject_status='selected', category='lighting')
        self.p['copy'] = {'name': 'Example lamp', 'description': 'Fictional product for tests.',
                          'caption': 'Example only.', 'hashtags': ['#Example']}
        self.p['price'].update(tax_status='inclusive', tax_note='Synthetic inclusive price')
        for slot in ['catalog', 'lifestyle', 'detail']:
            file = self.root / (slot + '.png')
            file.write_bytes(('synthetic ' + slot).encode())
            pack.record_asset(self.p, self.root, slot, file, 'pass', 'Synthetic test QA, not a real visual assessment')
        return self.p

    def test_duplicate_ingestion_resumes_and_conflicting_price_is_not_lost(self):
        pack.ingest(self.m, self.root, 'lamp-a', self.source, 'Example caption', '2026-01-02T10:00:00Z', 240, 'USD', 'Synthetic confirmed selling price')
        self.assertEqual(len(self.p['sources']), 1)
        self.assertEqual(len(self.p['price']['evidence']), 1)
        pack.ingest(self.m, self.root, 'lamp-a', self.source, 'New caption', '2026-01-02T11:00:00Z', 300, 'USD', 'Conflicting price')
        self.assertEqual(self.p['price']['status'], 'conflict')
        self.assertEqual(self.p['price']['amount'], 240)
        self.assertEqual(len(self.p['price']['evidence']), 2)

    def test_missing_price_and_ambiguous_subject_block_review(self):
        self.p['price']['status'] = 'missing'
        errors = pack.issues(self.m, self.p, self.root)
        self.assertIn('subject unresolved', errors)
        self.assertIn('selling price missing or conflicting', errors)

    def test_multiple_views_one_product_and_interrupted_resume(self):
        self.ready()
        second = self.root / 'other-view.jpg'; second.write_bytes(b'another source view')
        pack.ingest(self.m, self.root, 'lamp-a', second, 'Other view', '2026-01-02T11:00:00Z')
        self.assertEqual(len(self.p['sources']), 2)
        self.assertEqual(len(self.p['assets']), 3)
        manifest = self.root / 'manifest.json'; pack.save(manifest, self.m)
        loaded = json.loads(manifest.read_text())
        self.assertEqual(loaded['products']['lamp-a']['assets'], self.p['assets'])

    def test_changed_asset_invalidates_file_check(self):
        self.ready()
        (self.root / self.p['assets']['catalog']['path']).write_bytes(b'changed')
        self.assertTrue(any('changed file' in e for e in pack.issues(self.m, self.p, self.root)))

    def test_changed_copy_or_destination_invalidates_approval(self):
        self.ready(); pack.approve(self.m, self.p, self.root, 'Synthetic owner approved')
        self.assertEqual(pack.issues(self.m, self.p, self.root, 'publish'), [])
        self.p['copy']['caption'] = 'Changed'
        self.assertIn('exact pack has no current owner approval', pack.issues(self.m, self.p, self.root, 'publish'))
        pack.approve(self.m, self.p, self.root, 'Synthetic updated approval')
        self.m['business']['website'] = 'https://other.example.org'
        self.assertIn('exact pack has no current owner approval', pack.issues(self.m, self.p, self.root, 'publish'))

    def test_storage_url_assignment_does_not_reapprove_unchanged_content(self):
        self.ready(); pack.approve(self.m, self.p, self.root, 'Synthetic owner approved')
        self.p['public_media'] = ['https://cdn.example.org/approved-asset.png']
        self.assertEqual(pack.issues(self.m, self.p, self.root, 'publish'), [])

    def test_same_image_cannot_fill_three_slots(self):
        self.ready()
        self.p['assets']['detail'] = copy.deepcopy(self.p['assets']['catalog'])
        self.assertIn('same photo reused as multiple outputs', pack.issues(self.m, self.p, self.root))

    def test_unknown_tax_blocks_publication_but_not_review_delivery(self):
        self.ready(); self.p['price']['tax_status'] = 'unknown'
        key = pack.intent(self.m, self.p, self.root, 'whatsapp', 'Example owner', 'Synthetic send request')
        self.assertTrue(key)
        with self.assertRaises(ValueError):
            pack.intent(self.m, self.p, self.root, 'instagram', 'example_account', 'Synthetic release request')

    def test_uncertain_send_requires_reconciliation_and_success_is_immutable(self):
        self.ready()
        args = (self.m, self.p, self.root, 'whatsapp', 'Example owner', 'Synthetic delivery request')
        key = pack.intent(*args)
        pack.receipt(self.m, key, 'uncertain', 'Synthetic timeout')
        with self.assertRaises(ValueError): pack.intent(*args)
        pack.receipt(self.m, key, 'not_submitted', 'Synthetic destination checked; not present')
        self.assertEqual(pack.intent(*args), key)
        pack.receipt(self.m, key, 'verified', 'Synthetic outgoing attachments observed')
        with self.assertRaises(ValueError): pack.intent(*args)
        with self.assertRaises(ValueError): pack.receipt(self.m, key, 'not_submitted', 'Do not rewrite success')

    def test_catalog_patch_preserves_current_stock_and_requires_new_stock(self):
        self.ready(); self.p['public_media'] = ['https://cdn.example.org/lamp.png']
        with self.assertRaises(ValueError): pack.catalog_patch(self.p)
        self.p['stock_quantity'] = 2
        new = pack.catalog_patch(self.p)
        self.assertEqual(new['fields']['stock_quantity'], 2)
        self.assertEqual(new['id'], pack.catalog_patch(self.p)['id'])
        self.p['catalog_id'] = 'existing-a'
        patch = pack.catalog_patch(self.p, {'id': 'existing-a', 'stock_quantity': 11})
        self.assertNotIn('stock_quantity', patch['fields'])
        with self.assertRaises(ValueError): pack.catalog_patch(self.p, {'id': 'wrong-id'})
        with self.assertRaises(ValueError): pack.catalog_patch(self.p, {'id': 'existing-a', 'sale_price': 100})

    def test_invalid_price_rejected_and_revision_budget_enforced(self):
        for price in [-1, float('nan'), float('inf')]:
            with self.assertRaises(ValueError):
                pack.ingest(self.m, self.root, 'lamp-a', self.source, 'source', 'unknown', price, 'USD', 'example')
        with self.assertRaises(ValueError):
            pack.record_asset(self.p, self.root, 'catalog', self.source, 'pass', 'test', attempt=4)

    def test_review_escapes_copy_and_exposes_open_questions(self):
        self.ready(); self.p['copy']['caption'] = '<script>bad()</script>'
        self.p['unresolved'] = ['Confirm stock']
        document = pack.review_html(self.m, self.root)
        self.assertNotIn('<script>', document)
        self.assertIn('&lt;script&gt;', document)
        self.assertIn('Confirm stock', document)


if __name__ == '__main__':
    unittest.main(verbosity=2)
