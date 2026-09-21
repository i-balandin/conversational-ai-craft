# Two refusals, kept verbatim

The provider's own words, saved from real runs. They are here because the retry
logic in `../run.py` has to tell "wait and it will clear" from "wait and it
won't", and I got that wrong three times in a row by reasoning about the text
instead of reading it.

- `per_minute.txt` — a per-minute cap. It clears; wait and continue.
- `per_day.txt` — a per-day cap. It does not clear.
- `per_minute_multi.txt` — a third refusal, saved truncated, which is its own
  lesson: the error printer cut the message to 700 characters before logging
  it, and the cut removed exactly the part needed to diagnose what happened.

## Every text rule I tried, and how each one failed

**Match "quota exceeded for metric".** Appears in both. Marks every transient
limit as fatal.

**Match "billing".** Every refusal contains "check your plan and billing
details". Same failure, and this one survived a unit test because I tested
against an abbreviated copy of `per_minute.txt` from which I had, by chance,
removed the word. A fixture that agrees with you is worse than no fixture.

**Match the quota's identity (`RequestsPerDay`).** The most defensible of the
three, and it still aborted a run I could not afterwards diagnose, because the
message had been truncated before it reached the log. Whether it matched on a
per-day violation returned *alongside* the binding per-minute one, I cannot
say — and not being able to say is the point.

## What the code does instead

It decides by behaviour: honour the delay the provider asked for, retry, and
conclude a limit is hopeless only when waiting has demonstrably failed to clear
it. No classification of prose at all.

The asymmetry is what justifies the default. Retrying a few times against a
per-day cap wastes a handful of calls. Treating a per-minute cap as fatal
throws away an hour-long run, which is what actually happened, twice.

And the message is now printed in full when it finally gives up, because the
one time I truncated it to keep the output tidy, I destroyed the evidence.
