# Confirmation of the v0.4 revised reference model

19 Nov 2026 · Reviewer: Claude

Independent verification of the revised `safeguard_prototype.py` supplied on 19 November, against the seven-row evidence table in v0.4 §"Offline reference-model evidence". Executed in an isolated sandbox: in-process only, no network, no external effects. The hash was verified, the suite run, the five earlier probes re-run, and five new probes written.

## Verdict

**Confirmed. All seven rows of the v0.4 evidence table are accurate.** The file hashes to `7bfc00891de17100fa441ba3c35c8ef3731d6e8baf76a21cb259a5024f8f0adf`, exactly as the document states. The suite runs 9 tests and all pass. Each of the five probes that broke the previous harness now fails to break this one, and the H1 bypass — the decisive finding from the last round — is closed at the mechanism level rather than patched at the surface.

The fix is the right one. `perform()` now resolves every operation, including `read` and `write`, against an explicit `(actor, operation, resource)` grant before touching storage, and raises when there is no match. There is no implicitly-permitted operation left in the model. That is the general form of the bug, not just the instance I found.

v0.4's §"Offline reference-model evidence" may now drop "Independent confirmation of the revised model is pending" and record that confirmation was obtained, with the hash and date. The J6 recommendation from the v0.4 re-review — retitling that table to flag it as author-reported — is no longer needed and should be dropped rather than applied.

**Four new observations from fresh probing**, none of which reverses the above. Three concern the gap between what the fixture enforces and what the specification requires: the model's participant cap of 3 and per-actor budget of 4 are hardcoded constants with no counterpart in S11 or S12, so a passing T35 evidences the fixture's bound rather than the specification's. One is a small genuine defect: containment blocks a contained actor as a sender but not as a recipient.

**What this does not change.** The host and the tests still share a process and an author. Confirming that the model behaves as described raises this evidence from "asserted" to "verified", which is a real step, but it remains evidence about a specification model — not about enforcement against untrusted code, which is what a prototype has to establish. v0.4 says this plainly in its Evidence and assurance table and in the closing paragraph of the evidence section, and both remain correct.

## Verification record

### Integrity and suite

| Check                    | Result                                                                                                                                                                                  |
| ------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SHA-256 of supplied file | `7bfc0089…4f8f0adf` — **matches the document exactly**, as-is, 12,238 bytes. Variants (stripped trailing newline, CRLF) do not match, so the declared value is of the file as delivered |
| Suite execution          | `python3 -I safeguard_prototype.py -v` → **Ran 9 tests, OK**, 0.005s. Nine test methods, matching the document's count                                                                  |
| Isolation                | Imports only `concurrent.futures`, `dataclasses`, `threading`, `unittest`. No sockets, no subprocesses, no writes outside the scratch copy                                              |

### The seven claimed rows, re-probed

Each row was tested with a probe written against the fixture, not by reading the author's tests.

| Row     | Claim                                                                                                     | Probe result                                                                                                                                                                                                                                                                                                                                                                                 |
| ------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| H1 / G1 | Ungranted observer cannot read or overwrite the draft; approved handoff still works                       | **Confirmed.** `builder` wrote a message-board-style marker; `observer` read raised a permission error, and so did `observer` write. `reviewer`, who holds a read grant, retrieved it normally. The previous harness allowed the full exchange                                                                                                                                               |
| H2 / G5 | Method delivery requires a declaration granting sender, receiver and named target                         | **Confirmed.** `exchange_method` on an undeclared group raises. The old fixture delivered the payload with no group in existence at all                                                                                                                                                                                                                                                      |
| H3 / F1 | Two groups coexist with separate same-named drafts; cross-group access refused                            | **Confirmed.** The two groups held different content under the same resource name simultaneously, and a cross-group read raised. Storage is keyed by group and resource together. The old single member set made this property inexpressible                                                                                                                                                 |
| H4      | Structured objective checked against explicit grants; semantic breadth not assessed                       | **Confirmed, including the limitation.** A verb outside read/write, an empty resource, and an objective matching no grant are each refused. A generic-sounding resource name with a matching grant is accepted — correctly, since the check is structural. The concession in the document is accurate                                                                                        |
| H5      | Authorised read of a missing draft returns empty; unauthorised read raises                                | **Confirmed.** Returns None versus a permission error. The old fixture returned falsy for both, so a test could pass for the wrong reason                                                                                                                                                                                                                                                    |
| G3      | Launch cannot set a 150-unit budget; the policy path can; aggregate cap binds                             | **Confirmed.** The launch-supplied budget is refused; the policy path then permits 50 × 3 = 150 with the 151st unit refused. The 100-unit default also binds under 8-way concurrency: 33 successes, 99 units, then exactly one more single unit to reach 100                                                                                                                                 |
| G2      | Deadline contains the affected actor; unrelated task continues; a fresh declaration cannot restore access | **Confirmed.** Containment fires at minute 5 and not minute 4; the reviewer continues reading and writing; the advisory signal is correctly ignored; and group declaration raises when the member set intersects the contained set. That last part is the re-declaration bypass flagged as a *consequence* of making groups mutable — anticipated and closed before I raised it as a finding |

No row was overstated and none required qualification.

## New findings

Five fresh probes, four findings. None reverses the confirmation.

### K1 (Medium, specification) — the fixture's bounds are constants the specification does not require

The model refuses a participant cap above 3 and a per-actor budget above 4. Both are hardcoded. Probing `cap=3`, `cap=4` and `cap=50` gives accepted, refused, refused — so the model's rejection of an oversized group comes from the literal `cap <= 3`, not from anything S11 says.

