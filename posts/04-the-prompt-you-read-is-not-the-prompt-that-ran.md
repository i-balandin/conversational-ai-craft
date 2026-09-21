# The prompt you read is not the prompt that ran

*Conversational Eval Notes #4. Ihor Balandin.*

You change a prompt to fix a behaviour. The behaviour doesn't change. So you rewrite the instruction more forcefully. Still nothing. You move it, split it, give it an example, put it in capitals. By the fourth attempt you have a working theory: this model just doesn't follow that kind of instruction.

Sometimes that theory is right. Often the instruction was never in the prompt.

This note is about the gap between the prompt in your repository and the string the model actually received, why that gap is silent in both directions, and the one report that closes it.

## The known part

Nobody thinks the file is sent verbatim. Prompts are templates with variables, something assembles them at runtime, and prompt registries, versioning and tracing all exist and are well covered. If you run a mature LLM stack you already log requests somewhere.

So the mechanism isn't the contribution. What I want to argue is narrower: that this defect has a shape which makes it survive far longer than its difficulty deserves, and that the habit which prevents it is cheaper than the observability platform people postpone it to.

## The template is data, not code

Start with the thing that makes this different from an ordinary bug.

In most deployed systems the prompt text is not a constant in the source. It is a row in a database, edited through an authoring tool, versioned on its own schedule, and put live by an action that leaves no commit behind. Meanwhile the code that *builds the variables* — retrieves the documents, assembles the session context, formats the available options — lives in the repository and moves with your releases.

So "the prompt" has two owners moving at different speeds, and **only one of them is in version control.** Everything below follows from that.

## Two directions, both silent

When the two halves disagree, instructions go missing in one of two ways, and neither raises anything.

**Dropped.** The code supplies a variable the deployed template never names. Your retrieval runs, the documents come back, the context block is assembled correctly — and then the renderer has nowhere to put it, so it discards it. Handlebars and most of its relatives do exactly this: a value with no matching placeholder is not an error, it is simply unused.

**Empty.** The template names a variable the code no longer supplies, usually because someone renamed a key or removed the path that populated it. The placeholder resolves to an empty string. Also not an error.

The first is the one that surprises people, because every instinct says the risk runs the other way. You check that your retrieval works. You check that the context is built. Both are fine. The part nobody checks is whether the text that was supposed to consume them still mentions them.

Two more variants of the same shape are worth naming, because they are what "which prompt ran?" actually means in practice: the authoring tool tests the **draft** while users are served the **published** version, and the branch you read locally is not the branch that serves.

## The failure teaches the wrong lesson

A missing section produces no error, no latency change, no crash, and no obvious drop in fluency. The assistant keeps answering. It just answers from less, so it becomes more generic — and when a model has nothing to ground a specific claim in, it does not usually say so. It produces a plausible one.

That is the part that should worry an evaluation team. Run a normal answer-quality rubric over those turns — relevant, specific, confident, actionable — and every criterion passes. The rubric has no channel through which to ask whether the answer was grounded in anything, because grounding was supposed to be guaranteed upstream. So the dashboard is green while the answers are invented.

Meanwhile the human response to "my fix didn't take" is to write a better instruction. Each rewrite fails, and each failure is logged in someone's memory as evidence *about the model*. I have watched a team accumulate a sincere and entirely false belief that a category of instruction "doesn't work on this platform", built on a stack of experiments in which the instruction was not present. The cost isn't the defect. It's the theory the defect trains you into.

## It isn't only variables

The same gap swallows prose.

If the template carries a paragraph of standing instructions — a tone rule, a prohibition, a safety line — that paragraph is also template text, living in the same separately-versioned row. A fix written into the copy in your repository and never republished is simply not in the system, and it looks exactly like a fix that was applied and didn't work.

This is worth stating because it breaks the mental model that makes the defect feel small. "A variable didn't render" sounds like a formatting issue. "An entire section of our instructions has not been in production since March" is the same event.

## The fix is a report, not an assertion

**Log, for every turn, three sets: what the code declared, what the template names, and what actually carried a value.** The difference between them is the whole finding.

```python
named   = placeholders_in(template)
dropped = [n for n in declared if n not in named and supplied(n)]
empty   = [n for n in declared if n in named and not supplied(n)]
```

