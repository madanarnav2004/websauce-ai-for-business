# Private manifest helper

Requires Python 3.9+. No network or image libraries. All paths below belong to a private workspace, never this public skill. Use one writer per manifest; this lightweight local helper is not a concurrent job server.

```sh
python3 scripts/pack.py --manifest /private/batch/manifest.json init --business /private/business.json
python3 scripts/pack.py --manifest /private/batch/manifest.json ingest lamp-a /private/source.jpg \
  --source 'Authorized source photo caption' --timestamp '2026-01-02T10:00:00+00:00' \
  --price 240 --currency USD --evidence 'Owner confirmed caption is retail price'
```

Edit manifest product fields from observed evidence: `subject`, `subject_status` (`selected` or `unresolved`), `category`, `copy` (`name`, `description`, `caption`, `hashtags`, optional `seo`), `unresolved`, `reel_decision`, and `price.tax_status` (`inclusive`, `exclusive`, `not_applicable`, `unknown`) with `tax_note`. Record the source for resolved facts in the notes; do not delete conflicting evidence. Resolve price conflicts only with an actual clarification.

Originals and assets are copied into content-addressed names. `asset` records the inspected output and complete prompt; it does not perform QA itself:

```sh
python3 scripts/pack.py --manifest /private/batch/manifest.json asset lamp-a catalog /private/generated.png \
  --qa pass --notes 'Describe actual geometry, finish, lighting and crop checks' --prompt /private/catalog-prompt.txt
python3 scripts/pack.py --manifest /private/batch/manifest.json check --stage review
python3 scripts/pack.py --manifest /private/batch/manifest.json review --output /private/batch/review.html
```

`check` returns nonzero for missing/changed files, unresolved subject/price, incomplete stills or copy. Review can expose unresolved tax/stock; publication checks block unresolved facts and absent exact-version approval. A human visual comparison is still essential; no helper can certify fidelity from hashes.

Record approval only after the actual owner decision:

```sh
python3 scripts/pack.py --manifest /private/batch/manifest.json approve lamp-a --evidence 'Actual owner decision and scope'
python3 scripts/pack.py --manifest /private/batch/manifest.json intent lamp-a \
  --channel whatsapp --target 'Verified authorized recipient' --authorization 'Actual delivery request'
python3 scripts/pack.py --manifest /private/batch/manifest.json receipt KEY \
  --state verified --evidence 'Observed outgoing attachment count, timestamp and exposed ID'
```

WhatsApp intent permits a QA-passing review draft without public-release approval. Instagram/website intent additionally needs exact-version approval and resolved tax/facts. Intent is not an external action. State `uncertain` blocks blind retries; only an observed `not_submitted` reconciliation allows another intent. Verified receipts are immutable.

For catalog proposals, provide `public_media` (already approved uploaded HTTPS URLs), `image_labels`, `catalog_id` for an existing record or confirmed `stock_quantity` for a new product. `catalog-patch PRODUCT --existing /private/current-product.json` prints a minimal update excluding stock. Without `--existing`, it proposes a deterministic create-if-absent. Reconcile existing sale prices explicitly. The helper never touches live catalogs.

Keep public media URL acquisition separate from draft image generation. Transport-only `public_media` URLs are excluded from the approval fingerprint so uploading unchanged approved files does not require repeat approval. Before release, the operator must verify that each URL serves the corresponding approved asset, in the reviewed order. The helper cannot verify remote bytes. Uploading private originals or internal manifests is never required. Business configuration must not contain credentials; reuse authenticated account tools separately.
