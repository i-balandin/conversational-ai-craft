# A house standard for prompts

*Ihor Balandin. A working baseline, not a mandate.*

This is the list I check a prompt against before I call it done. It was assembled from two unrelated products — a multi-turn conversational assistant built as a graph of stages, and a content-generation pipeline with LLM judges gating what ships in a regulated domain — and every rule here is one I have actually applied to one of them and can point at a case for.

**The reason it is in this repository is not the rules.** Most of them are individually unremarkable, and a competent engineer will already do half. What I think is worth copying is the shape: **a short list, kept per team rather than per person, where each line carries the case that put it there.** A rule with no case behind it is somebody's taste, and taste does not survive a disagreement with a colleague at 6pm.

One meta-rule sits above the others: **you cannot call a prompt change "better" without a way to measure it.** Everything below makes prompts more *reliable*. Only evaluation tells you whether a content change helped.

---

## A. Structure and attention

- **End on what matters, not on cosmetics.** A model weighs the start and the end of a prompt most heavily. Don't spend the last lines on formatting minutiae — end on the one or two quality bars that actually decide whether the output is acceptable.
  *Case: a generator whose final instruction block was dominated by rules for a short breadcrumb label, which both of its own checkers treated as advisory and non-rejecting. Prime real estate, spent on the one thing that could not fail the output.*

- **Reinforce the fragile requirement near the generation point.** When you restate rules just before "now produce it", restate the quality most likely to be dropped — not the ones that are easiest to check.
  *Case: the same generator restated format and relevance immediately before generating, and omitted the depth requirement entirely. The requirement most at risk was the one not reinforced where it mattered.*

- **Show, don't only tell.** For any prompt that must emit a structured artefact, include at least one worked exemplar of the finished output, not only prose describing good qualities. A prose rubric guides; a gold exemplar anchors.
  *Case: a prompt shipped three GOOD/BAD pairs, every one a description of a quality. The model was asked for a complete JSON artefact and was never shown a single finished one.*

- **Spend the instruction budget deliberately.** Too many simultaneous MUSTs make a model satisfice: it nails the salient, checkable ones and quietly under-delivers on the soft one. Consolidate, and state priority explicitly for requirements that can conflict.
  *Case: six competing MUST-blocks in one generator, each with its own examples. The one that got dropped was the one the whole section had been added to fix.* See note #2 for the version of this argument that has numbers behind it.

## B. Judges and evaluation

- **Reason before verdict.** Put the `reasoning` field first and the score last, so the verdict is conditioned on the analysis instead of rationalising a decision already made.

- **Temperature 0 for evaluators — and know what that buys you.** A judge that samples is a non-deterministic gate: the same input can pass one run and fail the next. But greedy decoding does not give you determinism at the provider level, and it *hides* judge variance rather than removing it. So: score the shipped run at temperature 0, and once per rubric version run an n-repeat probe and report the judge's self-consistency next to its agreement with a human.

- **Define every level you gate on.** If the threshold sits at 3 out of 5, define what a 3 is. Don't leave the boundary you actually depend on to the model.
  *Case: a rubric that anchored 4–5 and 1–2 with descriptions and left 3 — the gate boundary — undefined.*

- **Aim the generator at what the judge measures.** Generator and evaluator should share one definition of the quality, or the generator produces things the judge rejects and you pay for the retries.

- **Fail closed on the verdict.** An unparseable or missing judge verdict must count as reject, never auto-approve.
  *Case: a quality gate that read only a boolean `approved` flag and treated a malformed response as approval — degrade-open, in a regulated domain.*

- **Test the judge before you trust it.** A curated gold set with expected verdicts, plus a run-to-run consistency check, before it gates anything. And measure agreement between two humans before you measure the judge against one: if two people agree 60% of the time, "the judge agrees with a human 70% of the time" is not interpretable.

## C. Output contracts

