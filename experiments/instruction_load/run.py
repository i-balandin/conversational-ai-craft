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

Any provider works. The claim is about instruction load, not about one vendor,
so the script takes whichever key you have:

    export ANTHROPIC_API_KEY=...    # pip install anthropic
    export OPENAI_API_KEY=...       # pip install openai
    export GEMINI_API_KEY=...       # pip install google-genai
    python experiments/instruction_load/run.py

Gemini has a free tier, which makes a full run of this cost nothing. Use it if
you would rather not spend money to check someone else's argument.

Environment:
    CEN_PROVIDER     anthropic | openai | gemini. Default: whichever key is set.
    CEN_MODELS       comma-separated model ids. Two is the useful number - a
                     small model and a large one, since the interesting result
                     is whether the curve has the same shape on both.
                     Defaulted only for anthropic; name them for the others,
                     because model ids move faster than this file does.
    CEN_REPEATS      runs per message per cell (default: 10)
    CEN_TEMPERATURE  sampling temperature (default: 1.0 - run-to-run variation
                     is one of the things being measured, so do not set 0)
    CEN_DELAY        minimum seconds between calls (default 0). Useful only
                     against a per-MINUTE limit. Check which kind your tier
                     has first: a per-day cap is the common one on free tiers,
                     and pacing does nothing about it except make the run
                     longer. Ask for the per-model figure this script prints
                     at startup and compare it with your daily cap.
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

KEY_ENV = {"anthropic": "ANTHROPIC_API_KEY",
           "openai": "OPENAI_API_KEY",
           "gemini": "GEMINI_API_KEY"}
DEFAULT_MODELS = {"anthropic": "claude-haiku-4-5-20251001,claude-sonnet-5"}


def detect_provider():
    named = os.environ.get("CEN_PROVIDER")
    if named:
        return named.strip().lower()
    for provider, env in KEY_ENV.items():
        if os.environ.get(env):
            return provider
    return "anthropic"


PROVIDER = detect_provider()
MODELS = [m.strip() for m in os.environ.get(
    "CEN_MODELS", DEFAULT_MODELS.get(PROVIDER, "")).split(",") if m.strip()]
REPEATS = int(os.environ.get("CEN_REPEATS", "10"))
TEMPERATURE = float(os.environ.get("CEN_TEMPERATURE", "1.0"))
DRY_RUN = os.environ.get("CEN_DRY_RUN") == "1"
DELAY = float(os.environ.get("CEN_DELAY", "0"))
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


def paced(call, min_interval):
    """Hold a minimum interval between calls, counting the call's own latency.

    A free tier rate-limits by requests per minute, and retrying into a limit
    you are still exceeding just burns the backoff. Pacing up front is cheaper
    than recovering: set CEN_DELAY to slightly more than 60/RPM for your tier.
    """
    if min_interval <= 0:
        return call
    import time
    last = [0.0]

    def wrapped(*args, **kwargs):
        wait = min_interval - (time.monotonic() - last[0])
        if wait > 0:
            time.sleep(wait)
        try:
            return call(*args, **kwargs)
        finally:
            last[0] = time.monotonic()

    return wrapped


# A provider can refuse for two reasons that look almost identical and need
# opposite responses. Discriminate on the quota's identity, never on the words
# "quota exceeded", which appear in both.
HOPELESS = re.compile(r"RequestsPerDay|PerDayPerProject|per\s*day|"
                      r"insufficient_quota|billing", re.IGNORECASE)
STATED_DELAY = re.compile(r"retry in ([0-9]+(?:\.[0-9]+)?)s|"
                          r"retryDelay['\"]?\s*:\s*['\"]?([0-9]+)s", re.IGNORECASE)


def stated_delay(text):
    """The wait the provider itself asked for, if it named one."""
    m = STATED_DELAY.search(text)
    if not m:
        return None
    return float(next(g for g in m.groups() if g))


