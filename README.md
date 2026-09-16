# Conversational AI Craft

Notes and runnable examples on building conversational AI assistants that are
specific to one organisation and still controllable, predictable and provable.
By **Ihor Balandin**.

Two things break most often once an assistant leaves the demo. Its behaviour
gets harder to steer the more it is tailored, and the evaluation that was
supposed to catch that reports a number measuring something else. Each note here
takes one such failure, explains the mechanism, and comes with a small example
you can run in a few seconds.

## Notes

1. **[Your AI pilot passed. That doesn't mean it works.](posts/01-silent-false-pass.md)**
   Stage-based checks quietly pass conversations that never reached the stage
   being checked. The fix is a third answer — not applicable — plus reporting
   how many conversations got that far.
   → [`examples/false_pass`](examples/false_pass)

2. **[More rules, less control: building assistants that stay specific.](posts/02-more-rules-less-control.md)**
   Encoding a client's method as an ever-growing list of rules works against the
   model. Where specificity should live instead: in the structure of the
   conversation, with a small shared floor kept separate.
   → [`experiments/instruction_load`](experiments/instruction_load)

3. **[Your guardrail passed the test. The user didn't follow the test.](posts/03-guardrails-off-the-planned-path.md)**
   A safety rule scoped to one stage only exists in that stage. When a real user
   discloses something early, late, or off the planned path, it isn't there — and
   planned-path testing can't see it.
   → [`examples/guardrail_branches`](examples/guardrail_branches)

**[Framework map](framework-map.md)** — how these pieces fit into one working
framework, with six contributions, where each transfers, and what evidence
currently backs it.

## Run the examples

No dependencies and no API key, except where noted.

```bash
python examples/false_pass/run_demo.py           # note #1: silent false-pass, and the N/A fix
python examples/guardrail_branches/run_demo.py   # note #3: a guardrail leaking off the planned path
python examples/silent_retrieval/run_demo.py     # retrieval fails silently; quality checks still pass
```

`examples/false_pass` scores three synthetic transcripts two ways and shows the
same broken conversation flip from a perfect naive score to a fail.
`examples/guardrail_branches` and `examples/silent_retrieval` are deterministic
models of the behaviour, not LLM runs: they demonstrate the test design, so the
result is the same every time.

One experiment does need a model:

```bash
export ANTHROPIC_API_KEY=...
python experiments/instruction_load/run.py       # note #2: rule adherence as instruction count grows
```

I haven't run it at a scale worth publishing, so there are no numbers in note #2.

## Scope and honesty

Everything here is synthetic and generic on purpose. No client material, no
system I've worked on. Where a claim is mine, each note says so in a "What I'm
claiming, and what I'm not" section, and where the underlying effect is already
established in published work, it says that too. These are working notes moving
toward a tested method, not finished research.

## License

MIT — see [LICENSE](LICENSE).
