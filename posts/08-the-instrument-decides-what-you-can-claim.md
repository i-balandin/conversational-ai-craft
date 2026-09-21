# The instrument decides what you can claim

*Conversational Eval Notes #8. Ihor Balandin.*

Sooner or later someone hands you a quality framework — a professional body's standards, a published design framework for your domain, an internal ethics policy — and asks two things. Make the assistant conform to it. And show that it does.

The second request is the hard one, and it is usually answered with a number. We conform on 87% of the principles. That number is almost always wrong, and it is wrong in a specific, repeatable way that has nothing to do with how carefully the criteria were written.

## The known part

Mapping a policy to controls and evidence is what compliance teams have done for decades, and the limits of doing it by keyword are documented in that literature. Rubric design and LLM-as-judge are well covered. Reporting per control rather than as an aggregate is standard advice in automated compliance checking.

None of that is mine. What I want to add is what happens when the thing being assessed is a conversation, and the instrument is a judge reading a transcript.

## An eval criterion is a judgement about a transcript

That sentence is the whole mechanism, and it constrains everything downstream.

Most quality frameworks worth adopting were written before LLM products, for human practitioners or for software in general. So a single numbered list will happily contain, side by side:

- things a conversation shows — how the assistant handles a boundary, whether it discloses what it is, whether it escalates a safety concern, whether it pressures anyone;
- things only a process shows — data retention, encryption, audit modes, release discipline, how openly the system is documented.

A transcript judge is blind to the second kind by construction, not by weakness. No amount of rubric craft changes that, because the evidence isn't in the artefact being judged.

So the first move, before translating a single principle into a criterion, is to **sort the list by the instrument that can see each item.** In one engagement where I did this against a published framework, roughly a third of the principles left no trace in a transcript at all, and several more left only a partial one. Which means the eval set could not substantiate conformance to that framework — and saying that it did would have been an overclaim that anyone who knew the framework would take apart in five minutes.

That is not an argument for a smaller ambition. It is an argument for three instruments instead of one.

## Three instruments, and what each may claim

**Session conformance.** A judge over a transcript. It can speak to behaviour that happens in the conversation, and to nothing else. This is the part most teams already have, and the part they over-extend.

**Outcome.** A measure of whether the thing worked, taken at the start and end of a programme rather than per session. Its value is that it produces a number comparable with a human baseline, which no transcript criterion can.

**System attestation.** A per-release checklist with evidence behind each line: retention, audit mode, escalation protocol, model-update discipline, criterion versioning. Not evals, and it must not pretend to be. Each line carries an assurance level — self-declared, evidence-backed, or independently reviewed — because those are three different strengths of claim and collapsing them is how an attestation becomes decoration.

Then two tags on every criterion, kept in the criterion set itself: **which instrument** it belongs to, and **whether a transcript can see it at all.** A principle with no transcript trace never enters the eval set. It goes to attestation.

## The worst case is the criterion that looks like coverage

If a principle has no trace in a transcript and somebody writes a session criterion for it anyway — "respects data minimisation", judged by a model reading a support conversation — you are worse off than with no criterion at all.

It counts as coverage in every tally. It passes, because there is nothing there to fail. And it converts an honest gap into a claim. This is the same failure as note #1's vacuous pass, and as the framework map's point that a grep for a framework's name cannot tell a framework that is built from one that is mentioned, arriving through a third door: a measure with nothing to measure returns a pass, and a pass gets read as evidence.

## Predictability, and what replaces it

Here is the part I think matters most, and it is a genuine open problem rather than a fix.

Frameworks written before generative models routinely list **predictability** among the conditions on which a user's trust is supposed to rest. It belongs there. And a generative assistant cannot deliver it in the form those frameworks assume, because variability is how the technology works. The tension is usually left unresolved: the requirement stays in the list, the technology cannot meet it literally, and everyone proceeds.

