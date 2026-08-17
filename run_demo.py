"""Run the false-pass demo.

    python run_demo.py

No dependencies, no API key. Watch the broken conversation score a perfect
1.0 under the naive eval (a false-pass) and fail under the phase-aware eval,
while the truncated one stops being penalised for a phase it never reached.
"""
import json
import os

from evals.checks import naive_eval, phase_aware_eval

HERE = os.path.dirname(__file__)


def main():
    with open(os.path.join(HERE, "transcripts", "synthetic_dialogues.json"), encoding="utf-8") as f:
        transcripts = json.load(f)

    print(f"{'transcript':<24}{'naive':>10}{'phase-aware':>14}")
    print("-" * 48)
    for t in transcripts:
        n = naive_eval(t["turns"])
        p = phase_aware_eval(t["turns"])
        print(f"{t['id']:<24}{n['score']:>10}{str(p['score']):>14}")

    print("\nDetail:")
    for t in transcripts:
        p = phase_aware_eval(t["turns"])
        print(f"\n  {t['id']}")
        print(f"    note: {t['note']}")
        for name, verdict in p["checks"].items():
            print(f"    - {name}: {verdict}")

    print(
        "\nRead the table top to bottom:\n"
        "  looks_good_but_broken -> naive 1.0 (FALSE-PASS) but phase-aware 0.0 (caught)\n"
        "  truncated             -> naive drops it for a missing close; phase-aware marks\n"
        "                           that check N/A and does not penalise it\n"
        "  clean                 -> passes both\n"
    )


if __name__ == "__main__":
    main()
