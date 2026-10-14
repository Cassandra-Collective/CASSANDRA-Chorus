# P9 signing dry run

Plan: `docs/implementations/2026-10-14-solo-prototypes.md`. Python 3.13.14, cryptography 46.0.3; release archive of commit `b2dcc9b8bfde` (1,126,841 bytes). Verifier: python -E -P verify.py ... (fresh process, started in an empty folder). One machine; throwaway key, deleted afterwards.

| Case | What was changed | Must be | Verifier said | As expected |
|---|---|---|---|---|
| genuine | the files as signed | accepted | accepted | yes |
| config-byte-flipped | one bit flipped in the configuration's first value | rejected | rejected: config: signature does not verify | yes |
| config-signature-flipped | one bit flipped in the configuration's signature | rejected | rejected: config: signature does not verify | yes |
| config-signature-truncated | the configuration's signature cut to 63 bytes | rejected | rejected: config: signature has 63 bytes, expected 64 | yes |
| wrong-public-key | the client holds a different public key | rejected | rejected: config: signature does not verify | yes |
| archive-modified | one bit flipped in the middle of the release archive | rejected | rejected: archive: SHA-256 or size does not match the manifest | yes |
| signature-cross-type | the configuration and its signature presented as the manifest and its signature | rejected | rejected: manifest: signature does not verify | yes |

All cases as expected: **yes**.
