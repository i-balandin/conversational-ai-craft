"""The prompt you read is not the prompt that ran: a modeled example (note #4).

The prompt in your repository is a template, and in most deployed systems the
template is *data*: a row in a database, versioned on its own schedule, put live
by an action that leaves no commit behind. The code that builds the variables
and the text that consumes them therefore have two different owners, and only
one of them is in version control.

When they disagree, instructions go missing in two directions, and neither
raises anything:

  dropped   the code supplies a variable the deployed template never names,
            so the value is built correctly and discarded before the model
            sees it
  empty     the template names a variable the code no longer supplies, so the
            placeholder resolves to an empty string

Three configurations of one assistant:

  in_repo    the template in the repository; every variable supplied
  deployed   an older published template that omits the two grounding blocks
  renamed    the repository template, but a refactor renamed a key upstream

The assistant is a MODEL, not a real LLM: with grounding it cites the grounded
fact, without grounding it produces a confident, plausible, invented one. That
is the behaviour worth modelling, because it is what makes the defect silent.
The part of this file that is not a model — and that you can lift — is
render_report(). No API key, no dependencies.

    python examples/render_drift/run_demo.py
"""
import re

# ------------------------------------------------- what the code declares

# The variables this prompt key is documented to provide. This list lives in
# the code, next to the builders that populate it.
DECLARED = ["account_history", "policy_excerpt", "user_message"]

CONTEXT = {
    "account_history": "Order #4471, delivered 3 March. Returned 9 March, refund pending.",
    "policy_excerpt": "Refunds are issued within 14 days of the return being received.",
}

# ------------------------------------------------------- the two templates

TEMPLATE_IN_REPO = """You are a support assistant for an online retailer.

Account history for this customer:
{{account_history}}

Relevant policy:
{{policy_excerpt}}

Answer the customer's question. Ground every claim in the two sections above.
If neither section supports an answer, say you need to check and do not guess.

Customer: {{user_message}}
"""

# The version actually published, months before the two grounding blocks were
# added to the copy in the repository. Nothing about it is malformed. It simply
# does not mention them, so they are discarded on every single turn.
TEMPLATE_DEPLOYED = """You are a support assistant for an online retailer.

Answer the customer's question in a professional tone.

Customer: {{user_message}}
"""

PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def render(template, context):
    """The ordinary, permissive render. A name with no value becomes empty."""
    return PLACEHOLDER.sub(lambda m: context.get(m.group(1), ""), template)


# ------------------------------------------------------ the liftable check

def render_report(declared, template, context):
    """Compare what the code declares, what the template names, and what has a value.

    Returns three lists:
        landed   declared, named by the template, and non-empty  -> reached the model
        dropped  declared and supplied, but the template never names it
        empty    named by the template, but nothing supplied a value

    Run this per turn in production and log the three. A non-empty `dropped` or
    `empty` is not automatically a bug, but a *change* in either is always
    something a person did, and it is the earliest signal you will get.

    Note what this does NOT do: it does not throw. See the note - when the
    defect may already be live, an assertion that fails the request takes the
    product down to tell you something a log line can tell you just as well.
    """
    named = set(PLACEHOLDER.findall(template))
    landed, dropped, empty = [], [], []
    for name in declared:
        supplied = bool(str(context.get(name, "")).strip())
        if name not in named:
            (dropped if supplied else empty).append(name)
        elif supplied:
            landed.append(name)
        else:
            empty.append(name)
    return landed, dropped, empty


# ---------------------------------------------------------- the assistant

GROUNDED = ("Your return on order #4471 was received on 9 March. "
            "Refunds go out within 14 days of receipt, so yours is due by 23 March.")
INVENTED = ("Your refund has been approved and should reach your account "
            "within 5 working days. Thanks for your patience.")


def assistant_reply(rendered):
    """Grounded only if the history text is present in what was actually rendered."""
    return GROUNDED if CONTEXT["account_history"] in rendered else INVENTED


# ------------------------------------------------------------ the rubric

HEDGE = re.compile(r"\b(I need to check|I'm not sure|I don't have|cannot confirm)\b", re.I)
SPECIFIC = re.compile(r"\b(#\d+|\d+ (?:March|April|working days|days))\b")


def answer_quality(reply):
    """A typical rubric: relevant, specific, confident, actionable.

    Every criterion here is one a real rubric would contain. Note what it has
    no way to ask: whether the answer was grounded in anything at all.
    """
    return all([
        "refund" in reply.lower(),
        bool(SPECIFIC.search(reply)),
        not HEDGE.search(reply),
        bool(re.search(r"\b(by|within)\b", reply, re.I)),
    ])


# ----------------------------------------------------------------- the run

TURNS = [
    "Where is my refund for the trainers I sent back?",
    "You said it was coming. How long now?",
    "Can you confirm the date?",
]

CONFIGS = [
    ("in_repo", TEMPLATE_IN_REPO, CONTEXT,
     "the template in the repository, every variable supplied"),
    ("deployed", TEMPLATE_DEPLOYED, CONTEXT,
     "an older published template that never names the grounding blocks"),
    ("renamed", TEMPLATE_IN_REPO,
     {"customer_history": CONTEXT["account_history"], "policy_excerpt": CONTEXT["policy_excerpt"]},
     "a refactor renamed account_history upstream; the template still asks for it"),
]


def main():
    print(__doc__.strip().split("\n\n")[0])
    print()

    for name, template, context, note in CONFIGS:
        ctx = dict(context, user_message=TURNS[0])
        landed, dropped, empty = render_report(DECLARED, template, ctx)

        print(f"=== {name} " + "=" * (56 - len(name)))
        print(f"  {note}")
        print(f"  landed  : {', '.join(landed) or '(none)'}")
        print(f"  DROPPED : {', '.join(dropped) or '(none)'}"
              f"{'   <- supplied, never named by the template' if dropped else ''}")
        print(f"  EMPTY   : {', '.join(empty) or '(none)'}"
              f"{'   <- named by the template, never supplied' if empty else ''}")
        print()

        passes = 0
        for turn in TURNS:
            reply = assistant_reply(render(template, dict(context, user_message=turn)))
            passes += answer_quality(reply)
        print(f"  sample reply    : {assistant_reply(render(template, ctx))}")
        print(f"  answer quality  : {passes}/{len(TURNS)} pass")
        print()

    print("=" * 62)
    print("Three configurations. One of them grounds its answers and two invent")
    print("them. The quality rubric scores all three the same, and no run raised")
    print("an error. The only thing that separates them is a report on what was")
    print("actually rendered - not on what the file in the repository says.")


if __name__ == "__main__":
    main()
