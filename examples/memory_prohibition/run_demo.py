"""A preference can live in memory, a prohibition can't: a modeled example (note #6).

An assistant with memory writes things about the user into a store, and later
retrieves the ones that look relevant to the current turn. That works for
preferences. Put a prohibition in the same store and two things happen that a
success-rate figure will not show you.

  paraphrase   the extraction step is a summariser. Summarisers keep content
               and lose negation, scope and conditionality - so a rule can come
               back out meaning something else, sometimes its opposite
  oblique      retrieval fires on resemblance to the current turn, and the
               turns where a prohibition matters most are often the ones that
               do not resemble it

Both are modeled here: the extractor and the retriever are a few lines each and
do exactly what the note describes. The point is not the hit rate this prints -
that is a property of my fixture. The point is that the memory-backed rule has
two failure modes the in-prompt rule does not have at all.

No API key, no dependencies.

    python examples/memory_prohibition/run_demo.py
"""
import re

# What the user actually said, in one turn, early on.
USER_STATEMENT = ("Please don't bring up the redundancy at my last job again, "
                  "and definitely not when my team is in the room.")

# ---------------------------------------------------------- the store writes

def extract(statement):
    """A summariser turning a turn into a memory entry.

    Deliberately ordinary: it keeps the topic, drops the negation and drops the
    condition. That is what summarisers do, and it is the whole mechanism -
    nothing here is a strawman of a badly built pipeline.
    """
    topic = re.search(r"(the [a-z ]+? at my last job|the [a-z]+)", statement)
    topic = topic.group(1) if topic else "an unnamed topic"
    return {
        "kind": "fact",                       # the store has no category for a rule
        "text": f"User is sensitive about {topic}.",
        "source_turn": 1,
    }


def extract_preference(statement):
    """The same summariser on a preference, for contrast."""
    return {"kind": "preference", "text": "User prefers short replies.", "source_turn": 1}


# ------------------------------------------------------- the store retrieves

# Function words only. Nothing topical goes in here: stripping the words the
# rule and the turn actually share would rig the result, and the honest result
# is more interesting than the rigged one.
STOPWORDS = {
    "a", "an", "the", "my", "your", "this", "that", "these", "those",
    "i", "we", "you", "it", "he", "she", "they", "me", "us", "them",
    "is", "are", "was", "were", "be", "been", "am", "do", "does", "did",
    "can", "could", "should", "would", "will", "shall", "may", "might",
    "and", "or", "but", "if", "so", "than", "then", "as", "because",
    "at", "in", "on", "of", "to", "for", "with", "about", "from", "by",
    "what", "when", "where", "how", "why", "who", "which",
    "not", "no", "please", "just", "up", "out", "again",
}


def words(text):
    return {w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOPWORDS}


def retrieve(entry, turn, threshold=1):
    """Similarity retrieval, modeled as shared content words.

    A real store uses embeddings, which are better at this than word overlap -
    but better at the same job, and the job is resemblance to the current turn.
    An approach that shares no content with the rule is hard for either.
    """
    return len(words(entry["text"]) & words(turn)) >= threshold


# ------------------------------------------------------------- the fixture

# Later turns. Each one either approaches the forbidden topic or doesn't, and
# for the approaches I have marked whether the resemblance is direct or oblique.
TURNS = [
    ("Can we talk about what happened at my last job?", "approach", "direct"),
    ("How are things going with the team this week?", "approach", "oblique"),
    ("I keep thinking about why I left.", "approach", "oblique"),
    ("What should I focus on in the next quarter?", "unrelated", None),
    ("My manager asked about the gap on my CV in front of everyone.", "approach", "oblique"),
]


def in_prompt_rule_fires(_turn):
    """An always-present instruction is in context on every turn, by construction."""
    return True


def main():
    print(__doc__.strip().split("\n\n")[0])
    print()
    print(f'User, turn 1: "{USER_STATEMENT}"')
    print()

    entry = extract(USER_STATEMENT)
    print("What the store now holds:")
    print(f'  kind : {entry["kind"]}')
    print(f'  text : "{entry["text"]}"')
    print()
    print("  Read that back against what the user said. The topic survived. The")
    print("  word 'don't' did not, and neither did the condition about the team.")
    print("  A later turn can read this entry as a subject to raise.")
    print()

    approaches = [(t, why) for t, kind, why in TURNS if kind == "approach"]
    print("=== does the rule reach the model on the turn where it matters? ===")
    print(f"  {'turn':<58}{'memory':>9}{'in prompt':>11}")
    mem_hits = 0
    for turn, kind, why in TURNS:
        got = retrieve(entry, turn)
        mem_hits += got and kind == "approach"
        tag = f"  {turn[:54]:<58}"
        print(tag + f"{'yes' if got else 'NO':>9}{'yes':>11}"
              + ("" if kind == "approach" else "   (unrelated turn)"))
    print()
    print(f"  approaches where the memory rule was retrieved : {mem_hits}/{len(approaches)}")
    print(f"  approaches where an in-prompt rule was present : {len(approaches)}/{len(approaches)}")
    print()
    direct = [w for _t, k, w in TURNS if k == "approach"].count("direct")
    print(f"  Look at which one it caught. The {direct} direct approach names the topic,")
    print("  so it resembles the stored entry and comes back. The oblique ones -")
    print("  the team, why I left, the gap on the CV - are the turns where a")
    print("  person walks up to the subject without naming it, and they are the")
    print("  turns a rule like this exists for. Retrieval works best exactly")
    print("  where you needed it least.")
    print()

    print("=== the same store, holding a preference ===")
    pref = extract_preference(USER_STATEMENT)
    print(f'  text : "{pref["text"]}"')
    print("  Not retrieved on a given turn? The reply is a bit longer than the")
    print("  user would like. Next turn is a fresh chance, and nothing is lost.")
    print()

    print("=" * 62)
    print("This is the asymmetry. For a preference, each miss costs a little and")
    print("the misses are independent. For a prohibition, one miss is the entire")
    print("harm, and the user does not experience it as a glitch.")
    print()
    print("So it is not a reliability percentage you can improve your way out of.")
    print("Raising retrieval recall helps a preference in proportion; for a rule")
    print("whose single failure is unacceptable, the substrate is wrong, not the")
    print("tuning. And note what the in-prompt column is NOT claiming: an")
    print("always-present instruction can still be disobeyed. It differs in")
    print("degree, not in kind. What memory adds is a SECOND, independent failure")
    print("- never retrieved, or retrieved as a paraphrase that inverted it - on")
    print("top of the one the prompt already has. That second one is avoidable.")


if __name__ == "__main__":
    main()
