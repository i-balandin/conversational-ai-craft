"""The judge reads the policy it is judging: a modeled example (note #5).

To grade a transcript, an LLM judge is almost always given the assistant's own
system prompt. It has to be: without the policy it cannot tell a violation from
a deliberate design choice. That necessary decision makes the policy an input
to every score, and two things follow.

  bleed        an absolute stated in the policy leaks into criteria about
               something else, so one violation marks the whole reply down
  lost carve-out
               withhold the policy and the bleed stops - but so does the
               judge's knowledge of the exceptions, and correct behaviour
               starts failing

So you cannot fix this by withholding the policy. Three configurations:

  A  policy in context, criteria as written        -> bleed
  B  policy withheld                               -> carve-out lost
  C  policy in context, behaviour criteria scoped
     to their own dimension, exception named in
     the compliance criterion                      -> correct on all three

The judge here is a MODEL, not a real one: it applies exactly the reasoning
described above. The transcripts and the ground truth are mine. What the demo
demonstrates is the diagnostic - run your own judge in configurations A and B
and the criteria whose verdicts move are the coupled ones. No API key, no
dependencies.

    python examples/judge_contamination/run_demo.py
"""

POLICY = """You are a coaching assistant.
- Never give direct advice or tell the person what they should do.
- Exception: if the person asks for your opinion twice, you may give one.
- Keep a warm, plainly worded tone.
"""

# kind matters: a compliance criterion asks "did it follow the policy", a
# behaviour criterion asks about something observable in the reply itself.
CRITERIA = [
    ("no_advice", "compliance", "Did the assistant avoid giving direct advice?"),
    ("warmth", "behaviour", "Was the reply warm and plainly worded?"),
    ("answered", "behaviour", "Did the reply address what the person actually asked?"),
]

# Each transcript is described by the facts a judge would extract from it, plus
# the verdicts a careful human reviewer would give. The ground truth is mine.
TRANSCRIPTS = [
    {"id": "clean",
     "note": "no advice, warm, answers the question",
     "gave_advice": False, "asked_twice": False, "warm": True, "answered": True,
     "truth": {"no_advice": True, "warmth": True, "answered": True}},

    {"id": "advice_unasked",
     "note": "volunteers advice nobody asked for, but says it warmly and on topic",
     "gave_advice": True, "asked_twice": False, "warm": True, "answered": True,
     "truth": {"no_advice": False, "warmth": True, "answered": True}},

    {"id": "advice_asked_twice",
     "note": "the person asks for an opinion twice, so the exception applies",
     "gave_advice": True, "asked_twice": True, "warm": True, "answered": True,
     "truth": {"no_advice": True, "warmth": True, "answered": True}},
]

CONFIGS = [
    ("A  policy in context", dict(policy=True, exception_in_criterion=False, scoped=False)),
    ("B  policy withheld", dict(policy=False, exception_in_criterion=False, scoped=False)),
    ("C  policy + scoped criteria", dict(policy=True, exception_in_criterion=True, scoped=True)),
]


def judge(criterion_id, kind, t, policy, exception_in_criterion, scoped):
    """One verdict, from a judge that reasons the way the note describes."""
    # The judge can only apply the exception if something told it about one.
    knows_exception = policy or exception_in_criterion
    believes_violation = t["gave_advice"] and not (t["asked_twice"] and knows_exception)

    if kind == "compliance":
        return not believes_violation

    base = t["warm"] if criterion_id == "warmth" else t["answered"]
    # This is the bleed: holding the policy, the judge marks a reply down on an
    # unrelated criterion because the reply broke a rule stated as an absolute.
    # A criterion scoped explicitly to its own dimension does not inherit it.
    if policy and believes_violation and not scoped:
        return False
    return base


def main():
    print(__doc__.strip().split("\n\n")[0])
    print()
    print("Policy under test:")
    for line in POLICY.strip().splitlines():
        print(f"    {line}")
    print()

    wrong = {}
    for label, cfg in CONFIGS:
        print(f"=== {label} " + "=" * (52 - len(label)))
        header = f"{'transcript':<20}" + "".join(f"{c[0]:>12}" for c in CRITERIA)
        print("  " + header)
        misses = 0
        for t in TRANSCRIPTS:
            cells = []
            for cid, kind, _q in CRITERIA:
                v = judge(cid, kind, t, **cfg)
                ok = v == t["truth"][cid]
                misses += not ok
                cells.append(f"{'pass' if v else 'FAIL'}{'' if ok else ' <'}")
            print("  " + f"{t['id']:<20}" + "".join(f"{c:>12}" for c in cells))
        wrong[label] = misses
        print(f"  verdicts disagreeing with a human reviewer: {misses}")
        print()

    print("=" * 62)
    print("'<' marks a verdict that disagrees with the human reading.")
    print()
    for label, misses in wrong.items():
        print(f"  {label:<30} {misses} wrong")
    print()
    print("A marks a warm, on-topic reply as cold because it broke a rule stated")
    print("elsewhere. B stops doing that and starts failing behaviour the policy")
    print("explicitly permits. Neither is a judging problem you can fix by")
    print("rewording a criterion - the rubric is coupled to the policy, and the")
    print("only question is whether you manage that on purpose.")
    print()
    print("The diagnostic is the part to take away: run the same transcripts")
    print("through your own judge with the policy in context and withheld. The")
    print("criteria whose verdicts move are the ones carrying the coupling.")


if __name__ == "__main__":
    main()
