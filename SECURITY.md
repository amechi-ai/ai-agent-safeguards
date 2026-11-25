# Security policy

This is an experimental specification and in-process Python fixture, not a deployed security boundary. No production version is supported.

## Reporting
Private vulnerability reporting must remain enabled for this repository. Submit sensitive findings privately using [Report a vulnerability](https://github.com/amechi-ai/ai-agent-safeguards/security/advisories/new). If the private reporting form is unavailable, open a public issue titled “Private reporting channel unavailable” and tag @amechi-ai, requesting restoration of the private reporting feature or a secure contact route. Include no vulnerability details or evidence, and wait for a verified private channel before transmitting them. Maintainers must restore the reporting feature or arrange a usable private contact route before soliciting sensitive reports. For non-sensitive design weaknesses, use a public issue. For vulnerabilities in another provider's systems, use that provider's authorised disclosure process.

Include affected version, expected and observed behaviour, scope, reproducible synthetic evidence, impact, and proposed mitigation if known. Do not post credentials, client data, live attack payloads, or private infrastructure details. Do not test real systems or agents without their owner's explicit permission.

Maintainers should acknowledge, triage, agree a disclosure plan and record remediation status; no fixed response SLA is promised. Avoid premature disclosure of exploitable details. Use isolated synthetic tests, no production credentials, no privileged workflows, and no self-hosted runners for untrusted contributions. GitHub-hosted CI is not a network-isolated adversarial sandbox. See VALIDATION_STATUS.md.
