"""Instruction-load experiment for note #2 ("More rules, less control").

Two questions, one run:

  1. As more realistic client rules are added to a system prompt, how well does
     the assistant still keep a few core rules you can check mechanically, and
     how much do repeated runs of the same input disagree with each other?
  2. Does *scoping* those rules help? At the same declared rule count, the
     scoped arm puts only the rules belonging to the current stage in front of
     the model. That is the direct test of design move 1 in the note.

Two arms, five load levels, two models, repeated runs. Nothing about the result
is assumed: the scoped arm can lose.

    pip install anthropic
    export ANTHROPIC_API_KEY=...          # set ANTHROPIC_API_KEY=... on Windows
    python experiments/instruction_load/run.py

Environment:
    CEN_MODELS       comma-separated model ids
                     (default: claude-haiku-4-5-20251001,claude-sonnet-5)
    CEN_REPEATS      runs per message per cell (default: 10)
    CEN_TEMPERATURE  sampling temperature (default: 1.0 - run-to-run variation
                     is one of the things being measured, so do not set 0)
    CEN_DRY_RUN      1 to exercise the whole pipeline with a canned responder,
                     no API key and no cost. Use it to check the plumbing.

Writes results.csv and, if matplotlib is present, adherence.png next to this
file. Both are committed once a real run has been done, so the numbers in the
note can be traced to the run that produced them.
"""
import csv
import os
import random
import re
import statistics
import sys
from collections import defaultdict

MODELS = [m.strip() for m in os.environ.get(
    "CEN_MODELS", "claude-haiku-4-5-20251001,claude-sonnet-5").split(",") if m.strip()]
REPEATS = int(os.environ.get("CEN_REPEATS", "10"))
TEMPERATURE = float(os.environ.get("CEN_TEMPERATURE", "1.0"))
DRY_RUN = os.environ.get("CEN_DRY_RUN") == "1"
LOAD_LEVELS = [0, 5, 10, 20, 40]
STAGES = 4

CORE_RULES = [
    "Ask exactly one question in each reply.",
    "Never give direct advice or tell the person what they should do.",
    "Keep every reply under 80 words.",
]

# Plausible client-specific rules. They do not conflict with the core rules on
# purpose: the experiment measures load, not contradiction.
EXTRA_RULES = [
    "Use the person's own words when reflecting back what they said.",
    "Refer to the session as a 'conversation', never a 'session'.",
    "Acknowledge feelings before moving to the next topic.",
    "Avoid jargon such as 'synergy', 'leverage' or 'bandwidth'.",
    "If the person mentions a deadline, note it explicitly.",
    "Use British spelling.",
    "Do not use emojis.",
    "Do not mention that you are an AI unless asked.",
    "If the person mentions their manager, ask about the relationship.",
    "Prefer open questions starting with 'what' or 'how'.",
    "Never use the word 'why' at the start of a question.",
    "If the person sounds uncertain, slow down and reflect before asking.",
    "Do not summarise more than once per conversation.",
    "Mention the person's stated goal when it becomes relevant.",
    "Avoid starting consecutive replies with the same word.",
    "Do not use bullet points.",
    "If the person asks for resources, say they can discuss them with their coach.",
    "Use a warm but professional tone.",
    "Do not repeat the person's full message back to them.",
    "If the person changes topic, acknowledge the change briefly.",
    "Avoid exclamation marks.",
    "Do not use the phrase 'I understand'.",
    "When the person reports progress, name one specific thing they did.",
    "Do not ask about personal life unless the person raises it.",
    "Refer to challenges as 'situations', not 'problems'.",
    "If the person mentions stress, check how they are before continuing.",
    "Do not make promises about outcomes.",
    "Keep language gender-neutral.",
    "If the person asks a factual question, say you focus on their thinking, not facts.",
    "Do not quote famous people.",
    "Avoid the word 'journey'.",
    "If the person seems stuck, invite them to describe a small next step.",
    "Do not compare the person to others.",
    "Use present tense where possible.",
    "If the person thanks you, respond briefly and continue.",
    "Do not use rhetorical questions.",
    "Avoid the phrase 'at the end of the day'.",
    "If the person mentions a meeting, ask what they want from it.",
    "Do not mention time limits of the conversation.",
    "Avoid starting a reply with 'So'.",
]

USER_MESSAGES = [
    "I have a performance review next week and I'm dreading it.",
    "My team keeps missing deadlines and I don't know how to raise it.",
    "I think I want to change careers but I'm not sure where to start.",
    "What should I say to my manager about getting a promotion?",
    "Honestly I just feel overwhelmed with everything at work right now.",
]

ADVICE_PATTERNS = re.compile(
    r"\b(you should|you need to|i recommend|i suggest|try to|make sure you|i'd advise)\b",
    re.IGNORECASE,
)


# ------------------------------------------------------------------ the arms

