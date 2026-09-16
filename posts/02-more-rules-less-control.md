# More rules, less control: building assistants that stay specific

*Conversational Eval Notes #2. Ihor Balandin.*

Making an AI assistant fit one organisation usually goes like this. You write a solid prompt. Testing shows a problem, so you add a rule. Then another. A client's method has twenty nuances, so twenty more rules. Each fix works when you test it alone. A few weeks later the assistant is harder to steer than it was at the start: a new rule fixes one thing and quietly breaks two others, and nobody can say which instruction is doing what.

This note is about why that happens and what to build instead.

## The known part

The first half is well documented. Research on instruction following shows that models get worse at obeying instructions as more constraints pile up, and worse again when those constraints accumulate over a long conversation. Benchmarks such as FollowBench, CFBench and, for multi-turn conversations, SEQUOR measure exactly this. So I won't argue that more instructions can hurt. That's established.

## The part that gets less attention

What the benchmarks measure is a curve. What they don't tell you is what it means for how you design a specific assistant.

Here's the consequence I keep running into. If the thing that makes your assistant specific lives in an ever-growing list of rules, you are building against that curve. Every nuance you encode as another instruction pushes you further along it. Past some point, adding specificity this way reduces control instead of increasing it.

So the design question isn't "how do I write better rules?" It's **"where should specificity live, if not in a longer list of rules?"**

## Signs you're past the point

- A new rule fixes the case you tested and breaks behaviour you didn't touch.
- Results vary more between runs of the same test than they used to.
- The team can't explain which instruction produces a given behaviour.
- Rules start contradicting each other in edge cases, and the model picks one at random.
- The prompt grows every week, and nothing ever gets removed.

## Where specificity should live

These are the design moves I use. They're arguments to test, not settled results, and the last section shows how to test them on your own assistant.

**1. Put rules where they apply.** Most rules only matter at one stage of a conversation. An onboarding rule doesn't need to be active during the closing. If the conversation is built as stages, each with its own short set of instructions, the model sees a few relevant rules at a time instead of all of them all the time. The specificity is still there. It's just spread across the structure instead of stacked in one place.

**2. Keep a small fixed floor, and a separate specific layer.** Some rules must hold everywhere: safety, escalation when someone is in distress, not inventing facts. Keep those as a short, stable floor that every assistant shares. The client's method, style and nuance go in a separate layer that changes per client. When the two are mixed in one list, every client-specific change risks the safety rules. When they're separate, you can change the method without touching the floor.

**3. Check behaviour instead of describing it.** Not every expectation has to become a prose instruction. Some are better expressed as examples, and many are better expressed as evaluation criteria: you check whether the behaviour happens, and fix only what fails. A behaviour that a test confirms doesn't need three extra sentences in the prompt.

**4. Make every rule earn its place.** A new rule comes with a test case that fails without it and passes with it. A rule that doesn't change any outcome gets removed. This keeps the list from growing just because adding is easier than deleting.

## Why this matters for teams adopting AI

If you're customising an assistant for your organisation, the length of its rule list is an early warning sign. It grows quietly, each addition looks reasonable, and the cost shows up later as behaviour nobody can predict or explain. That's a problem for trust, for maintenance and for anyone who has to answer "why did it say that?".

A structure with a small shared floor and a specific layer on top also transfers better. The floor carries over to the next use case. Only the specific layer is rebuilt.

## How to measure it on your own assistant

You don't need to take any of this on faith. The repository has a small experiment you can run against a real model:

- Pick a few core rules you can check automatically (for example: ask one question per reply, don't give direct advice, keep replies short).
- Run the same set of user messages several times, each time with a different number of additional, realistic rules active: none, 5, 10, 20, 40.
- For each level, measure two things: how often the core rules are still followed, and how much results vary between repeated runs.
- Look for the point where adherence starts to drop or variation starts to rise.

Then try the same core rules with the extra rules scoped to stages, so fewer are active at once, and compare. That's the direct test of design move 1.

```
export ANTHROPIC_API_KEY=...
python experiments/instruction_load/run.py
```

I'm not publishing numbers, because I haven't run this at a scale worth reporting. They would depend on the model and on the rules anyway, and the point is that you can find the knee for your own assistant.

## What I'm claiming, and what I'm not

I'm not claiming that too many instructions degrade performance. Others have measured that carefully. What I'm proposing is a design conclusion from it, based on building client-specific assistants: specificity should be encoded in structure, with a separate shared floor, rather than accumulated as rules. That conclusion should be tested, and the experiment above is how. If you've seen this argued elsewhere, I'd like to read it.

## Next

Next note: what happens to guardrails when a conversation leaves the path they were written for, and why some rules must never be scoped to a stage.
