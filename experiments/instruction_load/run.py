"""Instruction-load experiment for note #2 ("More rules, less control").

Measures how well an assistant keeps a few checkable CORE rules as more
realistic EXTRA rules are added to its system prompt, and how much results
vary between repeated runs.

Needs an Anthropic API key:
    pip install anthropic
    set ANTHROPIC_API_KEY=...          (Windows)  /  export ANTHROPIC_API_KEY=...
    python experiments/instruction_load/run.py

Optional env vars:
    CEN_MODEL    model id (default: claude-haiku-4-5-20251001)
    CEN_REPEATS  runs per message per load level (default: 3)

Writes results.csv next to this file. No results are shipped with the repo:
numbers depend on model and rules, so run it yourself.
"""
import csv
import os
import re
import statistics

from anthropic import Anthropic

MODEL = os.environ.get("CEN_MODEL", "claude-haiku-4-5-20251001")
REPEATS = int(os.environ.get("CEN_REPEATS", "3"))
LOAD_LEVELS = [0, 5, 10, 20, 40]

CORE_RULES = [
    "Ask exactly one question in each reply.",
    "Never give direct advice or tell the person what they should do.",
    "Keep every reply under 80 words.",
]

# Plausible client-specific rules. They don't conflict with the core rules
# on purpose: the experiment measures load, not contradiction.
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


def build_system_prompt(n_extra):
    rules = CORE_RULES + EXTRA_RULES[:n_extra]
    lines = "\n".join(f"- {r}" for r in rules)
    return f"You are a coaching assistant. Follow all of these rules:\n{lines}"


def check_core(reply):
    one_question = reply.count("?") == 1
    no_advice = ADVICE_PATTERNS.search(reply) is None
    short = len(reply.split()) < 80
    return {"one_question": one_question, "no_advice": no_advice, "short": short}


def main():
    client = Anthropic()
    rows = []
    for n_extra in LOAD_LEVELS:
        system = build_system_prompt(n_extra)
        for msg_idx, msg in enumerate(USER_MESSAGES):
            for rep in range(REPEATS):
                resp = client.messages.create(
                    model=MODEL,
                    max_tokens=300,
                    system=system,
                    messages=[{"role": "user", "content": msg}],
                )
                reply = "".join(b.text for b in resp.content if b.type == "text")
                checks = check_core(reply)
                rows.append({
                    "extra_rules": n_extra, "message": msg_idx, "repeat": rep,
                    **checks, "all_core": all(checks.values()),
                    "words": len(reply.split()),
                })
                print(f"load={n_extra:>2} msg={msg_idx} rep={rep} core={all(checks.values())}")

    out = os.path.join(os.path.dirname(__file__), "results.csv")
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("\nextra_rules  core_adherence  mean_words  stdev_words")
    for n_extra in LOAD_LEVELS:
        sub = [r for r in rows if r["extra_rules"] == n_extra]
        adherence = sum(r["all_core"] for r in sub) / len(sub)
        words = [r["words"] for r in sub]
        spread = statistics.pstdev(words) if len(words) > 1 else 0.0
        print(f"{n_extra:>11}  {adherence:>14.2f}  {statistics.mean(words):>10.1f}  {spread:>11.1f}")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