def with_retry(call, attempts=6, base=4.0):
    """Retry a transient limit; stop immediately on one that will not clear.

    A per-minute limit clears while you wait, and a run that dies at call 400
    of 600 wastes the whole thing - so backoff is worth having. A per-DAY quota
    does not clear, and retrying into it burns the remainder of the quota to
    learn nothing. Those need opposite responses.

    It still does not try to classify by exception type - providers spell rate
    limits differently and guessing the spelling is fragile. It looks for the
    one distinction that changes what you should do, in the provider's own
    message, and when in doubt it retries.
    """
    def wrapped(*args, **kwargs):
        import time
        for attempt in range(attempts):
            try:
                return call(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 - see docstring
                text = str(exc)
                if HOPELESS.search(text):
                    raise SystemExit(
                        "\nStopped: the provider names a per-day or billing quota, "
                        "which will not clear by waiting.\n\n" + text[:700] +
                        "\n\nRetrying would spend the rest of it for nothing. Run the "
                        "remaining models tomorrow, or on a model whose daily quota is "
                        "untouched - the buckets are per model.") from exc
                if attempt == attempts - 1:
                    raise
                # Prefer the wait the provider asked for over our own guess.
                asked = stated_delay(text)
                wait = (asked + 1.0) if asked else base * (2 ** attempt)
                source = "provider asked" if asked else "backoff"
                print(f"    retry {attempt + 1}/{attempts - 1} in {wait:.0f}s "
                      f"({source}, {type(exc).__name__})", flush=True)
                time.sleep(wait)
    return wrapped


def anthropic_responder():
    from anthropic import Anthropic
    client = Anthropic()

    def call(model, system, msg, _n_active):
        resp = client.messages.create(
            model=model, max_tokens=300, temperature=TEMPERATURE,
            system=system, messages=[{"role": "user", "content": msg}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")

    return call


def openai_responder():
    from openai import OpenAI
    client = OpenAI()

    def call(model, system, msg, _n_active):
        resp = client.chat.completions.create(
            model=model, max_tokens=300, temperature=TEMPERATURE,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": msg}],
        )
        return resp.choices[0].message.content or ""

    return call


def gemini_responder():
    from google import genai
    from google.genai import types
    client = genai.Client()

    def call(model, system, msg, _n_active):
        resp = client.models.generate_content(
            model=model, contents=msg,
            config=types.GenerateContentConfig(
                system_instruction=system, temperature=TEMPERATURE,
                max_output_tokens=300),
        )
        return resp.text or ""

    return call


# Which of these have been run against a live API, so a reader knows what they
# are trusting. Anthropic: yes. OpenAI and Gemini: written to the documented
# shape of each SDK but not yet exercised with a key. If one of them is wrong,
# it will fail loudly on the first call rather than quietly skew a result - but
# it is an untested path and saying so is cheaper than pretending otherwise.
RESPONDERS = {"anthropic": anthropic_responder,
              "openai": openai_responder,
              "gemini": gemini_responder}


def make_responder():
    if DRY_RUN:
        client = DryRunClient()
        return lambda model, system, msg, n_active: client.reply(n_active)
    if PROVIDER not in RESPONDERS:
        sys.exit(f"Unknown CEN_PROVIDER {PROVIDER!r}. One of: {', '.join(RESPONDERS)}")
    return with_retry(paced(RESPONDERS[PROVIDER](), DELAY))


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
    per_model = len(LOAD_LEVELS) * len(USER_MESSAGES) * 2 * REPEATS
    print(f"{per_model} calls per model, {per_model * len(MODELS)} in total "
          f"({len(MODELS)} models x 2 arms x {len(LOAD_LEVELS)} levels x "
          f"{len(USER_MESSAGES)} messages x {REPEATS} repeats).")
    print("Free tiers are usually capped per DAY per model - check yours against "
          "the per-model figure, not the total, and remember a pilot run spends "
          "from the same bucket.\n", flush=True)

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
    if not DRY_RUN:
        if PROVIDER not in KEY_ENV:
            sys.exit(f"Unknown CEN_PROVIDER {PROVIDER!r}. One of: {', '.join(KEY_ENV)}")
        key_env = KEY_ENV[PROVIDER]
        if not os.environ.get(key_env):
            sys.exit(f"{key_env} is not set. Set a key for any of "
                     f"{', '.join(KEY_ENV.values())}, or run with CEN_DRY_RUN=1 "
                     f"to exercise the pipeline without one.")
        if not MODELS:
            sys.exit(f"Set CEN_MODELS for provider {PROVIDER!r} — two model ids, "
                     f"comma-separated. Model ids move faster than this file, so "
                     f"only the anthropic defaults are hardcoded.")
    main()