Log `dropped` and `empty`. A non-empty set is not automatically a bug — plenty of blocks are legitimately absent on a given turn — but **a change in either set is always something a person did**, and it is the earliest and cheapest signal you will get.

Two details decide whether this works in practice.

**Parse the template; don't grep it.** A regex over `{{...}}` will count a mention inside a comment — `{{! account_history removed for now }}` — as the variable being present. That is the one direction the error must never fall, because a false "present" hides exactly the defect you built the check for. Parse the template and ask its syntax tree; let it err toward reporting a variable missing when it isn't, never the reverse.

**Log it; do not throw.** The temptation is to make this a hard assertion at startup. Resist it, for a specific reason: by the time you write this check, the defect is often already live. An assertion that fails the request would take the product down to tell you something a log line tells you just as well, and taking the product down is not the same as fixing it — the fix is republishing the template. Fail open, shout loudly, and let a human act. This is one of the few places where I think the usual "fail closed" instinct is wrong, and it is wrong because the check is *diagnostic*, not a safety control.

Three questions follow from it:

- **Before you rewrite an instruction that didn't take:** was it in the rendered prompt? If you can't answer from a log, the rewrite isn't an experiment, it's a guess with a clean shirt on.
- **Before you quote an evaluation result:** which rendered prompt produced it? A score inherits whatever was missing that day.
- **Before you tell anyone a behaviour is fixed:** which artefact is serving users — the draft, the published version, the row in the table, the branch? Name it.

The general rule, and the only sentence here I would keep if I had to drop the rest: **never evaluate against the file.** Evaluate against the render.

## See it happen

The repository has a small example: one set of declared variables, three configurations — the template from the repository, an older published template that never names the two grounding blocks, and a renamed key upstream. The assistant is a model, not a real LLM: grounded, it cites the grounded fact; ungrounded, it invents a confident one, which is the behaviour that makes this silent.

All three score 3 of 3 on the answer-quality rubric. The render report separates them in one line each, and names which block went missing and in which direction.

```
python examples/render_drift/run_demo.py
```

As with the example in note #3, read it as a diagram rather than a measurement: the fixture is mine and it executes an argument. The one part of that file that is not a model is `render_report()`, which is the check itself and which you can lift in about five minutes.

## What I'm claiming, and what I'm not

I'm not claiming that prompt templating, configuration drift or LLM observability are new problems, and I'm not claiming a renderer that discards an unused value is a bug. It is sensible behaviour, and so is filling an unmatched placeholder with nothing.

It is the stack of them that does the damage. A template that is data rather than code, a renderer that stays quiet in both directions, and a quality rubric with no way to ask about grounding: together they produce a defect that is **invisible to the instrument most teams are pointing at it**, that looks exactly like a model limitation, and that therefore gets answered with more prompt rewrites. You don't need an observability platform to catch that. You need three lines of logging, and the discipline not to call a rewrite an experiment until you've looked at what actually rendered.

**On evidence.** I have watched this run undetected in production. Two blocks the code assembled on every conversation — a retrieved-knowledge section and a session-context section — were absent from the deployed template, and therefore from every prompt the model saw, for **almost six months**: from 12 March 2026 until at least 2 September 2026, when the check described above was written. It was still live on that date, and the fix is republishing the template, so the code cannot tell me when — or whether — that happened. Hence "almost six months, and at least that", rather than a tidier figure.

The detail I find most useful is what it took to see it at all. Nothing in the system could report it, and nothing in version control could show it either — the change that broke it was a template publication, so there is no commit on that date to find. Almost six months of every conversation, and the artefact that caused it left no trace in the history anyone would think to read.

That is one case, at one company. Treat this note as one observation plus a mechanism you can check on your own system this afternoon.

If you have seen this class of failure written up, particularly the dropped direction or the interaction with answer-quality rubrics, I would like to read it.

## How this connects to the other notes

Note #1 is about an evaluation that passes because the conversation never reached the stage being checked. This one is about an evaluation that passes because the instruction never reached the model. They are the same species: the instrument reports on something that was not there, and reports it as fine. The unwritten note on silent retrieval is the third member of the family — and in the case above, the two were the same event, since what went missing was the retrieval block itself.

## Next

Next note: the judge that reads the policy it is marking against, and what that does to every criterion in the rubric.