S11 ¶2 requires "a justified and enforced participant cap" and states no bound, no maximum, and no criteria for what justifies one. S12 ¶1 likewise requires per-task limits without bounding them. **A conforming implementation could declare a cap of 500 with a one-line justification and satisfy S11 as written**, while the model that evidences T35 would refuse it at 4.

This is the residue of G1. The enumeration-and-deny rule closed the operation surface; the participant surface is bounded in the fixture and unbounded in the specification.

*Smallest correction:* S11 ¶2 — require the declaration to record the cap **and the justification for that specific number**, and require host policy to set a default maximum above which a declaration needs owner-level approval. *Usability:* low; it adds one policy constant and one approval for unusually large groups.

### K2 (Low, model) — containment stops a contained actor sending, not receiving

`perform()` and `exchange_method()` both check `actor in self._contained` for the *sender* only. With `reviewer` contained and `builder` holding a message grant to it, the message was delivered and retrievable.

For the fixture this is cosmetic. For the specification it is a real question S9 ¶4 does not answer: "pre-authorised containment of affected actors" does not say whether containment is outbound, inbound, or both. In the motivating incident, inbound mattered — a contained agent that can still receive assignments is still a participant.

*Smallest correction:* S9 ¶4 — state that containment suspends the actor as both originator and recipient of task communication. *Usability:* none.

### K3 (Low, model) — `launch()` is advisory and enforces nothing

`launch()` returns `False` for any proposed budget, but `consume()` never consults it; after a refused launch the budget remains the default and consumption proceeds. The G3 row is still accurate — the launch-supplied value never reaches the budget — but the model demonstrates refusal of a parameter rather than enforcement of a launch gate.

*Smallest correction:* in the model, have a refused launch prevent consumption by those actors. No specification change; S12 ¶1 is already correct. *Usability:* none.

### K4 (Low, specification) — the per-task limit has no policy path in the model

`set_policy_budget()` moves the fleet budget only. After setting it to 10,000, a single actor consuming 5 units is still refused. S1 and S12 treat both per-task and fleet limits as policy-set, so the model implements half of that. Worth noting because the T36 pair is the evidence for the policy-versus-launch distinction, and the distinction is only demonstrated at fleet level.

*Smallest correction:* model-side only — add a policy path for the per-task cap. *Usability:* none.

### Confirmed residual, not a finding

Two actors who both legitimately hold read and write grants on the same resource can exchange arbitrary content through it. I ran this: a request and a reply passed between `builder` and `reviewer` in the message-board style of the incident, through a correctly declared namespace with no rule broken.

This is exactly what v0.4 discloses — "undeclared signals between actors already authorised to share content" — and it is the permanent limit of declaration-based control. Declaration bounds *who* may exchange and *through what*, never *what a permitted exchange may encode*. The v0.4 re-review's J3 asked for this to appear in S11 ¶3 rather than only in an evidence note; that recommendation stands and this run is the demonstration behind it.

## Effect on v0.4, and what remains

### Changes to make in the document

| Change                                                                                                                                                                     | Reason                                                                               |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| §Offline reference-model evidence ¶2 — replace "Independent confirmation of the revised model is pending" with confirmation obtained, naming the hash and 19 November 2026 | The confirmation now exists                                                          |
| Drop J6 from the v0.4 re-review's findings                                                                                                                                 | It asked for the evidence table to be labelled author-reported. No longer applicable |
| S11 ¶2 — record the justification for the specific cap number; host policy sets a default maximum above which a declaration needs owner-level approval                     | K1                                                                                   |
| S9 ¶4 — state that containment suspends the actor as both originator and recipient                                                                                         | K2                                                                                   |
| S11 ¶3 — add the content-signalling residual, per J3 from the previous round                                                                                               | Now demonstrated rather than argued                                                  |

J1, J2, J4 and J5 from the v0.4 re-review are unaffected and still stand. J2 in particular — the blank line splitting T35–T37 into a headerless second table — is still worth thirty seconds.

### Status of the evidence classes

| Class                                    | Status                                                                                                                 |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Static document checks                   | Done. Protocol hash and both coverage maps verified by computation                                                     |
| Reference-model tests                    | **Done and independently confirmed.** Hash verified, 9 tests run, 7 claimed behaviours re-probed, 5 new probes written |
| Implementation and architecture evidence | Outstanding. Nothing built                                                                                             |
| Executed synthetic scenarios             | Outstanding. T01–T37 all NOT RUN                                                                                       |
| Benign regression                        | Outstanding. T01 not measured                                                                                          |
| Independent implementation review        | Outstanding                                                                                                            |

### Before a controlled offline prototype

Nothing blocking. The design conditions were met at v0.4 and the model evidence is now confirmed rather than asserted. K1 is worth folding in first because it concerns a bound the prototype will need to pick a value for anyway.

The prototype's job is the thing neither the document nor the model can reach: whether these grants hold when the code being governed is not cooperating. Every result so far comes from a fixture that checks permissions it was written to check. The first prototype test that matters is an agent with a shell trying to reach another group's namespace by a route nobody enumerated.

### How this round may be cited

*On 19 November 2026 an independent reviewer verified the revised reference model's hash, executed its 9 tests, and independently re-probed all seven behaviours claimed in v0.4; all were confirmed. Four further observations were recorded, none reversing the confirmation.*

That is the whole of it. It establishes that an in-process model of the specification behaves as its author described. It establishes nothing about enforcement against untrusted code, deployment isolation, or production readiness — and the distance between those two sentences is the entire remaining programme.