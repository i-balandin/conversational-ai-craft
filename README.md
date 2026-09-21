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

Every note ships with runnable code, though not all of it does the same job:
mostly a script that executes the argument so you can step through it, once a
suite that scores transcripts two ways, once a measuring tool that argues
nothing, and once an experiment that looked for the effect its note argues for
and did not find it. Plain Python, no dependencies, no API key — the exception
is that experiment, which needs a model. Everything is synthetic: made-up
transcripts, made-up policies, no client material anywhere.

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
thing here that needs a model. I ran it, and it found nothing: adherence held at
every load level, because two of my three criteria turned out to be incapable of
failing. The note reports that null and why it is my fault rather than the
argument's, which leaves the prescription resting on published benchmarks and
experience rather than on evidence of my own.

It runs end to end with no key and no network first, so you can see what it does
before deciding whether to point a real key at it:

```
CEN_DRY_RUN=1 python experiments/instruction_load/run.py
```

Any provider, and Gemini's free tier makes a full run cost nothing. What the
script sends, where, and why it never touches your key:
[experiments/instruction_load/README.md](experiments/instruction_load/README.md).

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

**5. [Your judge is reading the rules it marks against.](posts/05-the-judge-reads-the-policy.md)**

To grade a conversation, a model judge needs the assistant's policy — otherwise
it can't tell a violation from a design choice. That necessary decision makes
your prompt an input to your scores: an absolute in the policy bleeds into
criteria about something else entirely, exceptions are honoured only where a
criterion repeats them, and a criterion outlives the requirement it encoded, so
a corrected assistant scores *down* for obeying the client. Withholding the
policy stops the bleed and starts failing behaviour the policy permits, so it's
a diagnostic rather than a fix.

```
python examples/judge_contamination/run_demo.py
```

**6. [A preference can live in memory. A prohibition can't.](posts/06-a-prohibition-cannot-live-in-memory.md)**

Memory stores facts and preferences, and a boundary — "don't bring that up
again" — looks like the same kind of thing. It isn't. The extraction step is a
summariser, so it keeps the topic and drops the "don't", turning a rule into a
subject marked as significant. And retrieval fires on resemblance, so it catches
the turn that names the topic outright and misses the oblique approaches the
rule exists for. A preference that doesn't surface costs a little; a prohibition
that doesn't surface *is* the harm.

```
python examples/memory_prohibition/run_demo.py
```

**7. [The spec and the sign-off come from the same person.](posts/07-the-spec-and-the-signoff-come-from-the-same-person.md)**

When the assistant is built around one practitioner's method, the specification
comes from them and so does acceptance. Often their account is accurate — but
you can't tell from the description which case you're in, and if the spec
encoded the practice they intend rather than the one they run, sign-off compares
it against the same internal model and approves it. One held-out artefact of the
real practice breaks that circuit, and costs nothing when the account was right
all along.

```
python examples/style_markers/run_demo.py
```

**8. [The instrument decides what you can claim.](posts/08-the-instrument-decides-what-you-can-claim.md)**

Someone hands you a quality framework and asks you to show the assistant
conforms to it. An eval criterion is a judgement about a transcript, and most
such frameworks mix things a conversation shows with things only a process
shows — so sorting the list by observability before translating it usually
reveals the eval set substantiates considerably less than the tally suggests. Worse is the criterion
written anyway for an unobservable principle: it counts as coverage and proves
nothing. Plus what replaces predictability once the assistant is generative.

```
python examples/conformance_claim/run_demo.py
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

## Two practice pages

Neither of these makes a claim to be new. They are the working artefacts the
notes came out of, and they are here because the shape of them transfers even
where the content doesn't.

**[A house standard for prompts](prompt-house-standard.md)** — the list I check
a prompt against before calling it done, assembled from two unrelated products,
with the case that put each line there. The rules are mostly unremarkable; what
is worth copying is a short list, kept per team, where every line carries its
case.

**[Making prompt work auditable](making-prompt-work-auditable.md)** — prompt
work disappears when it succeeds, which leaves you making the one claim that
can't be checked. One table, four rules about how it's filled in, and why the
rows that say "not done" are the ones that make the rest credible.

## What the examples are and aren't

Three different kinds of thing live in `examples/`, and the difference matters.

**Proofs of design.** `guardrail_branches`, `silent_retrieval`, `render_drift`,
`judge_contamination`, `memory_prohibition` and `conformance_claim` are
deterministic models. Each is
a hundred-odd lines of Python doing exactly what its note describes — an
assistant that follows only the rules active in its stage, a renderer that
discards a value with nowhere to go, a summariser that keeps a topic and drops
the negation — run against conversations I wrote. They produce the same output
every time. They demonstrate a test design and execute an argument you can step
through. They are not measurements, and where one prints something like "three
out of four" or "one in four", that is a property of a fixture I built, not a
rate anyone observed.

**A tool, arguing nothing.** `style_markers` is a measuring stick, not a
demonstration: give it two transcripts and it prints the surface markers for
each and the gap. Note #7 says why shipping a demonstration there would have
proved only my own construction.

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
