# The AI Swarm: So Good at Being Bad — supporting materials

Experimental AI agent governance initiative. These materials are for scrutiny, controlled testing and improvement, not a deployed security product or a guarantee of protection.

## Contents
- `Agent_Authority_Safeguards_Review_Pack_v0_4.md`: original nine behavioural clauses, 12 technical requirements, threat model, coverage map, 37 implementation scenarios, reconciliation of Validator findings, evidence and limitations. Only the private library link to the Python model was replaced by a relative link for portability.
- `safeguard_prototype.py`: latest recovered Python reference model, unchanged; 11 in-process tests.
- `Independent_Validator_Report_2026-11-19.md`: recovered independent AI-assisted review of the earlier nine-test model. Requester handle omitted for public distribution; substantive text unchanged.

## Evidence status
On 19 November 2026 the independent AI reviewer confirmed nine tests and seven claimed fixture behaviours against SHA-256 `7bfc00891de17100fa441ba3c35c8ef3731d6e8baf76a21cb259a5024f8f0adf`. That exact earlier source file is not included. The included later revision hashes to `fd68d12fb3c96b7957284db3412f1b1e468d7fbf46fe4316e682ef34ac26aae3`. Its 11 tests passed locally again on 25 November 2026. This rerun is not independent validation. All T01–T37 implementation scenarios remain NOT RUN in the recovered record. J1, J4 and J5 remain open because their text is unavailable in the supplied confirmation. The group-size owner-approval path is untested. No live-agent resistance, adversarial code enforcement, deployment isolation, or production readiness is established. Authorised shared content can still carry undeclared signals.

## Run the reference tests
In an isolated local environment with Python 3, run:

```sh
python3 -I safeguard_prototype.py -v
```

No external dependencies are required. Do not deploy this in-process fixture as an agent security boundary. Use synthetic data, test identities and isolated environments for future adversarial testing; avoid real credentials and live third-party effects.

## Contributing
Criticise the protocol, propose concrete revisions, provide reproducible tests, report residual risks and measure effects on legitimate work. Distinguish behavioural compliance, host enforcement, and evidence of real-world outcomes. See [CONTRIBUTING.md](CONTRIBUTING.md) for suggested contribution and safe testing practices. The owner has conditionally approved Apache-2.0 for software and CC BY 4.0 for original documentation. No licence grant is effective through this notice: rights verification and third-party exclusions remain pending. See [LICENSING.md](LICENSING.md).

## Start here and contribute
- [Copy-and-paste foundational safeguards](AGENT_SAFEGUARD_PROTOCOL.md) — accessible ten-point adaptation; not independently validated as a whole.
- [Validation status](VALIDATION_STATUS.md) and [research roadmap](ROADMAP.md).
- [Project governance](GOVERNANCE.md), [security reporting](SECURITY.md), [code of conduct](CODE_OF_CONDUCT.md), and [citation metadata](CITATION.cff).
- [Proposed alpha release notes](RELEASE_NOTES_v0.4.0-alpha.1.md) and [changelog](CHANGELOG.md).

The proposed CI workflow runs only the standard-library fixture tests; it does not certify security or run the 37 implementation scenarios.
