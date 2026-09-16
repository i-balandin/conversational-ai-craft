# Conversational AI Craft

Notes by Ihor Balandin on two problems that show up once a conversational
assistant leaves the demo: it gets harder to steer the more you tailor it, and
the evaluation meant to catch that measures something else than everyone thinks.

Each note comes with a small example you can run. Everything is synthetic —
made-up transcripts, made-up policies, no client material anywhere.

## The notes

**1. [Your AI pilot passed. That doesn't mean it works.](posts/01-silent-false-pass.md)**

Checks written for a stage of a conversation quietly assume the conversation got
there. When it didn't, a check looking for a bad ending finds no ending, and
passes. The test set then scores well partly because conversations went nowhere.
Letting a check answer "not applicable", and reporting how far conversations
actually got, takes that away.

```
python examples/false_pass/run_demo.py
```

**2. [More rules, less control: building assistants that stay specific.](posts/02-more-rules-less-control.md)**

Twenty nuances in a client's method become twenty rules, then forty, and the
assistant ends up less predictable than the plain prompt was. That instruction
following degrades as constraints pile up is measured elsewhere; this note is
about the design conclusion — put the specificity in the structure of the
conversation, and keep a small floor of always-on rules separate from it.

There's an experiment for testing the claim on your own assistant. It's the one
thing here that needs a model, and I haven't run it at a scale worth publishing,
which is why the note has no numbers in it.

```
export ANTHROPIC_API_KEY=...
python experiments/instruction_load/run.py
```

**3. [Your guardrail passed the test. The user didn't follow the test.](posts/03-guardrails-off-the-planned-path.md)**

A rule about distress that lives in the "explore" stage does not exist in the
other three. So the person who says it in their first message, or while the
assistant is wrapping up, gets the script instead. The example runs the same
assistant in two configurations: on the scripted path both look safe, off it the
scoped rule misses three conversations out of four and the floor rule misses
none.

```
python examples/guardrail_branches/run_demo.py
```

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

[framework-map.md](framework-map.md) puts these into one picture: six
contributions, what each transfers to, what it's worth to a team adopting AI,
and how good the evidence for it currently is. Working name, Controlled
Specificity. It's a framework from practice on its way to a tested method, not a
finished standard.

## What the examples are and aren't

`guardrail_branches` and `silent_retrieval` are deterministic models of the
behaviour, not LLM runs — they demonstrate the test design, so they print the
same thing every time. `false_pass` scores real (synthetic) transcripts with two
evaluators and lets you watch the same conversation flip from a perfect score to
a fail.

Where a claim is mine, the note says so, and where the underlying effect is
already established in published work, it says that too. If you've seen any of
it written up elsewhere, tell me — I'd rather read it than re-derive it.

## License

MIT — see [LICENSE](LICENSE).
