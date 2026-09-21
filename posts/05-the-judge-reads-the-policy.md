# Your judge is reading the rules it marks against

*Conversational Eval Notes #5. Ihor Balandin.*

If you grade conversations with a model, you almost certainly hand it the assistant's own system prompt along with the transcript. You have to. Without the policy, a judge cannot tell a violation from a deliberate design choice: an assistant that refuses to give advice looks evasive, one that asks a single question per turn looks incurious, and one that never mentions its own limits looks overconfident. All three are behaviours somebody chose.

So the policy goes into the judge's context, and that one necessary decision makes your prompt an input to your scores. This note is about what follows from that, why the obvious fix makes things worse, and the five-minute diagnostic that shows you how much of it you have.

## The known part

The biases of LLM-as-judge are well covered by now: position bias, a preference for longer answers, a preference for its own outputs, and the reliability that drops as transcripts get longer. Checking judge-against-human agreement is standard advice, and evaluation guides name contamination — including benchmark examples leaking into evaluator prompts — as something to watch.

None of that is what I want to add. What I want to add is narrower: the specific things that go wrong because the judge is reading *the policy*, as opposed to reading anything else it shouldn't.

## Three consequences, and one trap

**An absolute bleeds into criteria about something else.** Write "never give direct advice" in the prompt, and every criterion in the rubric inherits it, including the ones about tone, structure or relevance. A reply that gave advice — warm, on topic, exactly what the person needed — comes back marked down on *warmth*, because the judge holding an absolute reads a violation as a fact about the whole reply. You will spend an afternoon rewording the warmth criterion, and the warmth criterion was never the problem.

**A carve-out is honoured only where the criterion repeats it.** Say the policy has an exception: no advice, unless the person asks twice. The judge applies it while evaluating the criterion that mentions advice, and quietly forgets it everywhere else. So you write the exception into the criteria that need it — and now your rubric contains a copy of your policy, maintained separately, in different words, by a person who is often not the person maintaining the prompt. Both halves are correct on the day they are written.

**A criterion outlives the requirement it encoded.** This one is the expensive one. A client asks you to drop a requirement — they've decided the acknowledgment is optional, or the question limit is too tight. You remove it from the prompt. The criterion that checked it stays, because nobody thinks of a rubric as part of the change. The next run scores lower, and the assistant is now being penalised **for doing what the client asked**. The team reads a red number and starts fixing a bot that isn't broken.

That last one is worth stating as a rule, because it is not obvious and it is cheap to get right: **removing a requirement is a change to the evaluation, not only to the build.**

**And the trap.** The instinct, once you see the bleed, is to stop giving the judge the policy. It works: the bleed stops immediately. It also removes every exception the judge knew about, so correct behaviour starts failing — the assistant that gave advice *because the person asked twice* now fails the advice criterion, and it is right and the rubric is wrong. You have swapped one class of wrong verdict for another and lost the ability to compare the two runs.

This is not a judging problem you can reword your way out of. The rubric is coupled to the policy. The only question is whether you manage the coupling deliberately.

## Why this matters outside the eval team

Two practical consequences, both of which bite in ordinary work.

**Your score moves when you edit the prompt, on criteria you didn't touch.** Which means a comparison between two builds is only clean if the rubric was held fixed *and* none of the policy's absolutes changed between them. If either moved, part of the delta is instrumentation. Most before-and-after numbers I have seen quoted did not hold either constant.

**A rubric quietly encodes an older version of the product.** It accumulates criteria for requirements that have since been withdrawn, and every one of them is a standing penalty on the current build. Nobody notices, because nobody re-reads a rubric that isn't failing.

## What to do about it

**Run the diagnostic.** Take a fixed set of transcripts, and score them twice with your real judge: once with the policy in context, once without. Criteria whose verdicts do not move are independent of the policy. Criteria whose verdicts move are carrying the coupling, and they are the ones to look at. This costs two runs and a diff, and it is the only part of this note I would insist on.

**Then, for each criterion that moved, decide what it is.** A *compliance* criterion asks whether the policy was followed; it should see the policy, and any exception it depends on should be written into the criterion rather than inferred. A *behaviour* criterion asks about something observable in the reply — was it warm, did it answer the question — and should be told explicitly to judge only its own dimension, and to ignore rule violations belonging to other criteria. The distinction is worth making once, per criterion, in writing.

**Keep a list of the absolutes in the policy.** Every "never", "always" and "under no circumstances". When one of them changes, re-read every criterion, because they all inherited it.

**Version the rubric against the prompt.** A score carries two version identifiers or it is uninterpretable later: which build, and which rubric. This sounds bureaucratic until the first time someone asks why last month's number was higher.

## See it happen

The repository has a small example: one policy with one absolute and one exception, three transcripts, three criteria, and three judge configurations — policy in context, policy withheld, and policy in context with the behaviour criteria scoped and the exception named where it is needed.

The first configuration gets two verdicts wrong. The second gets one wrong — a different one. The third gets none wrong.

```
python examples/judge_contamination/run_demo.py
```

Read it as a diagram rather than a measurement. The judge is a model that reasons exactly as described above, and the transcripts and the human verdicts are both mine, so the demo cannot tell you how often this happens to you. What it does is execute the argument, and show you what the with-and-without diff looks like before you run it on a judge that costs money.

## What I'm claiming, and what I'm not

I'm not claiming that LLM-as-judge has biases, that contamination is a category, or that rubrics go stale. All three are documented, and the last one turns up as a bullet in most evaluation guides.

What I'd put forward is the specific coupling, and that it is not optional. Because a judge needs the policy to do its job at all, the rubric and the prompt are one system with two owners, and the three consequences above follow mechanically rather than as accidents. The withheld-policy run as a *diagnostic* rather than a fix, the compliance-versus-behaviour split as the thing you decide per criterion, and "removing a requirement is a change to the evaluation" as a rule with a cost attached, are the parts I have not seen written up.

**On evidence.** This comes from one family of setups on one platform, where all three consequences turned up in the same quarter and the third one cost the most — a corrected assistant scoring down for obeying the client, argued about for a fortnight before anyone re-read the rubric. No counts: I didn't keep any, and I am not going to construct them now. Treat it as one practitioner's observation plus a diagnostic you can run this afternoon on your own rubric, which will tell you more about your situation than my number would.

If you have seen the coupling written up — particularly the bleed, which I find the most surprising of the three — I'd like to read it.

## How this connects to the other notes

Note #1 is about a criterion that passes because the conversation never reached the stage it was checking. Note #4 is about a criterion scoring a prompt that was never sent. This one is about a criterion that is not independent of the thing it measures. In each case the instrument is reporting on something other than what its name says, and in each case the fix is a cheap check nobody runs because nothing looks broken.

## Next

Next note: why a prohibition cannot be stored in an assistant's memory, even though a preference can — and why the difference is not a matter of reliability percentages.