def active_extras(n_extra, arm, msg_idx):
    """Which of the declared extra rules the model actually sees this turn.

    flat    all of them, every turn - the accumulating rule list the note is about
    scoped  only the slice belonging to this stage, which is what "put rules
            where they apply" means in practice

    The declared count is identical in both arms. Only how many are in front of
    the model at once differs, which is the whole claim under test.
    """
    declared = EXTRA_RULES[:n_extra]
    if arm == "flat" or not declared:
        return declared
    stage = msg_idx % STAGES
    per_stage = max(1, len(declared) // STAGES)
    return declared[stage * per_stage:(stage + 1) * per_stage] or declared[:per_stage]


def build_system_prompt(rules):
    lines = "\n".join(f"- {r}" for r in CORE_RULES + rules)
    return f"You are a coaching assistant. Follow all of these rules:\n{lines}"


# ------------------------------------------------------------- the criteria

def check_core(reply):
    return {
        "one_question": reply.count("?") == 1,
        "no_advice": ADVICE_PATTERNS.search(reply) is None,
        "short": len(reply.split()) < 80,
    }


# ------------------------------------------------------------- the responder

class DryRunClient:
    """Canned responder so the pipeline can be checked without a key or a bill.

    It degrades with load on purpose - that is what makes it useful for testing
    the plumbing, and exactly why its output must never be published as a
    result. A dry run proves the script works, not that the claim holds.
    """

    def __init__(self, seed=7):
        self.rng = random.Random(seed)

    def reply(self, n_active):
        p_keep = max(0.25, 1.0 - 0.02 * n_active)
        if self.rng.random() < p_keep:
            return "That sounds like a lot to carry. What matters most to you about it?"
        return ("You should raise it with your manager directly, and you need to "
                "prepare notes first. What do you think? Does that feel possible? ")


def make_responder():
    if DRY_RUN:
        client = DryRunClient()
        return lambda model, system, msg, n_active: client.reply(n_active)

    from anthropic import Anthropic
    client = Anthropic()

    def call(model, system, msg, n_active):
        resp = client.messages.create(
            model=model, max_tokens=300, temperature=TEMPERATURE,
            system=system, messages=[{"role": "user", "content": msg}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")

    return call


# ------------------------------------------------------------------- the run

def instability(flags):
    """How often repeated runs of the same input disagree.

    0.0 means every repeat gave the same verdict; 0.5 is a coin flip. This is
    the second thing the note claims moves with load, and a mean adherence
    figure cannot show it.
    """
    if not flags:
        return 0.0
    p = sum(flags) / len(flags)
    return round(min(p, 1 - p), 3)


def main():
    respond = make_responder()
    rows = []

    for model in MODELS:
        for arm in ("flat", "scoped"):
            for n_extra in LOAD_LEVELS:
                for msg_idx, msg in enumerate(USER_MESSAGES):
                    rules = active_extras(n_extra, arm, msg_idx)
                    system = build_system_prompt(rules)
                    for rep in range(REPEATS):
                        reply = respond(model, system, msg, len(rules) + len(CORE_RULES))
                        checks = check_core(reply)
                        rows.append({
                            "model": model, "arm": arm, "temperature": TEMPERATURE,
                            "declared_extras": n_extra, "active_extras": len(rules),
                            "message": msg_idx, "repeat": rep,
                            **checks, "all_core": all(checks.values()),
                            "words": len(reply.split()),
                        })
                print(f"{model:<28} {arm:<7} declared={n_extra:>2} done", flush=True)

    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "results.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    summary = summarise(rows)
    print_summary(summary)
    write_chart(summary, here)

    print(f"\nWrote {out}")
    if DRY_RUN:
        print("DRY RUN - canned responder. These numbers are plumbing, not evidence.")


def summarise(rows):
    cells = defaultdict(list)
    for r in rows:
        cells[(r["model"], r["arm"], r["declared_extras"], r["message"])].append(r)

    out = defaultdict(dict)
    for (model, arm, load, _msg), group in cells.items():
        out[(model, arm, load)].setdefault("core", []).extend(g["all_core"] for g in group)
        out[(model, arm, load)].setdefault("words", []).extend(g["words"] for g in group)
        out[(model, arm, load)].setdefault("per_msg", []).append(
            instability([g["all_core"] for g in group]))
        for crit in ("one_question", "no_advice", "short"):
            out[(model, arm, load)].setdefault(crit, []).extend(g[crit] for g in group)
    return out


def print_summary(summary):
    print("\nmodel                        arm      declared  core   1q    adv   len   instab  words")
    print("-" * 92)
    for (model, arm, load) in sorted(summary):
        s = summary[(model, arm, load)]
        rate = lambda k: sum(s[k]) / len(s[k])  # noqa: E731
        print(f"{model:<28} {arm:<8} {load:>8}  "
              f"{rate('core'):.2f}  {rate('one_question'):.2f}  {rate('no_advice'):.2f}  "
              f"{rate('short'):.2f}  {statistics.mean(s['per_msg']):>6.3f}  "
              f"{statistics.mean(s['words']):>5.1f}")
    print("\ncore = all three core rules kept · instab = mean run-to-run disagreement "
          "(0 = identical verdicts, 0.5 = coin flip)")


def write_chart(summary, here):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib not installed - skipping the chart)")
        return

    models = sorted({m for (m, _a, _l) in summary})
    fig, axes = plt.subplots(1, len(models), figsize=(6 * len(models), 4), squeeze=False)
    for ax, model in zip(axes[0], models):
        for arm, style in (("flat", "-o"), ("scoped", "--s")):
            loads = sorted(l for (m, a, l) in summary if m == model and a == arm)
            ys = [sum(summary[(model, arm, l)]["core"]) / len(summary[(model, arm, l)]["core"])
                  for l in loads]
            ax.plot(loads, ys, style, label=arm)
        ax.set_title(model, fontsize=10)
        ax.set_xlabel("extra rules declared")
        ax.set_ylabel("core-rule adherence")
        ax.set_ylim(0, 1.02)
        ax.grid(alpha=0.3)
        ax.legend()
    fig.tight_layout()
    path = os.path.join(here, "adherence.png")
    fig.savefig(path, dpi=120)
    print(f"Wrote {path}")


if __name__ == "__main__":
    if not DRY_RUN and not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set. Set it, or run with CEN_DRY_RUN=1 "
                 "to exercise the pipeline without a key.")
    main()
