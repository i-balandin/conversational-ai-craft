# Conversational AI Craft

Notes by Ihor Balandin on conversational AI once it is past the demo: an
assistant built around one organisation's own method, which then has to keep
behaving predictably while real people use it and ask things no test script
contained.

The thread running through most of these notes is that the evaluation around
such a system fails quietly. An evaluation that passes because the conversation
never got far enough to fail. A safeguard that exists in only one stage out of
four. A retrieval that returned nothing while the answer implies otherwise. An
instruction that was never in the rendered prompt at all. None of these raise an
error or look like a failure, which is why a test suite catches them only if it
was written with that specific shape of defect in mind. Each note describes one
of those shapes, how to test for it, and what the test costs.

Every note ships with a script that reproduces what it describes: plain Python,
no dependencies, no API key — the one exception is the experiment in note #2,
which needs a model. Everything is synthetic: made-up transcripts, made-up
policies, no client material anywhere.

## The notes

**1. [Your AI pilot passed. That doesn't mean it works.](posts/01-silent-false-pass.md)**

Checks written for a stage of a conversation quietly assume the conversation got
there. When it didn't, a check looking for a bad ending finds no ending, and
passes. This has an older name — vacuity, in formal verification, where they
have been measuring it since the 1990s and where a vacuous pass is known never
to be benign. The note is about the transfer: letting a check answer "not
applicable", and reporting how far conversations actually got.

```
python examples/false_pass/run_demo.py
```

**2. [More rules, less control: building assistants that stay specific.](posts/02-more-rules-less-control.md)**

Twenty nuances in a client's method become twenty rules, then forty, and the
assistant ends up less predictable than the plain prompt was. That instruction
following degrades as constraints pile up is measured elsewhere; this note is
about the design conclusion — put the specificity in the structure of the
conversation, and keep a small floor of always-on rules separate from it.

The claim comes with an experiment that tests it on your own assistant — the one
thing here that needs a model. It hasn't yet been run at a scale worth
publishing, so the note states the argument and leaves the result slot open
rather than filling it with numbers that wouldn't carry.

```
export ANTHROPIC_API_KEY=...
python experiments/instruction_load/run.py
```

**3. [Your guardrail passed the test. The user didn't follow the test.](posts/03-guardrails-off-the-planned-path.md)**

A rule about distress that lives in the "explore" stage does not exist in the
other three. So the person who says it in their first message, or while the
assistant is wrapping up, gets the script instead. The note also covers what
this is adjacent to and is not — an instruction hierarchy ranks instructions by
whose they are, this ranks them by where they exist — and the second substrate
the same argument now applies to, which is memory.

```
python examples/guardrail_branches/run_demo.py
```

**4. [The prompt you read is not the prompt that ran.](posts/04-the-prompt-you-read-is-not-the-prompt-that-ran.md)**

Your prompt text is usually data, not code: a row in a database, versioned on
its own schedule and put live by an action that leaves no commit. The code that
builds the variables moves separately. When they disagree the renderer says
nothing in either direction — it discards a value the template doesn't name,
and it fills a name nothing supplied with an empty string — so a whole section
of the instructions can be absent for months while the assistant answers
fluently and an answer-quality rubric keeps passing it. The remedy is a
three-line report. The habit it replaces — rewriting an instruction that was
never in the prompt — is the expensive part.

```
python examples/render_drift/run_demo.py
```

## The same argument in a real harness

An argument that only holds inside my own evaluator isn't worth much. So note
#1's remedy is also implemented in [promptfoo](https://promptfoo.dev), which is
binary by design and therefore has nowhere to put "not applicable".

```
cd evals/promptfoo && npm install && npm run eval && npm run report
```

promptfoo reports 67% pass. Over the results that actually applied it is 50%,
and one criterion sits at 0% on the single conversation where it was testable —
invisible in the headline, because its other two results had nothing to judge
and were counted as passes. No API key: the provider replays stored transcripts,
so the evaluator is the only variable. It runs in CI on every push.

See [evals/promptfoo/README.md](evals/promptfoo/README.md).

## One more example, no note yet

An assistant retrieves nothing from the knowledge base and answers anyway, out
of general knowledge, saying it consulted company policy. A typical
answer-quality check likes that answer — it's specific and confident — and
dislikes the one honest reply that admits it found nothing. A grounding check
gets both right.

```
python examples/silent_retrieval/run_demo.py
```

## The framework behind them

[framework-map.md](framework-map.md) puts these into one picture: thirteen
items across control, encoding, verification and warrant, each with what it
transfers to, what it's worth to a team adopting AI, and how good the evidence
for it currently is, stated plainly and at a named rung.
Working name, Controlled Specificity. It's a framework from practice on its way
to a tested method, not a finished standard.

## What the examples are and aren't

Two different kinds of thing live in `examples/`, and the difference matters.

**Proofs of design.** `guardrail_branches`, `silent_retrieval` and
`render_drift` are deterministic models. The assistant is a hundred lines of
Python that does exactly what its configuration says, the conversations are ones
I wrote, and running them produces the same output every time. They demonstrate
a test design and execute an argument you can step through. They are not
measurements, and where one of them prints something like "three out of four",
that is a property of a fixture I built — not a rate anyone observed.

**Proofs of effect.** `false_pass` and the promptfoo suite score transcripts
with two different evaluators and let you watch the same conversation flip from
a perfect score to a fail. The transcripts are still synthetic, but the result
is computed rather than asserted, and it could have come out otherwise.

Where a claim is mine, the note says so, and where the underlying effect is
already established in published work, it says that too — in note #1 the
established work turned out to be both older and better measured than mine. If
you've seen any of the rest written up elsewhere, tell me — I'd rather read it
than re-derive it.

## Who wrote this

Ihor Balandin — AI engineer working on the reliability and quality layer of
production LLM systems: evaluation harnesses, golden datasets, LLM-as-judge and
regression runs, safety guardrails, and the prompt and persona architecture
underneath them. Mostly on conversational products, where quality is easy to
assert and hard to measure. A research background is where the habit of
measuring rather than going by feel came from.

Open to roles and contract work where getting the quality bar right is the
point. Corrections, disagreements and "this already exists, here it is" are all
welcome: [open an issue](https://github.com/i-balandin/conversational-ai-craft/issues)
or reach me on [LinkedIn](https://www.linkedin.com/in/ihor-balandin-2510412b/).

## License

MIT — see [LICENSE](LICENSE).
