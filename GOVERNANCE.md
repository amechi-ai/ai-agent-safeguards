# Project governance

Status: experimental community initiative. The founder and project owner, @amechi-ai, retains final responsibility for scope, maintainers, official publications, licensing and acceptance of residual risk. This document defines a proposed operating process; GitHub rules must be separately enabled and verified.

## Roles
- Project owner: appoints maintainers, approves material changes and releases, resolves conflicts.
- Maintainers: triage, review and manage approved changes within delegated scope.
- Contributors: propose changes and provide evidence; no implied administrative authority.
- Independent reviewers: assess changes and evidence independently of their authors; disclose conflicts and whether review is human or AI-assisted. AI review alone is not equivalent to independent human expert assurance.

## Change control
Use issues or Discussions for proposals and pull requests for changes to main. Include affected clauses, assumptions, threat model, legitimate-work impact, tests, residual risks and evidence status. Editorial changes need proportionate review; substantive security or behaviour changes require independent review and explicit owner approval before merging. Do not allow agents to approve or merge their own work. Record any emergency exception, owner approval, scope and retrospective review.

Keep main protected against direct changes, force-push and deletion once rules are enabled. Require passing applicable CI checks; a green reference-model suite is not operational assurance. Until a second reviewer is appointed, do not require a platform approval that locks out the sole owner; substantive changes still wait for independent review.

## Releases
Preserve immutable version references and evidence, describe changes and limitations, and distinguish proposals, local tests, independent review and operational tests. No production or immunity claims without supporting evidence. Credit contributors with consent; material AI assistance should be disclosed. Only the owner may authorise licensing changes or official release. Public participation does not grant permission to use third-party materials.
