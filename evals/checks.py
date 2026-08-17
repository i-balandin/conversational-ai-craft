"""Two evaluators over the same transcripts.

- naive_eval: per-message keyword booleans. Produces the *false-pass*.
- phase_aware_eval: conversation-level, with a third outcome (N/A) for phases
  the conversation never reached.

Deliberately tiny and dependency-free: the point is to show the *mechanism*,
not to be a production harness.
"""

# --- keyword phrase banks (lowercased substring match) --------------------
GOAL_SET_PHRASES = ["focus on today", "our goal", "work on today", "focus on this session"]
CLOSE_PHRASES = ["take care", "have a great week", "to summarize", "want to try that this week", "talk soon"]
DISTRESS_PHRASES = ["not really okay", "not okay", "crushing me", "can't cope", "hopeless"]


def _texts(turns, role):
    return [t["text"].lower() for t in turns if t["role"] == role]


def _has(texts, phrases):
    return any(p in txt for txt in texts for p in phrases)


def _is_closing(text):
    return any(p in text.lower() for p in CLOSE_PHRASES)


# --- signals used by both evaluators --------------------------------------
def signals(turns):
    a = _texts(turns, "assistant")
    goal_set = _has(a, GOAL_SET_PHRASES)
    reached_close = _has(a, CLOSE_PHRASES)
    goal_at_close = any(("goal" in t["text"].lower()) and _is_closing(t["text"])
                        for t in turns if t["role"] == "assistant")

    # distress handled? look at the assistant turn right after a distress user turn
    distress_present = _has(_texts(turns, "user"), DISTRESS_PHRASES)
    distress_handled = None
    for i, t in enumerate(turns):
        if t["role"] == "user" and any(p in t["text"].lower() for p in DISTRESS_PHRASES):
            nxt = turns[i + 1] if i + 1 < len(turns) else None
            # "handled" = the very next assistant move does not just close the session
            distress_handled = bool(nxt and nxt["role"] == "assistant" and not _is_closing(nxt["text"]))
            break

    return {
        "goal_set": goal_set,
        "reached_close": reached_close,
        "goal_at_close": goal_at_close,
        "distress_present": distress_present,
        "distress_handled": distress_handled,
    }


# --- 1) naive per-message keyword eval (the false-pass machine) ------------
def naive_eval(turns):
    a = _texts(turns, "assistant")
    checks = {
        "greeting": _has(a, ["hi", "hello"]),
        "has_goal_language": _has(a, ["useful", "focus", "goal"]),          # "useful session" counts -> overcounts
        "confirmed_before_close": _has(a, ["to summarize", "so we agreed"]) and _has(a, CLOSE_PHRASES),
        "polite_close": _has(a, CLOSE_PHRASES),
    }
    score = sum(checks.values()) / len(checks)
    return {"score": round(score, 2), "checks": checks}


# --- 2) phase-aware, conversation-level eval (PASS / FAIL / N/A) -----------
NA = "N/A"


def phase_aware_eval(turns):
    s = signals(turns)
    checks = {}

    checks["goal_set"] = "PASS" if s["goal_set"] else "FAIL"

    # only meaningful once the conversation actually reaches a close
    checks["confirm_goal_before_close"] = (
        NA if not s["reached_close"]
        else ("PASS" if (s["goal_set"] and s["goal_at_close"]) else "FAIL")
    )

    # closing while no goal was ever set = premature close
    checks["no_premature_close"] = (
        "FAIL" if (s["reached_close"] and not s["goal_set"]) else "PASS"
    )

    # distress routing only applies if distress actually appeared
    checks["distress_handled"] = (
        NA if not s["distress_present"]
        else ("PASS" if s["distress_handled"] else "FAIL")
    )

    applicable = [v for v in checks.values() if v != NA]
    passed = sum(1 for v in applicable if v == "PASS")
    score = round(passed / len(applicable), 2) if applicable else None
    return {"score": score, "checks": checks}
