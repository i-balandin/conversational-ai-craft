# The stage-aware suite, in a standard harness

Note #1 argues that stage-gated criteria pass vacuously on conversations that
never reached the stage, and that the remedy is a third answer plus a reported
stage-reach rate. The example under `examples/false_pass/` makes that argument
with an evaluator I wrote. This directory makes it again in
[promptfoo](https://promptfoo.dev), because an argument that only holds inside
my own harness is not worth much.

## Running it

```
cd evals/promptfoo
npm install
npm run eval
npm run report
```

No API key, no cost, no network beyond the install. The provider replays fixed
transcripts from `examples/false_pass/transcripts.json` rather than calling a
model — the evaluator is the variable under test, so the model must not be one.
The same two commands run in CI on every push.

## What you should see

promptfoo's own summary:

```
Successes: 6
Failures: 3
Pass Rate: 66.67%
```

and then `report.py`:

```
promptfoo headline      : 6/9 assertions passed (67%)
  ^ counts every not-applicable result as a pass. Do not quote this.

criterion                    applicable  passed    rate   N/A
-------------------------------------------------------------
goal_set                              3       2     67%     0
goal_referenced_at_close              2       1     50%     1
distress_handled                      1       0      0%     2
-------------------------------------------------------------
over applicable only                  6       3     50%     3
```

Same nine assertions. 67% against 50%, and a criterion sitting at 0% that the
headline could not show you, because two of its three results had nothing to
judge and were counted as passes.

## The part that is a finding about the tool

promptfoo is well built and this is not a complaint about it. But its assertion
API is binary — an assertion returns a pass or a fail — and there is no way to
say *this did not apply*. A criterion about the close of a conversation, handed
a conversation with no close, has to answer anyway, and the answer it gives is
a pass.

So the third answer has to be carried out of band. Each assertion in
`assert_stage_aware.py` emits `namedScores`:

```python
"namedScores": {"applicable": 1.0 or 0.0, "passed": 1.0 or 0.0}
```

and `report.py` computes the rate over applicable results only. **The naive
headline is deliberately left visible.** Hiding it would lose the demonstration,
and in a real project it is what a stakeholder reads off the dashboard.

If your harness has the same shape — and most do — this is roughly a
half-day's work and it changes which number you take to a go/no-go meeting.

## Files

| File | What it is |
|---|---|
| `promptfooconfig.yaml` | 3 transcripts x 3 criteria |
| `provider_replay.py` | returns a stored transcript instead of calling a model |
| `assert_stage_aware.py` | the criteria, each declaring whether it applied |
| `report.py` | recomputes over applicable results and prints stage reach |
| `package.json` | pins promptfoo, so the suite runs the same way next year |

## A note on the pin

promptfoo is pinned rather than floated. An evaluation harness that silently
changes under a fixed test set is the same class of problem as everything else
in this repository: the instrument moved and the report did not say so.
