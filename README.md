# Conversational Eval Notes

Field notes on evaluating conversational AI — short write-ups, each with a small,
runnable example. By **Ihor Balandin**.

Most LLM evaluation advice is written for the single-turn case (one prompt, one
answer, one score). Multi-turn assistants — coaches, agents, support bots — break
in ways that shape of evaluation never sees. This is a running set of notes on the
parts that actually bite, each backed by a minimal reproduction you can run.

## Notes

1. **[Your eval says 10/10. The conversation still failed.](posts/01-false-pass-in-multi-turn-eval.md)**
   — false-passes in multi-turn evaluation: why automated suites report success on
   conversations a human immediately sees as broken, and what catches it.
   *(Draft.)*

## Run the example for note #1

```bash
python run_demo.py
```

No dependencies, no API key. It scores three synthetic transcripts two ways —
a naive per-message keyword eval and a phase-aware, conversation-level eval — and
shows the same broken conversation flip from a perfect naive score to a fail.

```
transcripts/synthetic_dialogues.json   three synthetic, generic dialogues
evals/checks.py                        naive vs phase-aware evaluators
run_demo.py                            runs both, prints the comparison
judge/                                 LLM-as-judge calibration (next increment)
```

## Roadmap

- [ ] #2 — guardrail behaviour across conversation branches
- [ ] #3 — calibrating and reporting judge-vs-human agreement (see `judge/`)

## Note on scope

Examples are synthetic and generic on purpose. Where a claim is made, the runnable
reproduction is the evidence — not any one system I've worked on. See the "What
generalizes, and what doesn't" section in note #1.

## License

MIT — see [LICENSE](LICENSE).
