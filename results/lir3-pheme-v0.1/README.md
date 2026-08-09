# LIR-3 sealed PHEME splits

The public inventory binds two disjoint, previously unused PHEME case sets while
keeping tweet text, identities, and normalized rows local:

- development: 417 cases, 5,000 claims;
- confirmatory: 425 cases, 5,000 claims; and
- overlap: zero cases.

The case-set and normalized-file SHA-256 digests in `inventory.json` make the
local inputs auditable without redistributing tweet content.
