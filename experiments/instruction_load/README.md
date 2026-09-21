# The instruction-load experiment

The argument in [note #2](../../posts/02-more-rules-less-control.md) is that
encoding a client's specificity as an ever-growing list of rules costs you
control, and that the specificity should live in the structure of the
conversation instead. This is how you check that on your own system rather than
taking my word for it.

It measures two things as more rules are added: whether a few core rules you can
check mechanically are still kept, and how much repeated runs of the same input
disagree with each other. It runs two arms at every load level — all the rules
in the prompt at once, versus only the ones belonging to the current stage —
which is the direct test of the design move the note argues for.

## Run it with no key first

```
CEN_DRY_RUN=1 python run.py
```

That exercises the entire pipeline against a canned responder: no key, no
network, no cost. You get the same table and the same chart, filled with
numbers that mean nothing. It exists so you can see exactly what the script
does before deciding whether to point a real key at it.

## What it does with a key, precisely

Running a stranger's script against your API key is a reasonable thing to be
cautious about, so here is what there is to check. The file is about 390 lines
of plain Python in one place, with no imports beyond the standard library and
whichever provider SDK you chose, and all of this is verifiable by reading it.

- **It never handles your key.** `grep API_KEY run.py` returns six lines and you
  can check all six: three are the `export` examples in the usage notes at the
  top, and three are a dictionary of environment-variable *names*, used only to
  print a useful error when none is set. Nowhere does the script read the value.
  The key is read by the provider's own SDK, the way that SDK always reads it.
  The script never receives it, never prints it and never writes it anywhere.
- **What it sends.** The system prompts assembled from the two rule lists in the
  file, and the five user messages in the file. That is all. Nothing from your
  machine, your files, your environment or your data.
- **Where it sends it.** Your provider's SDK, and nowhere else. There is no
  telemetry, no analytics, no reporting back, and no other network call in the
  script.
- **What it writes.** Two files, both in this directory: `results.csv` and
  `adherence.png`. There is one `open()` call in the whole script and one chart
  save; nothing is written outside this folder.

If you want a further belt: use a throwaway key with a spend cap, or run it on
Gemini's free tier, where a full run costs nothing at all.

## Scale and cost

The defaults are 5 load levels × 5 messages × 10 repeats × 2 arms × 2 models,
which is 1000 calls. Each one sends a system prompt of at most about 700 tokens
and caps the reply at 300. On a small model that is cents; on a large one, a few
dollars. `CEN_REPEATS=5` halves it and still leaves enough repeats for the
run-to-run figure to mean something.

Two models is the useful number, and the interesting question is not which
scores higher — it is whether the curve has the same shape on both. One model's
curve is a fact about that model.

## And if you would rather not run anything

The argument in the note is stated in full without it, and the note says plainly
that it has no numbers yet. Nothing here depends on you spending money to check
someone else's reasoning. The reason to run it is that the number that matters
for your product is the one from your model and your rules — mine would only
tell you that the effect exists somewhere else.
