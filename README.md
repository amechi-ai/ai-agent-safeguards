# AI Agent Safeguards

**Agent Authority and Collaboration Safeguards: a behavioural protocol, technical safeguard requirements and a Python reference model for governing AI agents.**

What should happen when an AI agent receives an instruction that exceeds its authority? This experimental, research-stage initiative works through how governance principles on agent authority and collaboration can be translated into technically enforceable controls. It contains nine behavioural clauses, 12 technical requirements with a threat model, 37 proposed implementation scenarios, a Python reference model with 11 in-process tests, and an independent AI-assisted review of an earlier revision.

Experimental AI agent governance initiative. These materials are for scrutiny, controlled testing and improvement, not a deployed security product or a guarantee of protection.

Origin: these are the supporting materials for the article [The AI Swarm: So Good at Being Bad](https://www.linkedin.com/pulse/ai-swarm-so-good-being-bad-amechi-isiekwena-opfmc). The protocol and reference model were developed under the author's direction with AI assistance, as the article describes.

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

The review pack and the model's docstring record slightly different invocations (`-q`, and without `-I`). Those files are preserved unchanged as evidence; the command above is the recommended one.

No external dependencies are required. Do not deploy this in-process fixture as an agent security boundary. Use synthetic data, test identities and isolated environments for future adversarial testing; avoid real credentials and live third-party effects.

## Contributing
Criticise the protocol, propose concrete revisions, provide reproducible tests, report residual risks and measure effects on legitimate work. Distinguish behavioural compliance, host enforcement, and evidence of real-world outcomes. See [CONTRIBUTING.md](CONTRIBUTING.md) for suggested contribution and safe testing practices. A licence has not yet been selected; public availability alone does not grant general reuse rights.