- **Constrain the output natively.** Prefer the provider's structured-output facility over repairing model JSON with regular expressions. It removes a whole class of failure.
  *Case: a pipeline hand-repairing JSON with regex while the provider's schema enforcement sat unused.*

- **Validate, then reject — don't repair.** Check required fields, ranges and types on the way out, and reject a malformed response rather than patching it into shape.

- **One authoritative schema.** When a schema controls the output, don't also maintain a divergent example of the same thing. They drift, and the example usually wins.

## D. User input and injection

- **Isolate user input in delimiters**, and tell the model the delimited text is content to analyse, not instructions to follow.

- **Sanitise the delimiter itself.** Strip the closing delimiter string from the user's text before wrapping it, or the user can simply close it and walk out.

- **System prompts are server-side only.** The client sends the user's text, or a key naming a prompt — never the prompt.

- **Size the defence to the blast radius.** Absolute constraints plus an explicit "injection detected" path where the risk justifies it; not a parallel detector where it doesn't.

- **A delimiter is hygiene, not a security control.** It is widely treated as one. It isn't, and a prompt that consumes untrusted text in a system that can act on the result needs a layer outside the model.

- **Transit-only for sensitive input.** Don't persist prompt text or responses that may carry client data. Log metadata, never content.

## E. Content quality

- **Turn soft asks into enforceable rules.** "Be realistic" is unfollowable. "Name the actual tool and the actual artefact; the words 'a customer' and 'some data' are banned" is followable and checkable.

- **Ground in one concrete case, not a catalogue.** A single (role → tool → artefact → deliverable) case beats a menu of options, which invites blended, generic output.

- **Use contrastive examples.** A GOOD/BAD pair per quality communicates a bar faster than any amount of description.

- **Specify voice and structure for anything user-facing.** A tone plus a repeatable beat structure, with one concrete example.
  *Case: a feedback voice specified as acknowledge → why it matters in this specific situation → link to the reader's own work.*

- **Match the language of the input** wherever the surface is user-facing — and know whether the language of the first message is even yours to control. On one platform it is a runtime parameter set by the interface locale, and no wording in the prompt reaches it.

- **Watch what a stated bound does to the distribution.** "Under 100 words" makes 95 words the target; "one or two questions" makes two the floor. State the band you actually want, not the ceiling you will tolerate.

## F. Engineering hygiene

- **Thresholds live in code, not in prompt text.** Don't hardcode a tunable constant into a prompt: it duplicates the value and drifts the first time the code changes.

- **Naturalness belongs where it is read.** Warm, human phrasing is for user-facing prompts. Internal judges want precision and determinism, not warmth.

- **Version prompts against a base.** When handing a prompt change to engineering, stamp the base commit and prefer a minimal diff to a wholesale file replacement.

- **Evaluate against the render, not the file.** See note #4. This is the one on the list that has cost the most.

- **Measure before you claim.** "Looks better" is not a result. Record what changed, why, and the measured effect — or say plainly that you didn't measure it.

---

## The quick reject list

Faster than the whole standard, for a first pass over someone else's prompt:

- A judge that emits its score before its reasoning.
- An evaluator running at sampling temperature, or at temperature 0 with no variance probe ever run.
- A gate threshold that sits on a rubric level the rubric never defines.
- A prompt that ends on a cosmetic detail.
- Rubric prose with no worked exemplar of the actual output.
- A pass threshold hardcoded into a prompt string.
- User input concatenated into a prompt with no delimiter isolation, or with a delimiter the user can close.
- Regex-repairing model JSON while native structured output sits available.
- A malformed judge verdict that counts as approval.
- A content change shipped with no way to tell whether it helped.

---

## How to use this

For a new prompt: skim A–F and apply what fits the surface — a user-facing prompt, an internal judge and a generator want different things from this list. For reviewing someone else's prompt: the reject list is a fast first pass.

**And for the version of this that belongs to your team rather than mine:** start it empty. Add a line the first time something bites, with the case attached. A list assembled that way is short, defensible and gets followed. A list copied from someone else's repository is neither.
