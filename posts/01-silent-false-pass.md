# Your AI pilot passed. That doesn't mean it works.

*Conversational Eval Notes #1. Ihor Balandin.*

When a team rolls an AI assistant out beyond a pilot, the decision usually rests on one thing: the evaluation came back green. That's the moment the risk is highest, because a green evaluation of a conversational assistant can be wrong in a way nobody sees.

This note is about one specific way that happens, why it's easy to miss, and a small fix. There's a runnable example at the end.

## The known half

Most people who evaluate chat assistants have already learned the first lesson: scoring each reply on its own misses problems that only show up across the conversation. A reply can be polite, accurate and on-brand while the conversation as a whole goes nowhere. The assistant wraps up before it understood what the person wanted. It forgets something from three turns back. It moves past "I'm not really okay" as if it wasn't said.

The main eval tools now recommend scoring at conversation level as well as per turn, so I won't spend long on this. It's real, it's common, and it's the part most teams already know.

## The half that stays hidden

The second problem is quieter, and it's the one that cost me the most.

To score whole conversations, teams write checks tied to stages of the conversation. "Did the assistant confirm the goal before closing?" "Did it summarize at the end?" These are usually yes/no checks, and they quietly assume every conversation runs the full course: opening, middle, close.

Test conversations don't do that. They end early. They branch. The user leaves halfway. So the check gets asked about a stage that never happened, and it still has to answer yes or no.

Sometimes it says no, and a perfectly reasonable conversation gets marked as a failure. Annoying, but at least someone looks at it.

The worse case is when it says yes. The check was written to catch a bad close. The conversation never reached a close, so there's nothing bad to catch, and it passes. Multiply that across a test set and you get a score that looks healthy precisely because the conversations didn't get far enough to fail. Nothing errors. Nothing stands out. The average just looks good.

I call this a silent false-pass. It's the dangerous kind, because it produces exactly the evidence a team needs to say "ready".

**It also has an older and much better-documented name.** In formal verification a specification can pass *vacuously* — an implication that holds trivially because its precondition was never satisfied. It has been studied since the 1990s under the names vacuity and antecedent failure, and the findings there transfer almost word for word. Beer and colleagues report that typically one specification in five passes vacuously during the first formal-verification runs of a new hardware design, and — the part worth sitting with — that a vacuous pass *always* points at a real problem, in the design, the specification or the environment. It is never just noise.

So the phenomenon is not new, and I am not going to pretend it is. My addition is that conversation-level evaluation reproduces it exactly, that the unsatisfied precondition here is a stage of the conversation that the test never reached, and that the remedy has to do something formal verification does not need to: report how far the conversations got, because in our setting the precondition failing is itself the finding.

## Why this matters beyond the eval team

If you're responsible for getting an AI assistant adopted, the evaluation is how you earn the right to put it in front of more people. A silent false-pass means that right was granted on a number that didn't measure what everyone assumed. The failures don't go away. They show up later, in front of real users, where they cost trust instead of a test run.

So the question to ask of any green dashboard isn't only "what's the score?" It's "how many of these conversations actually reached the part we were checking?"

## The fix is small

Give stage checks three answers instead of two: pass, fail, or not applicable. If the conversation never reached the stage, the check says N/A, and N/A is left out of the score. It doesn't count as a pass and it doesn't count as a fail.

That one change does two things. It stops good-but-short conversations from being punished, and it stops unfinished ones from quietly inflating the result. It also gives you a number worth reporting on its own: what share of conversations reached each stage. If most of your test set never gets to the close, your "closing quality" score rests on very little, and now you can see that.

Three habits make the fix hold:

- **Score the conversation as well as the turns.** Use checks that look at the whole arc: was a goal set and used, did it close too early, was a distress signal handled.
- **Check your judge against people.** If an AI model grades the conversations, label a small set yourself and report how often it agrees with you, next to the score. Judges also get less reliable as conversations get longer, which is one more reason to check.
- **Don't confirm a fix with the test that missed the problem.** Add the failing conversation as a test case first, then fix it.

## See it happen

The repository with this note has a small example: three made-up coaching-style conversations (one that looks fine but isn't, one cut off halfway, one clean), a naive yes/no evaluation, and a version with not-applicable checks. No API key, no dependencies.

The naive version gives the broken conversation a perfect score. The stage-aware version fails it, and stops penalizing the one that was cut off. Same conversations, opposite conclusions.

```
python examples/false_pass/run_demo.py
```

## What I'm claiming, and what I'm not

Some of this came from work on one particular platform, and one product's quirks aren't a general rule. So my test is whether the effect shows up in a plain setup that has nothing to do with that platform. It does: both problems appear in about a hundred lines of code with no special infrastructure.

Neither half is new. Scoring whole conversations is standard advice by now, and the silent pass is vacuity, which hardware verification has been detecting and measuring for twenty-five years. That's a good thing to know rather than a disappointment: a field with that much more experience of the same failure can tell you something I couldn't, namely that a vacuous pass is never benign.

The transfer is the part worth writing down. Conversation-level evaluation has the same structure and almost none of the same hygiene; the precondition that fails here is a stage a test conversation never reached; and the remedy needs one thing verification doesn't, which is a reported stage-reach rate, because how far the conversations got is itself a result. If someone has already made that transfer in writing, I'd genuinely like to read it.

## Next

Next note: why adding more rules to make an assistant specific usually makes it harder to control, and where that specificity should live instead.
