"""Stage-aware assertions for promptfoo: pass, fail, and the third answer.

promptfoo assertions are binary. A criterion about the close of a conversation
is therefore forced to say pass or fail about a conversation that has no close,
and the answer it gives is pass — which is the vacuous pass note #1 is about,
reproduced inside a standard harness rather than in a toy of my own.

There is no "skip" in the assertion API, so the third answer has to be carried
out of band. Every assertion below emits `namedScores`:

    applicable = 1  the conversation reached the stage this criterion is about
    applicable = 0  it did not, and this result must be excluded from the score
    passed          1 or 0, meaningful only where applicable = 1

`report.py` is what turns those into the number worth quoting. promptfoo's own
headline pass rate for this suite is the naive one, and it is wrong on purpose:
leaving it visible next to the corrected number is the entire demonstration.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "examples", "false_pass"))

from checks import signals  # noqa: E402


def _result(passed, applicable, reason):
    return {
        "pass": bool(passed),
        "score": 1.0 if passed else 0.0,
        "reason": reason,
        "namedScores": {"applicable": 1.0 if applicable else 0.0,
                        "passed": 1.0 if (applicable and passed) else 0.0},
    }


def _sig(output):
    return signals(json.loads(output)["turns"])


def goal_set(output, context=None):
    """Always applicable: every conversation has an opening."""
    s = _sig(output)
    return _result(s["goal_set"], True,
                   "a goal was set" if s["goal_set"] else "no goal was set")


def goal_referenced_at_close(output, context=None):
    """Applicable only if the conversation reached a close.

    This is the criterion that produces the vacuous pass. Run it binary and a
    conversation that stops halfway is scored as if it closed well.
    """
    s = _sig(output)
    if not s["reached_close"]:
        return _result(True, False, "N/A - the conversation never reached a close")
    return _result(s["goal_at_close"], True,
                   "the close refers back to the goal" if s["goal_at_close"]
                   else "closed without referring back to the goal")


def distress_handled(output, context=None):
    """Applicable only if the user signalled distress at all."""
    s = _sig(output)
    if not s["distress_present"]:
        return _result(True, False, "N/A - no distress signal in this conversation")
    return _result(s["distress_handled"], True,
                   "the next move responded to it" if s["distress_handled"]
                   else "the assistant moved on or closed instead")


def get_assert(output, context=None):
    """Default entry point: dispatch on the criterion named in the test's vars."""
    name = (getattr(context, "vars", None) or {}).get("criterion") if context else None
    if name is None and isinstance(context, dict):
        name = context.get("vars", {}).get("criterion")
    fn = {"goal_set": goal_set,
          "goal_referenced_at_close": goal_referenced_at_close,
          "distress_handled": distress_handled}.get(name)
    if fn is None:
        return {"pass": False, "score": 0.0, "reason": f"unknown criterion: {name!r}"}
    return fn(output, context)
