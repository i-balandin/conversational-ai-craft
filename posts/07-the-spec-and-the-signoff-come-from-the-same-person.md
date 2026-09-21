# The spec and the sign-off come from the same person

*Conversational Eval Notes #7. Ihor Balandin.*

You are building an assistant around one person's method — a coach, a consultant, a senior specialist whose way of working is the product. Where does the specification come from? From them: a questionnaire, a few interviews, a document they wrote. And where does acceptance come from? Also from them. They read a transcript and tell you whether it sounds right.

Stop on that for a second, because it's a loop. The thing you built the assistant from and the thing you check it against are the same source. Which is fine when the source is accurate, and invisible when it isn't.

This note is about the second case, why you can't tell which one you're in from the description alone, and the one cheap thing that breaks the loop.

## First, the part that gets overstated

There's a temptation in this territory to say that people don't know how they work. I don't believe that, and it isn't what I've seen.

A practitioner who has taught their own method for fifteen years will often describe it more precisely than an observer could — they have language for distinctions you'd need months of watching to notice, and they know which parts are load-bearing and which are habit. Treating every such account as suspect is both wrong and insulting, and it poisons a working relationship for no return.

Sometimes, though, the account describes the practice as *intended* rather than as it runs. Not because anyone is being dishonest — because the description is assembled from the same place a self-image is: what you aim at, what you tell trainees, the version you'd defend. And that version of the gap is invisible to the person describing it, which is exactly why asking sharper questions doesn't close it. Sharper questions get you a sharper account of the same thing.

**The useful observation isn't that clients are wrong about themselves. It's that you cannot tell from the description which case you're in, and the two need very different amounts of work.**

## The known part

The distinction is old and has a proper name. Argyris and Schön called it espoused theory versus theory-in-use (1974): what a professional says governs their practice, against what an observer would infer from watching it. The limits of introspective access are older still — Nisbett and Wilson's *Telling More Than We Can Know* is from 1977. Knowledge elicitation for expert systems hit the same wall decades ago and reached the same conclusion: for some kinds of knowledge you observe rather than ask.

So the gap, its direction and the remedy in principle are all established ground, and I'm citing them rather than claiming them.

## The part I'd add

In this work, **the acceptance criterion is drawn from the same source as the specification** — and that has a consequence I haven't seen stated.

If the spec encoded the intended practice, then the assistant faithfully implements the intended practice. When the client reads its transcript, they compare it against the same internal model that produced the spec. It matches. They approve it, sincerely and correctly by their own lights.

So the defect doesn't merely survive sign-off. **Sign-off is structurally incapable of reporting it**, because it's being checked against the thing that introduced it. You can run three review rounds and get three approvals, and none of them carries information about this particular error.

What happens next is familiar to anyone who's shipped one of these. Weeks later, something vague: *it's close, but it isn't quite me.* No diagnosis attached, because the thing that's missing is the thing that couldn't be articulated in the first place. And now you're changing a built product on the strength of a feeling, which is the most expensive moment in the whole engagement.

## The cheap thing that breaks the loop

Get hold of one artefact of the practice, and keep it out of the build.

A recorded session, a recorded talk, a piece of their written work in their own voice — whatever exists. Use everything else for the build if you like, but hold one back and treat it as the acceptance test alongside the client's reading.

Notice what this is not. It isn't a way to catch the client out, and you shouldn't frame it that way to them, because it isn't what usually happens. **Where the account and the artefact agree, the description has just become evidence** — you now have a specification with independent support, which is a better position than you were in, and it cost one afternoon. Where they diverge, you find out in week two rather than after launch, when it's a conversation instead of a rebuild.

Two more things that help, both small:

**Ask at the start which one you're building.** *Are we reproducing how you work, or how you'd like to work?* Both are completely legitimate products. Some clients answer this crisply and honestly — "the second, and I know it" — and that's a gift, because now the intended practice *is* the spec and there's no gap to find. The failure isn't choosing the aspirational version. The failure is not choosing.

**Remember what you're actually reproducing.** It isn't a list of behaviours. It's a specificity — a tone, a way of moving through a conversation, a vocabulary, a sense of what gets left alone. Every case carries its own, and that's why I'd rather hand someone a worked example than a rule here. The question to keep in your head is: *what would show me I have this person's practice rather than their account of it?*

## Making it measurable, honestly

You can put numbers on part of this, and it's worth doing because "not quite me" is unactionable while a table of gaps is a conversation.

The repository has a small tool that takes two transcripts — one from the assistant you built, one held out from the real practice — and prints surface markers for the assistant's side of each: turn length and its spread, sentences per turn, how often a turn ends on a question, directive phrasing, hedging, self-reference, vocabulary variety, and the words that are much commoner on one side than the other.

```
python examples/style_markers/run_demo.py
```

It argues nothing. It's a measuring stick, and the only honest way to ship this part — a demonstration here would mean writing both the spec and the "real" transcript myself, which would prove my own construction and nothing else.

It also shows you its own limit, which is why I'd read its output twice. The two transcripts it ships with differ obviously in directiveness — one offers a frame and tells the person to write three things down — and the directive-phrasing marker scores both at zero, because none of it is phrased as "you should". **A marker built from phrasings catches the phrasings it was built from.** Agreement on the surface is necessary and nowhere near sufficient, and a gap is a place to go and read, never a score.

## What I'm claiming, and what I'm not

I'm not claiming that self-report is unreliable, that observation beats asking, or that experts can't introspect — all three are long-settled, cited above, and better established than anything I could add.

The circuit, then. In this work the spec and the acceptance test come from one source, so the review round cannot detect an error the spec introduced, and the cost surfaces later as an undiagnosable complaint. One held-out artefact breaks it, costs almost nothing when the account was accurate all along, and turns a vague verdict into a comparison you can act on.

**On evidence.** This recurs across engagements rather than resting on one, and I kept no count, so it sits at the observation rung: it informs how I'd scope a build, and it doesn't constrain anyone else's. The strongest single thing I can say for it is negative — I have not had a case where holding an artefact back cost anything, and I have had cases where nothing independent existed and the vague complaint arrived on schedule.

If you've seen the sign-off half written up — not the espoused/in-use gap, which is textbook, but the observation that acceptance inherits the specification's bias in exactly this class of project — I'd like to read it.

## Next

Next note: what happens when someone hands you a published quality framework and asks you to show the assistant conforms to it — and why the honest answer is never a single percentage.

## How this connects to the other notes

The other six notes are all about instruments that report on something that wasn't there: a stage the conversation never reached, a prompt that never rendered, a policy the judge shouldn't have been marking against, a rule that was never retrieved. This one is about the first instrument in the chain, which is the client's own account of their practice — and it fails the same way. It reports, and the report is confident, and confidence is not the thing you needed.
