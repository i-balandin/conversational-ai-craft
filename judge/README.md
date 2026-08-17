# LLM-as-judge calibration (next increment)

The evaluators in `../evals/checks.py` are deterministic (keyword and
structure based) so the false-pass demo runs with no API key. In practice the
conversation-level checks — "was the goal referenced", "was distress handled" —
are better done by an LLM-as-judge. The risk is that an uncalibrated judge
produces confident numbers no human ever checked.

This directory is where note #3 will live. The plan:

1. **`labels.jsonl`** — a small set of transcripts hand-labelled by a human
   (pass/fail per conversation-level criterion). This is the ground truth.
2. **`judge_prompt.md`** — the judge prompt: given a transcript and a criterion,
   return a verdict + one line of reasoning.
3. **`calibrate.py`** — run the judge over the labelled set and report
   **judge-vs-human agreement** (e.g. Cohen's kappa, plus a confusion table).
   That number is reported *next to* any eval result the judge produces.

Principle: a judge is worth exactly what it agrees with a human on. If it
disagrees with a human half the time, its score is decoration — and everyone
looking at the dashboard should be able to see that.

*(Stub — to be built. No working code here yet.)*