What can be promised instead is **bounded conformance** — not that the assistant says the same thing, but that its behaviour stays inside declared bounds, and that those bounds were measured rather than asserted. Operationally, three things:

- **Bands, not points.** A criterion declares a range of acceptable behaviour with countable anchors, not a model answer to match.
- **Spread as part of the result.** The same transcripts, re-run, give a range. Publish the range beside the score. **A score without its spread is not a measurement**, and a single number invites exactly the comparison it cannot support.
- **Invariants with no spread at all.** Disclosure of what the assistant is, the crisis protocol, the limits of competence. These are not bands; they are a floor, and one violation is a failure rather than a dip in an average.

That third item is note #3's shared floor, arriving from the governance side of the same argument. It is the same set of rules, identified by a different route, which is the strongest evidence I have that the distinction is real.

## Two preconditions nobody sequences

Both of these cost nothing to check and are routinely skipped, and each one invalidates everything after it.

**Do not calibrate an instrument on a broken substrate.** In one case I was preparing to calibrate a judge when it turned out that most sessions were not progressing past their opening stage — a platform defect, nothing to do with the coaching or the criteria. Calibrating then would have produced a beautifully stable measurement of a navigation bug. Before you calibrate a measure of how well something is done, check that the thing is being done at all.

**A threshold means nothing without a human baseline.** "Seven out of ten to ship" is an arbitrary number until you know what a competent human session scores on the same instrument. Getting that requires a transcript set labelled by a qualified practitioner — expert hours, not engineering hours — which is precisely why it is the item that never gets funded and the reason so many acceptance bars are, in the end, a feeling with a decimal point.

And one that follows from both: agreement between two human raters comes before agreement between the judge and one human. If two experts agree 60% of the time, "the judge agrees with an expert 70% of the time" is not interpretable.

## See it happen

The repository has a small example: an invented framework for a support assistant, a set of session criteria, an attestation list, and three ways of counting the same facts. Its shape was chosen to exercise every case once rather than to resemble anything real.

A keyword harness reports one number. Counting principles that have a criterion mapped to them reports a much higher one. What the eval set can actually substantiate sits below that — and two principles come back flagged for different reasons: one because a session criterion was written for something no transcript can show, the other because a transcript *could* show it and nothing checks it.

```
python examples/conformance_claim/run_demo.py
```

Read it as a diagram: the framework is mine, invented for the file, and the arithmetic is the argument. Bring your own list of principles and your own criteria, and the sorting is the same half-hour's work.

## What I'm claiming, and what I'm not

I'm not claiming that policy-to-control mapping is new, that keyword coverage is unreliable, or that assurance levels are my idea — those come from the assurance-case tradition and I'm borrowing them.

What I'd put forward is the sorting step and what it implies. That an eval criterion's reach is bounded by what a transcript contains; that sorting a framework by observability *before* translating it usually shows the eval set can substantiate markedly less of it than a tally of criteria implies; that the criterion written for an unobservable principle is worse than no criterion; and that predictability, in the form pre-generative frameworks require it, has to be replaced by bounded conformance with published spread rather than quietly dropped.

**On evidence.** This comes from one engagement, working against one published framework in one domain, plus the measurement practice in the rest of these notes. The sorting exercise I did once; the three-instrument split I proposed and have not yet seen adopted; the predictability replacement is a proposal, not a result. No counts beyond "roughly a third", which is as precise as I am willing to be about a single case.

If the sorting-by-observability step is written up somewhere — it feels like the kind of thing a standards body would have formalised — I would genuinely rather read it than keep re-deriving it.

## How this connects to the other notes

Note #1 is a criterion that passes because the conversation never reached the stage. Note #4 is a criterion scoring a prompt that never rendered. Note #5 is a criterion that is not independent of what it measures. This one is a criterion asked about something that was never in the artefact at all — the same species again, and the reason all four are worth separate notes is that each one is invisible to the others' fixes.
