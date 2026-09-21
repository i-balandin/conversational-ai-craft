"""A promptfoo provider that replays fixed transcripts instead of calling a model.

Why replay. The claim under test here is about the *evaluator*, not about any
model: a stage-gated criterion returns a vacuous pass when the conversation
never reached the stage. Holding the transcripts fixed is what isolates that.
It also means this suite runs in CI on every push with no API key and no cost.

promptfoo calls `call_api(prompt, options, context)` and expects a dict with
at least `output` or `error`.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRANSCRIPTS = os.path.join(ROOT, "examples", "false_pass", "transcripts.json")

with open(TRANSCRIPTS, encoding="utf-8") as fh:
    BY_ID = {t["id"]: t for t in json.load(fh)}


def call_api(prompt, options, context):
    transcript_id = (context or {}).get("vars", {}).get("transcript_id")
    if transcript_id not in BY_ID:
        return {"error": f"unknown transcript_id: {transcript_id!r}"}
    return {"output": json.dumps(BY_ID[transcript_id], ensure_ascii=False), "cached": True}
