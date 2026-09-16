"""Silent retrieval failure: a modeled example (framework item 5).

An assistant connected to a knowledge base can retrieve nothing and still
answer fluently from general knowledge, while saying it used the company's
documents. A typical answer-quality check passes that answer. A grounding
check catches it.

This is a MODEL of the behaviour, not a real LLM: the "assistant" replies are
fixed strings that reproduce three patterns seen in practice. No API key, no
dependencies.

    python examples/silent_retrieval/run_demo.py
"""
import re

# --- fictional company knowledge base --------------------------------------
DOCS = {
    "leave-policy": "Employees receive 26 days of annual leave per calendar year. "
                    "Unused annual leave of up to 5 days can be carried over to March.",
    "expenses": "Travel expenses are reimbursed within 14 days after the claim "
                "is approved by the line manager.",
    "remote-work": "Staff may work remotely up to 3 days per week with manager agreement.",
}

STOPWORDS = {"how", "many", "do", "i", "get", "the", "a", "of", "is", "what",
             "can", "my", "per", "to", "for", "and", "in", "are", "we", "our"}


def tokens(text):
    return {w for w in re.findall(r"[a-z]+", text.lower()) if w not in STOPWORDS}


def retrieve(query, min_overlap=2):
    """Keyword retriever: returns ids of docs sharing enough words with the query."""
    q = tokens(query)
    return [doc_id for doc_id, text in DOCS.items() if len(q & tokens(text)) >= min_overlap]


# --- three cases: query + modeled assistant reply -------------------------
CASES = [
    {
        "id": "grounded",
        "query": "How many days of annual leave do employees receive?",
        "reply": "According to our leave policy, employees receive 26 days of annual "
                 "leave per year, and up to 5 unused days can be carried over to March.",
    },
    {
        "id": "silent_failure",
        # "vacation" instead of "annual leave": the retriever finds nothing,
        # the modeled assistant answers from general knowledge anyway.
        "query": "How much vacation time am I entitled to?",
        "reply": "According to our company policy documents, you are entitled to 20 "
                 "vacation days per year, plus public holidays.",
    },
    {
        "id": "honest_miss",
        "query": "What is the policy on parental leave?",
        "reply": "I couldn't find anything about parental leave in the company documents "
                 "I have access to. HR will be able to confirm the details.",
    },
]

ATTRIBUTION = re.compile(r"\b(according to our|our (company )?polic|the company documents say|"
                         r"our documents|per our policy)", re.IGNORECASE)
ADMITS_MISS = re.compile(r"\b(couldn't find|could not find|no information|not in the)", re.IGNORECASE)


# --- 1) typical answer-quality check ---------------------------------------
def naive_quality(reply):
    """Rewards a confident, specific, on-topic answer. Blind to grounding."""
    specific = re.search(r"\d", reply) is not None
    confident = ADMITS_MISS.search(reply) is None
    long_enough = len(reply.split()) >= 12
    return "PASS" if (specific and confident and long_enough) else "FAIL"


# --- 2) grounding check -----------------------------------------------------
def grounding(reply, retrieved_ids):
    """Fails when the reply claims documents it didn't get, or states numbers
    that aren't in the retrieved text. An honest 'not found' passes."""
    retrieved_text = " ".join(DOCS[d] for d in retrieved_ids)
    claims_docs = ATTRIBUTION.search(reply) is not None

    if not retrieved_ids:
        if claims_docs:
            return "FAIL", "claims company documents, but nothing was retrieved"
        if ADMITS_MISS.search(reply):
            return "PASS", "nothing retrieved and says so"
        return "FAIL", "nothing retrieved, answers anyway"

    unsupported = [n for n in re.findall(r"\d+", reply) if n not in retrieved_text]
    if unsupported:
        return "FAIL", f"numbers not in retrieved text: {', '.join(unsupported)}"
    return "PASS", "claims supported by retrieved text"


def main():
    print(f"{'case':<16}{'retrieved':<18}{'answer-quality':>15}{'grounding':>11}")
    print("-" * 60)
    hits = 0
    rows = []
    for c in CASES:
        ids = retrieve(c["query"])
        hits += bool(ids)
        q = naive_quality(c["reply"])
        g, why = grounding(c["reply"], ids)
        rows.append((c["id"], why))
        print(f"{c['id']:<16}{(', '.join(ids) or 'nothing'):<18}{q:>15}{g:>11}")

    print(f"\nRetrieval hit rate: {hits}/{len(CASES)}  <- report this next to any quality score")
    print("\nWhy the grounding check decided:")
    for case_id, why in rows:
        print(f"  {case_id:<16}{why}")
    print(
        "\nRead it top to bottom:\n"
        "  grounded       -> both checks pass\n"
        "  silent_failure -> answer-quality PASSES a fluent answer built on nothing;\n"
        "                    grounding catches it\n"
        "  honest_miss    -> answer-quality FAILS the only honest reply;\n"
        "                    grounding passes it\n"
        "The quality check rewards the wrong behaviour in both failure cases."
    )


if __name__ == "__main__":
    main()
