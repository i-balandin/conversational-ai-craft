"""Can your measure fail at all? A pre-flight check, run on real data (note #2).

Before you run an experiment that looks for degradation, check that the thing
you are measuring is capable of registering it. A criterion that never fails at
the easiest condition cannot show you anything getting worse — it will report a
clean sweep whatever happens, and you will read that as a result.

This is the only example here that runs on measured data rather than a fixture:
it reads the committed results.csv from the instruction-load experiment, which
returned a null, and shows why it had to.

    python examples/measure_can_fail/run_demo.py
    python examples/measure_can_fail/run_demo.py path/to/your.csv

Your CSV needs one row per observation, a column per boolean criterion, and one
column naming the condition (load, difficulty, whatever you varied). Point the
three constants below at your own column names and it works on your data.
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CSV = os.path.join(HERE, "..", "..", "experiments", "instruction_load", "results.csv")

CRITERIA = ["one_question", "no_advice", "short"]
CONDITION = "declared_extras"       # the thing that was varied
EASIEST = "0"                        # its easiest level


def load(path):
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main(path=None):
    rows = load(path or DEFAULT_CSV)
    baseline = [r for r in rows if r[CONDITION] == EASIEST]

    print(__doc__.strip().split("\n\n")[0])
    print()
    print(f"{len(rows)} observations, {len(baseline)} of them at the easiest condition "
          f"({CONDITION}={EASIEST}).")
    print()
    print(f"  {'criterion':<16}{'fails at easiest':>18}{'fails anywhere':>17}   verdict")
    print("  " + "-" * 72)

    dead = []
    for c in CRITERIA:
        f_base = sum(1 for r in baseline if r[c] == "False")
        f_all = sum(1 for r in rows if r[c] == "False")
        if f_base == 0 and f_all == 0:
            verdict = "NEVER FAILS - cannot show degradation"
            dead.append(c)
        elif f_base == 0:
            verdict = "no headroom at baseline; weak"
        else:
            verdict = "can fail; usable"
        print(f"  {c:<16}{f_base:>10}/{len(baseline):<7}{f_all:>9}/{len(rows):<7}   {verdict}")

    print()
    if dead:
        print(f"  {len(dead)} of {len(CRITERIA)} criteria never failed once, anywhere in the run.")
        print("  For those, a pass carries no information: they would have reported")
        print("  a clean sweep no matter what the condition did. An experiment whose")
        print("  measure cannot move cannot find an effect, and its null says")
        print("  something about the instrument rather than about the world.")
    else:
        print("  Every criterion failed somewhere, so the measure has room to move.")
    print()

    print("=" * 76)
    print("The rule, stated so you can run it before spending anything:")
    print()
    print("  Before an experiment that looks for degradation, verify that each")
    print("  criterion fails at least sometimes under the EASIEST condition.")
    print("  A criterion that passes 100% at baseline has no room to fall, and")
    print("  including it inflates your headline while measuring nothing.")
    print()
    print("It costs one small run at baseline. Skipping it cost me a full")
    print("experiment: the note that ships this data reports a null, and the")
    print("reason is in the table above rather than in the models or the rules.")


if __name__ == "__main__":
    main(*sys.argv[1:2])
