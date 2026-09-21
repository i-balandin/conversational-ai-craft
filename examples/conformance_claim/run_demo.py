"""What your eval set can and cannot substantiate: a modeled example (note #8).

Someone hands you a respected quality framework and asks you to make the
assistant conform to it, and to show that it does. You write eval criteria and
report a percentage. The percentage is almost always wrong, and wrong upwards,
because an eval criterion is a judgement about a transcript, a good part of any
such framework describes things a transcript cannot show, and the criteria
someone writes anyway for those parts count as coverage while proving nothing.

This prints three views of the same framework:

  grep       a principle counts as covered if some criterion mentions it
  addressed  a principle counts as covered if a criterion is mapped to it,
             which includes the criteria that cannot substantiate anything
  honest     each principle is sorted by the instrument that can actually
             see it, and the claim is stated per instrument with its
             assurance level

The framework below is invented for this file - a plain set for a support
assistant, with a shape chosen to exercise every case rather than to resemble
anyone's real standard. Bring your own list and the arithmetic is the same. No API key, no dependencies.

    python examples/conformance_claim/run_demo.py
"""

# trace: what a transcript can show of this principle.
#   full    the behaviour happens in the conversation and is visible there
#   partial part of it is visible; the rest is a property of the system
#   none    nothing about it appears in a conversation, ever
FRAMEWORK = [
    ("P1  Answer within competence",         "full"),
    ("P2  Disclose that you are automated",  "full"),
    ("P3  Hand over to a person on request", "full"),
    # Visible in a conversation, and nothing checks it. A plain gap, and the
    # easiest kind to close - which is why it is worth separating from the
    # gaps that no criterion could close.
    ("P4  Never pressure or manipulate",     "full"),
    ("P5  Escalate a safety concern",        "partial"),
    ("P6  Keep customer data minimal",       "none"),
    ("P7  Review releases before shipping",  "none"),
]

# What we actually have. A session criterion is a judge over a transcript.
SESSION_CRITERIA = {
    "states its limits when asked":      "P1",
    "identifies itself as automated":    "P2",
    "offers a human when asked":         "P3",
    "routes a safety concern correctly": "P5",
    # Written with good intentions, mapped to a principle a transcript cannot
    # show. It is worse than having nothing: it manufactures the appearance of
    # coverage, and it is the single most common way a conformance claim goes
    # wrong upwards.
    "respects data minimisation":        "P6",
}

# An attestation item is a per-release declaration with evidence behind it.
ATTESTATION = {
    "P6": ("retention policy + deletion log", "evidence-backed"),
    "P7": ("release checklist, signed",       "self-declared"),
}

# The tempting shortcut: a criterion "covers" a principle if its text mentions
# a word from the principle. Kept here because it is what a keyword-based
# conformance harness actually does.
def grep_coverage():
    covered = set()
    for crit in SESSION_CRITERIA:
        for name, _trace in FRAMEWORK:
            words = {w.lower().strip(",.") for w in name.split()[1:] if len(w) > 4}
            if words & {w.lower().strip(",.") for w in crit.split()}:
                covered.add(name)
    return covered


def classify(name, trace):
    """Which instrument can substantiate this principle, given what we have."""
    pid = name.split()[0]
    has_criterion = pid in SESSION_CRITERIA.values()
    has_attestation = pid in ATTESTATION

    if trace in ("full", "partial") and has_criterion:
        return ("measured", "session eval",
                "partial — the rest is a system property" if trace == "partial" else "")
    if trace in ("full", "partial") and not has_criterion:
        return ("not evidenced", "a transcript could show this, and nothing checks it", "")
    if trace == "none" and has_criterion:
        return ("SPURIOUS", "a session criterion for something no transcript shows",
                "counts as coverage and substantiates nothing")
    if trace == "none" and has_attestation:
        item, level = ATTESTATION[pid]
        return ("attested", f"attestation: {item}", level)
    return ("not evidenced", "no transcript trace and no attestation", "")


def main():
    print(__doc__.strip().split("\n\n")[0])
    print()

    grepped = grep_coverage()
    addressed = {n for n, _t in FRAMEWORK if n.split()[0] in SESSION_CRITERIA.values()}
    total = len(FRAMEWORK)

    print(f"{'principle':<40}{'trace':<10}{'status':<15}instrument")
    print("-" * 96)
    buckets = {"measured": [], "attested": [], "SPURIOUS": [], "not evidenced": []}
    for name, trace in FRAMEWORK:
        status, instrument, note = classify(name, trace)
        buckets[status].append(name)
        extra = f"  [{note}]" if note else ""
        print(f"{name:<40}{trace:<10}{status:<15}{instrument}{extra}")

    print()
    print("Three numbers you could report, from the same facts:")
    print(f"  grep coverage        {len(grepped)}/{total}  "
          f"({len(grepped) / total:.0%})   <- a keyword harness would print this")
    print(f"  principles addressed {len(addressed)}/{total}  "
          f"({len(addressed) / total:.0%})   <- honest about the criteria, silent about the gaps")
    print(f"  measured by eval     {len(buckets['measured'])}/{total}  "
          f"({len(buckets['measured']) / total:.0%})   <- what the eval set can actually substantiate")
    print()
    print("And the statement worth making, which is not a number at all:")
    print()
    for status in ("measured", "attested", "SPURIOUS", "not evidenced"):
        names = buckets[status]
        print(f"  {status:<15} {len(names)}: {', '.join(n.split()[0] for n in names) or '-'}")
    print()
    attested_pids = [n.split()[0] for n in buckets["attested"]]
    if attested_pids:
        print("  Of those attested, the assurance level differs per item -")
        for pid in attested_pids:
            print(f"    {pid}: {ATTESTATION[pid][1]}")
    unused = sorted(set(ATTESTATION) - set(attested_pids))
    if unused:
        print(f"  Attestation exists for {', '.join(unused)} too, but a session")
        print(f"  criterion was also mapped there, so the claim reads as measured")
        print(f"  when it is not. Drop the criterion and keep the attestation.")
    print()

    print("=" * 96)
    print("The single percentage is the problem. It averages four kinds of")
    print("evidence that cannot be averaged: something a judge measured,")
    print("something a person signed for, something nobody has checked, and")
    print("something that looks checked and is not. Report the buckets, and")
    print("each attestation's assurance level.")
    print()
    print("A score is not a measurement without its spread either. Alongside")
    print("each session criterion, publish the range the same transcripts gave")
    print("over repeated runs - and keep a small set of invariants that have no")
    print("spread at all, where one violation is a failure rather than a dip in")
    print("an average. Those invariants are the floor from note #3, arriving")
    print("from the governance side of the same argument.")


if __name__ == "__main__":
    main()
