# Validation status

Baseline: v0.4 review pack, 19 November 2026; latest recorded local rerun 25 November 2026.

| Evidence | Status |
| --- | --- |
| Initial reference model | 7 tests passed; independent probes exposed weaknesses |
| Earlier revised model | 9 tests and 7 evidence claims independently confirmed by Claude (AI-assisted reviewer) |
| Current recovered model | 11 tests passed locally; independent confirmation pending |
| T01–T37 implementation scenarios | 0/37 run |
| Prompt behavioural effectiveness and resistance to live-agent persuasion | Not established |
| Enforcement against untrusted code, deployment isolation, production readiness | Not established |

Earlier verified SHA-256: `7bfc00891de17100fa441ba3c35c8ef3731d6e8baf76a21cb259a5024f8f0adf` (exact earlier source not supplied). Current fixture SHA-256: `fd68d12fb3c96b7957284db3412f1b1e468d7fbf46fe4316e682ef34ac26aae3`.

J1, J4, J5 remain open because their text is missing. Group-size owner-approval path is not exercised. Authorised collaborators can still encode undeclared signals in shared content; semantic misuse within broadly granted permissions remains possible. The expanded public ten-point prompt has not been independently validated as a whole.

The fixture uses synthetic identities and in-process enforcement; test success is evidence about fixture behaviour only. A CI rerun does not advance implementation scenario status. New evidence must name the exact version, environment, assumptions, independent observation, expected/actual result, and coverage limits. Record benign-work regressions separately. See the original review pack and independent Validator report for full provenance.
