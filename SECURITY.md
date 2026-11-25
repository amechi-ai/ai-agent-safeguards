# Security policy

This is an experimental specification and in-process Python fixture, not a deployed security boundary. No production version is supported.

## Reporting
Private vulnerability reporting must remain enabled for this repository. Use the following reporting channels, in order of preference:

1. **Primary:** submit sensitive findings privately using GitHub's [Report a vulnerability](https://github.com/amechi-ai/ai-agent-safeguards/security/advisories/new) form.
2. **Secondary:** if the form is unavailable or inaccessible, email the project's designated masked security contact at [nozzle-wears-7j@icloud.com](mailto:nozzle-wears-7j@icloud.com). Begin with a minimal, non-sensitive message requesting acknowledgement and, if needed, a suitable secure channel. Ordinary email is not guaranteed to provide end-to-end encryption. Do not send secrets, protected information or sensitive attachments before agreeing on an appropriate secure means of transmission.
3. **Last resort:** if neither private route works, open a public issue titled “Maintainer contact request” and tag @amechi-ai. Request a private contact route only; do not state or imply that you have discovered a vulnerability, or include any details or evidence. Wait for a verified private channel before transmitting sensitive information.

Maintainers must restore private reporting or arrange a usable private contact route if the established channels become unavailable. For non-sensitive design weaknesses, use a public issue. For vulnerabilities in another provider's systems, use that provider's authorised disclosure process.

Include affected version, expected and observed behaviour, scope, reproducible synthetic evidence, impact, and proposed mitigation if known. Do not post credentials, client data, live attack payloads, or private infrastructure details. Do not test real systems or agents without their owner's explicit permission.

Maintainers should acknowledge, triage, agree a disclosure plan and record remediation status; no fixed response SLA is promised. Avoid premature disclosure of exploitable details. Use isolated synthetic tests, no production credentials, no privileged workflows, and no self-hosted runners for untrusted contributions. GitHub-hosted CI is not a network-isolated adversarial sandbox. See VALIDATION_STATUS.md.
