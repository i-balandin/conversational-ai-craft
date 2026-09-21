# Making prompt work auditable

*Ihor Balandin. A practice, not a claim.*

Prompt and evaluation work has an awkward property: when it succeeds, it disappears. A prompt change that removes a class of failure leaves no artefact behind — the failure simply stops happening, the team moves on, and six weeks later nobody can say which of the eleven things that changed that month was the one that mattered.

That is a problem for the work, not just for the person doing it. If you cannot point at what your analysis changed, you cannot tell a correct call from a lucky one, you cannot defend a decision that later looks odd, and you end up making the only claim available to you, which is "we improved quality" — a sentence that cannot be checked and therefore isn't worth much.

This is the artefact I keep to avoid that. It is simple and slightly tedious, which is most of why it works.

## The artefact

One table. One row per thing you proposed. Five columns:

| # | What I proposed | Where I proposed it | Status | Where it landed | Commit |
|---|---|---|---|---|---|
| A1 | Route the decision off a signal that is actually written, not off a field nothing populates | Analysis doc 1, finding 1 | ✅ implemented | `module/views.py:1511` | `90eaed0c` |
| Gate | Use the granular 1–5 scores as a real threshold instead of reading only the boolean | Analysis doc 2, fix 1 | ✅ implemented + hardened | `module/llm.py:44–98` | `90eaed0c` |
| BoN | Generate several candidates and keep the best, instead of shipping the first acceptable one | Analysis doc 2, fix 1 | ❌ open | still a single-candidate loop | — |
| Thr | Raise the gate threshold so a mediocre score stops shipping | Analysis doc 2 | ❌ deferred by design | gated behind evaluation | — |

That is the whole method. What makes it worth anything is four rules about how it is filled in.

## The four rules

**1. Verify against the code, not against the report.** Every row is checked against the actual branch that serves users, and the row cites a `file:line` anyone can open. Not against your own memory of the call, not against the status someone gave in a stand-up, and not against the ticket being marked done. A ticket closing and a behaviour changing are different events, and the gap between them is exactly what this table exists to measure.

**2. Name the commit you read.** `file:line` drifts the moment anyone touches the file. Commit IDs don't. State the branch and the commit you verified against, and say in the document that the line numbers will move. That single sentence is the difference between a durable record and one that quietly becomes wrong.

**3. The open rows are the load-bearing ones.** A table where everything is green reads as a sales document and gets discounted as one. The rows that say ❌ are what make the ✅ rows credible — and they are also the useful half, because they are the clean handoff if the work resumes. Distinguish two kinds of open honestly: *not done*, and *deliberately sequenced behind something else*. The second is not a miss, and calling it one is as inaccurate as calling it done.

**4. Separate what shipped from what was absorbed.** These are different and the second is stronger. A prompt change that ships is compliance: somebody applied your patch. Your reasoning turning up in *their* code comment, in their words, on a decision you were not in the room for — that is absorption, and it means the argument transferred rather than the instruction. Look for it specifically. In the one case where I found it, a strategic framing I had argued for in a positioning document appeared, months later, as a one-line comment explaining why a threshold had been left where it was.

## What it is good for, beyond the obvious

**A clean restart.** Engagements pause. When one resumes — and mine have — the next scope starts from a table of done / partial / open rather than from whoever remembers most confidently.

**Knowing whether the work was load-bearing.** The strongest signal I have come across is a proposal landing in production *after* the engagement had formally stopped. Nobody was performing for anybody at that point. If your findings get implemented when there is no longer a contract to justify it, they were real.

**Evidence that survives you leaving.** Instances are lost. Access is revoked, branches move, products get shut down. What survives is the record, and a record built on commit anchors is still checkable by someone who was never there.

## The honest limits

Most of the time the underlying code is private, which means the matrix itself cannot be published. So what goes in a public repository is the method — this page — while the filled-in table goes to the small number of people who can actually verify it, which is exactly the audience it is for.

It is also not a productivity metric and should not be turned into one. Counting rows rewards proposing many small things. The point of the table is traceability of a claim to an artefact, not volume.

And it measures whether your proposal was *implemented*, which is not the same as whether it was *right*. A shipped change with no evaluation behind it is still a guess — it has simply become a guess with better provenance. That is why the keystone row in the example above is the one that stayed deliberately un-shipped until an evaluation existed to judge it.

## How to start one

Keep it open while you work rather than reconstructing it at the end; reconstruction is when memory quietly replaces evidence. One line per proposal, written the day you make it, with the document and section you made it in. Then one verification pass at a natural boundary — end of a phase, a pause, a handoff — where you open the branch, check each row, and write the status you actually find, including the ones you would rather not.

The version of this that is worth having takes about an hour to fill in and is the only thing you will still be able to prove a year later.
