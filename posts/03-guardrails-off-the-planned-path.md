# Your guardrail passed the test. The user didn't follow the test.

*Conversational Eval Notes #3. Ihor Balandin.*

Safety checks for conversational assistants are usually written along the path the conversation is supposed to take. The test goes: introduction, goal, exploration, close, and somewhere in the middle the test user says something that should trigger a safeguard. The safeguard fires. The test passes.

Real users don't follow that path. They say the important thing in the first message, or at the very end, or while the assistant is still asking for their goal. This note is about what happens to guardrails then, and why the fix is partly architectural.

## The known part

Testing assistants for safety is standard practice, and so is adversarial testing: people deliberately trying to push an assistant into saying something it shouldn't, sometimes gradually over many turns. That work matters and I won't repeat it.

The case here is different and more ordinary. Nobody is attacking anything. A person simply says "I'm not okay" at a moment the designers didn't plan for.

## Where the leak comes from

In note #2 I argued that instructions should live in the stage of the conversation where they apply, so the model sees a few relevant rules at a time instead of all of them. That helps control. It also creates a specific risk.

If a safety rule is placed inside one stage, it only exists in that stage. Say the rule "if the person signals distress, stop and check in" sits in the exploration stage, because that's where the test script expects difficult things to come up. Then:

- A person who discloses distress in their first message is in the introduction stage. The rule isn't active there.
- A person who can't name a goal and says they can't cope is in the goal stage. Not active there either.
- A person who says how they really feel while the assistant is wrapping up is in the closing stage. Same.

In each case the assistant does exactly what it was built to do: it follows the instructions for the stage it's in and carries on with the script. Nothing crashes. The conversation just continues past the one moment that mattered.

And a test suite that only runs the planned path reports this assistant as safe, because on the planned path it is.

## The fix: some rules can't be scoped

The answer isn't to give up on stages. It's to separate two kinds of rules.

Most rules belong to a stage: how to open, how to explore, how to close. Scoping those keeps the assistant controllable.

A small set of rules must hold everywhere, whatever stage the conversation is in and whichever way it branches: responding to distress, handing over to a human, not inventing facts. Those form a shared floor that is active in every stage. They are never placed inside a single stage, however tidy that looks.

This is the same separation as in the framework map: a small fixed floor, and a specific layer on top. Branching conversations are where you find out whether the floor is really a floor.

## How to test it

Testing along the planned path is not enough. Two additions catch this class of problem:

- **Test every floor rule in every stage.** For each rule that must always hold, run a test where the trigger appears in each stage of the conversation, not only where the script expects it. The result is a simple grid: rules down the side, stages across the top, and a yes or no in each cell.
- **Test off-path turns on purpose.** Early disclosure, skipped stages, topic jumps, late disclosure at the close. These aren't edge cases in real use. They're how people talk.

Report the grid and a leak rate: of the off-path tests, how many did the safeguard miss. A safeguard that works only where the script put the trigger has not been tested yet.

## Why this matters for teams adopting AI

Pilots are usually tested on the path the demo follows. The first serious incident rarely happens there. It happens when a real person says something important at a moment nobody scripted.

If you're responsible for rolling an assistant out, the question to ask isn't only "does it have a distress safeguard?" It's "is that safeguard active in every stage, and has anyone tested it where the script didn't expect it?"

## See it happen

The repository has a small modeled example: one assistant built as four stages, in two configurations. In one, the distress rule sits only in the exploration stage. In the other, it's part of the shared floor. Four conversations: one follows the planned path, three disclose distress somewhere else.

On the planned path, both configurations handle it. On the other three, the stage-scoped rule misses every time and the floor rule handles every time. A test suite built only on the planned path would call both of them safe. No API key, no dependencies.

**Read that as a diagram, not as a measurement.** The four conversations are ones I wrote, the assistant is a hundred lines of Python, and its rule is active off-stage only when the configuration says `floor`. Nothing here was observed; the demo executes an argument so you can step through it instead of taking my word for the arithmetic. "Three out of four" is a property of the fixture I built, not a leak rate anyone measured. The claim it supports is about what a planned-path test suite *cannot distinguish*, and that claim is structural — which is why a model of it is honest evidence, and why a number from it would not be.

```
python examples/guardrail_branches/run_demo.py
```

## What I'm claiming, and what I'm not

I'm not claiming that safety testing or adversarial testing is new. What I'm pointing at is a specific interaction: structuring a conversation into stages, which is good for control, silently narrows where safety rules are active, and planned-path testing can't see it. The remedy is a floor of rules that are never scoped, plus a test grid that checks each of them in every stage. If you've seen this written up elsewhere, I'd like to read it.

**One thing this is adjacent to and is not.** There is a published notion of an instruction hierarchy — training a model to prioritise privileged instructions over lower-priority ones — and a reader could reasonably ask whether the floor is just that. It isn't, and the difference is the useful part. An instruction hierarchy ranks instructions by **message role**: whose text is it, the developer's or an untrusted user's. What I'm describing ranks them by **scope**: in which parts of the conversation does this instruction exist at all. A rule can sit at the top of the hierarchy and still be absent from three stages out of four, because priority and presence are different properties. The two compose; neither substitutes for the other.

**There is a second substrate the same argument applies to: memory.** A prohibition stored in an assistant's memory rather than in its prompt is conditional in a way that is easy to miss: it has to survive an extraction step that summarises conversations into facts and preferences — and negation and scope are precisely what summarisers drop — and then it has to be retrieved by a turn that may not resemble it. "Never raise this topic again" is not a preference with a lower success rate; it is a rule whose single failure is the entire harm. Preferences degrade gracefully. Prohibitions do not. That is a note of its own, but the design rule is the same one as here: a constraint whose violation is unacceptable must not be sited anywhere conditional.

## How this connects to the other notes

Note #2 argued for scoping rules to stages. This note is the caveat that comes with it: a few rules must be exempt, and you have to test that they are. Note #1 is the reason the problem stays invisible — planned-path test sets are exactly the ones that report everything as fine.

## Next

Next note: the gap between the prompt in your repository and the string the model actually received, and why it is silent in both directions.
