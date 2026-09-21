# A preference can live in memory. A prohibition can't.

*Conversational Eval Notes #6. Ihor Balandin.*

Memory is the feature everyone is adding. The pitch is that the assistant remembers you: your goals, your situation, how you like to be spoken to. It mostly works, and when it doesn't the cost is small — a reply slightly longer than you'd have chosen, a goal not referred back to.

Then someone puts a boundary in it. *Don't bring up the redundancy again.* It looks like exactly the same kind of thing: a durable fact about the user, stated once, wanted forever. The store cannot tell the difference, and the difference is the whole of this note.

## The known part

Two pieces of this are settled and I'm not going to argue them.

Retrieval-backed memory returns a bounded subset selected by similarity to the current turn. That's how it works and it's a reasonable design — you cannot put everything you know about a user in front of the model on every turn.

And the guardrails community already knows that a constraint which must hold belongs in a layer that doesn't depend on the model's cooperation: a deterministic filter, a policy model, a check outside the generator. That argument is made and won.

What has not caught up is that **memory is a new place people are putting rules**, and the distinction between a preference and a prohibition is not one the store makes, asks about, or exposes.

## Two things go wrong, and neither shows up in a recall figure

**The extraction step drops the negation.** A memory pipeline is a summariser. It reads a conversation and writes facts and preferences, and summarisers are optimised to keep content. Negation, scope and conditionality are exactly what they shed. So:

> *"Please don't bring up the redundancy at my last job again, and definitely not when my team is in the room."*

goes in, and what comes out is something like *"User is sensitive about the redundancy at their last job."* The topic survived. The word "don't" didn't, and neither did the condition about the team.

Read that entry the way a model will read it on a later turn. It is no longer a rule. It is a **topic marked as significant** — which, to an assistant trying to be attentive, reads like something to ask about. The rule didn't fail to fire. It was rewritten into an invitation.

**Retrieval fires on resemblance, and the dangerous turns don't resemble.** A prohibition earns its keep at the moment a conversation approaches the subject. People approach subjects obliquely. "How are things with the team?" "I keep thinking about why I left." "My manager asked about the gap on my CV." None of those look like the stored entry, so none of them retrieve it.

What does retrieve it is the turn where the person names the topic outright — the one occasion you would have noticed anyway. **The retrieval works best exactly where you needed it least.**

## The asymmetry

Put those together and the point isn't that memory is unreliable. It's that reliability means different things for the two objects you've filed in it.

A **preference** that fails to surface costs a little quality, the misses are independent, and the next turn is a fresh chance. Recall of 85% buys you roughly 85% of the value. The relationship is linear and forgiving.

A **prohibition** that fails to surface *is the harm.* There is no partial credit. One miss is the entire event, it is not recoverable on the next turn, and the user does not experience it as a glitch — they experience it as being ignored on the one thing they explicitly asked for. The cost sits entirely in the tail, and the tail is where the damage is.

So the question to ask of a memory entry is not "how often will this be retrieved?" It is: **what happens the one time it isn't?** If the answer is "the reply is a bit off", memory is the right place. If the answer is a harm, you are not looking at a memory item, whatever it looks like in the store.

## What I am not claiming

An always-present instruction in the prompt is **also** probabilistic. The model can read "never raise this topic" and raise it anyway; note #2 is partly about how that gets worse as the rule list grows, and note #5 is about how a judge then mis-scores it. In-prompt is not a guarantee, and I'd be overselling it if I implied otherwise.

The difference is not kind, it's the number of independent ways to fail. An in-prompt rule can be disobeyed. A memory-backed rule can be **disobeyed, or never retrieved, or retrieved as a paraphrase that inverted it** — three failure modes where the first had one, and the two extra ones are avoidable at no cost. That is the whole argument, and it doesn't need the prompt to be perfect to hold.

It also means this is a design rule rather than a measurement, so here is the measurement that would settle it: take one prohibition, a set of approach turns including oblique ones, and compare how often the rule reaches the model from memory versus from the prompt — and read the extracted entry to see whether it still says what the user said. If the memory-backed version reaches the model as reliably as the in-prompt one across oblique approaches, I'm wrong.

## What to do instead

**Prohibitions go where they are unconditional.** In the always-present part of the prompt, or — better, for anything with real consequences — in a check outside the model that doesn't care whether the model cooperated. This is the same argument as note #3's shared floor, arriving at a second substrate: a constraint whose violation is unacceptable must not be sited anywhere conditional, and "retrieved by similarity" is conditional.

**If the product needs a user-settable "never again", build it as a flag, not a sentence.** A field on the user or conversation record, read on every turn, with an explicit lifetime and a way for the user to see and undo it. That is a small feature. It is not the same feature as memory, and using memory for it because memory already exists is how this happens.

**Don't let the summariser be the only writer of anything you'd call a rule.** A paraphrase of a prohibition is not a prohibition. If a store must hold them, the rule text goes in verbatim and unparaphrased, with a type, and the retrieval for that type is unconditional rather than similarity-gated.

**And check the extraction, not just the recall.** Read what your pipeline actually wrote for a handful of boundary statements. It takes ten minutes and it is the part nobody looks at, because the store reports what it retrieved, never what it understood.

## See it happen

The repository has a small example: one boundary stated by a user, the entry a summariser writes from it, and five later turns — one direct approach and three oblique ones, plus an unrelated turn.

The memory-backed rule reaches the model on one of the four approaches. The in-prompt rule is present on all four. And the entry printed at the top has lost the negation, which is the part worth looking at longest.

```
python examples/memory_prohibition/run_demo.py
```

Read it as a diagram, not a measurement. The extractor and the retriever are a few lines of Python each, doing exactly what the note describes, and the turns are ones I wrote — so the 1-in-4 is a property of my fixture and not a rate anybody observed. What the fixture can show honestly is the *shape*: which kinds of turn retrieve and which don't, and what a summariser does to a sentence containing "don't".

## What I'm claiming, and what I'm not

I'm not claiming that retrieval-based memory is badly designed, that summarisers being lossy is news, or that safety constraints belong outside the model — that last one is established practice and I'm leaning on it rather than proposing it.

My claim is the asymmetry, plus the fact that the store is where it goes missing: preferences degrade gracefully and prohibitions do not, the two are indistinguishable to a memory pipeline, and the pipeline's two extra failure modes land entirely on the object that can't absorb them. Plus the consequence for design — that "never mention X again" is not a memory feature, and the ten-minute check that shows you what your extraction step did to the sentence.

**On evidence.** This came out of establishing what a cross-bot memory layer could and couldn't be asked to do on one platform: real memory, scoped per user and project, holding goals and commitments, with entries written by asynchronous extraction and fetched by a similarity search the model chooses to call. There was no boundary category, and a prohibition stored as a fact behaved the way this note describes. One platform, one investigation, no counts — and the design rule is the part I'd defend, not a number.

If you've seen the preference/prohibition distinction made in a memory architecture, I'd genuinely like to read it. My impression from looking is that the literature treats both as the same object stored in the same place, which is itself the evidence that the distinction isn't being made.

## Next

Next note: why the specification a practitioner writes about their own method is sometimes exactly right, sometimes a description of the practice they intend, and why sign-off can't tell you which one you got.
