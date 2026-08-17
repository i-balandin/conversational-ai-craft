# Your eval says 10/10. The conversation still failed.

*Field notes on evaluating conversational AI — #1: false-passes in multi-turn evaluation.*
*Draft by Ihor Balandin. Rough — will be edited.*

## The gap that started this

You run your eval suite over a conversational assistant. Every check is green, the average lands around 9.6/10, and you move on. Then you actually read one of the transcripts. The assistant wrapped up after two exchanges, never checked what the person came for, and slid past a moment where the user said they weren't really okay. The numbers said pass. A human reading it says no, obviously not.

I ran into this often enough — building and testing multi-turn assistants — that I stopped treating it as a one-off bad transcript and started treating it as a class of failure with a name: a **false-pass**. The evaluation reports success while the conversation fails. Worse, it fails quietly: a false-pass doesn't spike an error, it averages into a clean-looking score.

This note is about the two mechanisms behind it, what actually catches them, and a minimal example you can run to see it happen.

## Two mechanisms

Almost every false-pass I've looked at traces back to one of two things.

**1. Per-turn scoring misses conversation-level failure.**
The common setup grades each message on its own: is this reply helpful, on-tone, safe? Every individual message can pass that bar while the *arc* is broken. The assistant closed before the goal was ever set. It ignored what the user asked for three turns ago. The tone drifted. A distress signal went unhandled. None of those live inside a single turn — they live in the relationships *between* turns, which per-turn scoring never looks at.

**2. Phase-gated boolean criteria mis-score on truncated or branching threads.**
Teams often write criteria as booleans tied to a phase of the conversation: "did it confirm the goal before closing?", "did it summarize at the end?". These quietly assume a full, linear arc. Real test threads don't cooperate — they end early, branch, or never reach the phase the check is about. When that happens the boolean fires the wrong way. It returns FAIL for a step that legitimately didn't apply, or — the dangerous one — returns PASS because the disqualifying phase simply never occurred. Either way the metric is now lying, and it looks exactly like signal.

The second mechanism is the one that cost me the most, because a spurious PASS is invisible. A spurious FAIL at least makes someone look.

## Why it happens

Most eval harnesses are inherited from single-turn or RAG grading, where the shape is one prompt → one answer → one score. That shape works there. A conversation isn't that shape, but the tooling and the mental model come along anyway. Boolean phase criteria are the linear-arc assumption made concrete. And an LLM-as-judge dropped in without calibration will happily produce confident numbers that no human ever checked against a real transcript. On top of all that, a wall of green checks is socially comfortable — nobody interrogates a 9.6.

## What actually catches it

Four practices. None of them is clever on its own; the discipline is using them together.

**Score the conversation, not only the turns.** Add assertions that run over the whole transcript: was a goal set and then referenced before closing; did a close happen before any goal existed (premature close); was a distress or edge signal acknowledged and routed. These are arc-level, not message-level.

**Make phase criteria conditional, not boolean.** A phase criterion should have three outcomes, not two: pass, fail, or **N/A when the phase wasn't reached** — and N/A is excluded from the score, not counted as a fail and not counted as a pass. This single change removes most of the phantom fails *and* phantom passes, because the check stops answering a question the conversation never asked.

**Calibrate the judge against human labels — and report the agreement.** An LLM-as-judge is worth exactly what it agrees with a human on. Take a small set of transcripts, label them yourself, run the judge over the same set, and report judge-vs-human agreement as a number that sits *next to* your eval results. If the judge and a human disagree half the time, the score is decoration and everyone should know that.

**Don't test the fix with the suite that missed the bug.** If the same suite that scored the broken conversation 9.6 is what you use to confirm your fix, you've proven nothing. The failing transcript goes in as a regression case first, then you fix.

## A reproducible example

The repo that hosts this note has a minimal harness: three synthetic, coaching-style transcripts — one that looks fine but is broken, one that's truncated mid-conversation, one that's clean — plus a naive boolean eval that produces the false-pass and a phase-aware/conditional eval that catches it. It runs with no API key and no dependencies.

Run it and watch the same broken conversation flip from a high naive score to a fail once the criteria stop assuming a linear arc — and watch the truncated one stop being penalized for a phase it never reached.

## What generalizes, and what doesn't

I want to be careful here, because some of how I arrived at this came from working on one particular platform, and one product's quirks are not a general law. So the bar I hold myself to is simple: **does the effect reproduce in a plain, minimal setup that has nothing to do with that platform?**

The two mechanisms above do. You can see both in the ~100-line example, with no special infrastructure — which is why I'm comfortable calling them a general class rather than one system's bug. Anything that only appeared because of a specific engine's internals I've deliberately left out; that's an implementation detail, not a finding. Where I make a claim in this note, the synthetic reproduction is the evidence — not my having seen it once.

## Next in the series

Two threads I want to pick up next: guardrail behaviour across conversation branches (a guardrail that holds on the happy path and leaks the moment the dialogue forks), and a more formal way to calibrate and report judge-vs-human agreement. This is note #1 of a running set.
