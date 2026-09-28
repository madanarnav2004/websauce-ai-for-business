---
name: retail-content
description: Turn noisy retail product photos and confirmed selling prices into three to four faithful marketing photos, captions and listing copy, with optional Blender reels. Use for showroom or WhatsApp photo intake, review packs and authorized delivery or publication; not product redesign or full 3D reconstruction.
---

# Retail content

Give a shop owner a useful marketing pack from photographs of the actual item being sold. Originals define product identity. This is an agent-operated workflow, not a connected service or scheduler.

## Establish the source

Use a private work directory outside this skill. Read the user's request and private business configuration for brand, recipients, destinations and authorization. The bundled [business example](assets/example-business.json) is fictional. Keep real originals, messages, prices, credentials and receipts out of public examples and Git.

Read [intake](references/intake.md). Inspect every original at useful resolution, select the intended product and group its different views. Confirm selling-price meaning and currency; tax and stock remain unknown unless evidenced. Never substitute blurred previews or unrelated catalog images. Use the [manifest helper](references/manifest.md) to track source hashes, price evidence and durable progress.

## Create the pack

Follow [photography](references/photography.md). Use the session's built-in image-generation tool, one asset per prompt. Inspect local sources before editing; no paid API fallback without explicit user choice.

Produce three to four distinct photographs per product: catalog hero, believable lifestyle scene, supported detail or second scene, and an optional useful fourth composition. Reels supplement these stills. Do not invent angles exposing unseen geometry. Preserve product proportions; adapt the canvas for each channel.

Save exact prompts, source references, final files and specific fidelity notes. Compare every output with the original. Allow at most two targeted revisions per failed asset, then flag it rather than accepting distortion. Resume successful slots without regenerating them.

Write concise captions, relevant hashtags, factual description and SEO copy. Label suggested names as suggestions, not manufacturer models. Do not infer material composition, measurements, wattage, warranties, discounts or stock. Keep catalog masters text-free; put verified branding and price copy in separate social layouts.

Use [Blender](references/blender.md) when motion helps explain the product. Default to an 8–12-second vertical photo-based scene without simulated unseen sides. Record why the reel was selected or omitted.

## Review and deliver

Build a private side-by-side review containing originals, generated assets, exact prices/copy, unresolved facts and optional video. QA and owner approval are separate decisions. Run helper review checks before presenting the pack; do not call a pack finished if fewer than three assets pass.

Read [WhatsApp delivery](references/whatsapp-delivery.md) when the user asks to send results back. Verify the authorized recipient, match each pack to its product/price, send once and record the observed receipt. This does not authorize public posting.

For website or Instagram work, read [publication](references/publication.md). Respect the requested review policy. Prepare everything before requesting first-batch approval. Verify the exact account and reviewed version, record intent, act once and verify the actual result. Reconcile uncertain actions before retrying. Missing access blocks that channel, not independent preparation.

## Validate

Run `python3 scripts/test_pack.py` from this skill directory. Local synthetic tests establish helper behavior, not photographic quality or live account access. Follow [acceptance scenarios](references/acceptance.md) for visual and channel verification. Label untested integrations honestly.
