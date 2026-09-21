"""Style markers, side by side: a TOOL, not a demonstration (note #7).

Everything else under examples/ argues something. This one argues nothing. It
is the measuring stick note #7 asks for: given two transcripts of the same kind
of conversation, it prints surface markers for the assistant's side of each and
the gap between them.

The intended use is your own two files - one from the assistant you built, one
held out from the practice you were asked to reproduce - so that "it doesn't
quite sound like me" becomes something with numbers attached instead of a
feeling nobody can act on.

The two transcripts bundled here are synthetic and exist only so the script has
something to run on out of the box:

    python examples/style_markers/run_demo.py
    python examples/style_markers/run_demo.py mine.json theirs.json

Transcript format is the one used elsewhere in this repository: a JSON object
with "turns", each {"role": "assistant"|"user", "text": "..."}.

**What this cannot tell you.** These are surface features. Two transcripts can
agree on every number here and still not sound like the same person, because
what makes a practice recognisable is partly in choices these markers do not
see - which thread gets followed, what gets left alone, when a silence is
allowed to stand. Agreement on the markers is necessary, not sufficient. Treat
a gap as a question to go and look at, never as a score.

The bundled pair demonstrates that limit against itself. Transcript B is
plainly the more directive of the two - it offers a frame, tells the person to
write three things down, and says which question is bigger than today - and the
"turns with a directive phrase" marker scores both at zero, because none of it
is phrased as "you should". A marker built from phrasings catches the phrasings
it was built from. That is the honest condition of every list of markers,
including this one, and the reason the output tells you to go and read.
"""
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

DIRECTIVE = re.compile(
    r"\b(you should|you need to|i recommend|i suggest|make sure|the key is|"
    r"what you want to do|i'd advise|you have to|the answer is)\b", re.I)
HEDGE = re.compile(
    r"\b(perhaps|maybe|it might be|i wonder|possibly|it may|could be|"
    r"i'm not sure|somewhat|a little)\b", re.I)
FIRST_PERSON = re.compile(r"\b(i|i'm|i'd|i've|my|me)\b", re.I)
SECOND_PERSON = re.compile(r"\b(you|you're|your|you've|yourself)\b", re.I)


def load(path):
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return data["turns"] if isinstance(data, dict) else data


def assistant_turns(turns):
    return [t["text"] for t in turns if t.get("role") == "assistant"]


def rate(pattern, texts):
    """Turns containing at least one match, as a share of turns."""
    if not texts:
        return 0.0
    return sum(bool(pattern.search(t)) for t in texts) / len(texts)


def markers(texts):
    if not texts:
        return {}
    words = [len(t.split()) for t in texts]
    all_words = [w.lower().strip(".,!?;:\"'") for t in texts for w in t.split()]
    sentences = [max(1, len(re.findall(r"[.!?](?:\s|$)", t))) for t in texts]
    return {
        "assistant turns": len(texts),
        "words per turn (mean)": statistics.mean(words),
        "words per turn (median)": statistics.median(words),
        "words per turn (spread)": statistics.pstdev(words) if len(words) > 1 else 0.0,
        "sentences per turn": statistics.mean(sentences),
        "turns ending on a question": sum(t.rstrip().endswith("?") for t in texts) / len(texts),
        "questions per turn": statistics.mean(t.count("?") for t in texts),
        "turns with a directive phrase": rate(DIRECTIVE, texts),
        "turns with a hedge": rate(HEDGE, texts),
        "turns referring to themselves": rate(FIRST_PERSON, texts),
        "turns addressing the person": rate(SECOND_PERSON, texts),
        "vocabulary variety (type/token)": len(set(all_words)) / max(1, len(all_words)),
    }


def distinctive(a_texts, b_texts, n=6):
    """Words much commoner on one side than the other. Crude and useful."""
    def freq(texts):
        ws = [w.lower().strip(".,!?;:\"'") for t in texts for w in t.split()]
        ws = [w for w in ws if len(w) > 3]
        total = max(1, len(ws))
        out = {}
        for w in ws:
            out[w] = out.get(w, 0) + 1 / total
        return out

    fa, fb = freq(a_texts), freq(b_texts)
    keys = set(fa) | set(fb)
    scored = sorted(keys, key=lambda w: fa.get(w, 0) - fb.get(w, 0))
    return scored[-n:][::-1], scored[:n]


def main(a_path=None, b_path=None):
    a_path = a_path or os.path.join(HERE, "transcript-a-described.json")
    b_path = b_path or os.path.join(HERE, "transcript-b-observed.json")

    a = assistant_turns(load(a_path))
    b = assistant_turns(load(b_path))
    ma, mb = markers(a), markers(b)

    label_a = os.path.basename(a_path)
    label_b = os.path.basename(b_path)

    print("Style markers, assistant side only\n")
    print(f"  A = {label_a}")
    print(f"  B = {label_b}\n")
    print(f"  {'marker':<34}{'A':>10}{'B':>10}{'gap':>10}")
    print("  " + "-" * 64)
    for key in ma:
        va, vb = ma[key], mb.get(key, 0)
        fmt = "{:>10.0f}" if key == "assistant turns" else "{:>10.2f}"
        gap = ("{:>+10.2f}".format(vb - va) if key != "assistant turns"
               else "{:>+10.0f}".format(vb - va))
        print("  " + f"{key:<34}" + fmt.format(va) + fmt.format(vb) + gap)

    more_a, more_b = distinctive(a, b)
    print()
    print(f"  words much commoner in A: {', '.join(more_a)}")
    print(f"  words much commoner in B: {', '.join(more_b)}")
    print()
    print("  A gap is a place to go and read the transcripts, not a verdict.")
    print("  These are surface features; see the header of this file for what")
    print("  they cannot see.")


if __name__ == "__main__":
    main(*sys.argv[1:3])
