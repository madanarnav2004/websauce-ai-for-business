# Acceptance scenarios

| Scenario | Expected outcome |
| --- | --- |
| Noisy background | Select precise product; exclude overlapping fixtures; preserve visible geometry. |
| Ambiguous subject | Clarify before generation. |
| Multiple views | One product, all source hashes retained. |
| Duplicate input | Resume existing source; conflicting price is not overwritten. |
| Missing/conflicting price or tax | Block public price use until resolved. |
| Interrupted generation | Reuse valid completed slots. |
| Attractive but changed geometry | Fail QA; bounded targeted revision. |
| File changed after QA | Hash mismatch blocks review/release. |
| Copy changed after approval | Fingerprint mismatch blocks publication. |
| New product with unknown stock | Block catalog export. |
| Existing stock changed by staff | Preserve current inventory; patch excludes stock. |
| Uncertain delivery | Reconcile before retry. |
| WhatsApp pack | Correct recipient, exact price, matching attachment count and observed sent receipt. |
| Blender reel | Source-faithful cutout, inspected MP4 and editable blend file. |

Automated tests verify bookkeeping, not subjective fidelity. Record specific visual judgments and channel evidence for each real pilot. Synthetic examples and local tests are not live publication receipts.
