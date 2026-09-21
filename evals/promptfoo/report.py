"""Turn a promptfoo run into a number worth quoting.

promptfoo reports one headline: how many assertions passed. For a suite whose
criteria are gated on stages of a conversation, that headline counts every
criterion that had nothing to judge as a success. It is the vacuous pass from
note #1, arriving through a standard, well-built tool rather than a toy.

This script reads the run's JSON and prints both numbers side by side, plus the
one figure the headline can never contain: how many conversations reached the
stage each criterion is about.

    python report.py results.json
"""
import json
import sys
from collections import defaultdict


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)["results"]["results"]


def main(path="results.json"):
    rows = load(path)

    headline_pass = sum(1 for r in rows if r["success"])
    by_criterion = defaultdict(lambda: {"applicable": 0, "passed": 0, "na": 0, "total": 0})

    for r in rows:
        crit = r["vars"]["criterion"]
        named = r.get("namedScores") or {}
        bucket = by_criterion[crit]
        bucket["total"] += 1
        if named.get("applicable"):
            bucket["applicable"] += 1
            bucket["passed"] += int(bool(named.get("passed")))
        else:
            bucket["na"] += 1

    print()
    print(f"promptfoo headline      : {headline_pass}/{len(rows)} assertions passed "
          f"({headline_pass / len(rows):.0%})")
    print("  ^ counts every not-applicable result as a pass. Do not quote this.")
    print()
    print(f"{'criterion':<28}{'applicable':>11}{'passed':>8}{'rate':>8}{'N/A':>6}")
    print("-" * 61)

    applicable_total = passed_total = 0
    for crit, b in by_criterion.items():
        rate = f"{b['passed'] / b['applicable']:.0%}" if b["applicable"] else "  --"
        print(f"{crit:<28}{b['applicable']:>11}{b['passed']:>8}{rate:>8}{b['na']:>6}")
        applicable_total += b["applicable"]
        passed_total += b["passed"]

    print("-" * 61)
    rate = f"{passed_total / applicable_total:.0%}" if applicable_total else "  --"
    print(f"{'over applicable only':<28}{applicable_total:>11}{passed_total:>8}{rate:>8}"
          f"{len(rows) - applicable_total:>6}")
    print()

    for crit, b in by_criterion.items():
        if b["na"]:
            print(f"stage reach: {crit} — {b['applicable']}/{b['total']} conversations "
                  f"reached the stage this criterion judges")
    print()
    print("A criterion whose stage reach is low is not measuring what its name says.")
    print("Report the reach next to the rate, or the rate is resting on very little.")

    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
