# Four refusals, kept verbatim

Real refusals from real runs, saved because the retry logic in `../run.py` has
to decide whether waiting will help — and because getting that wrong five times
turned out to be a better story than getting it right.

| file | model | limit | quota id survived? |
|---|---|---|---|
| `day-500-untruncated.txt` | a flash-lite | 500 | yes — `…RequestsPerDayPerProjectPerModel…` |
| `day-20-untruncated.txt` | a newer flash | 20 | yes — same, per **day** |
| `day-20-truncated.txt` | a newer flash | 20 | no |
| `day-20-truncated-2.txt` | a newer flash | 20 | no |

## The mistake worth reading

Every one of these is a **per-day** cap. I never once observed a per-minute
refusal on this tier.

But I spent five runs writing rules to tell per-minute from per-day, because I
assumed a refusal that says *"Please retry in 28 seconds"* and names a limit of
20 must be twenty per minute. It wasn't. It was twenty per day, and the "retry
in 28s" was there anyway.

So I was not failing to draw a subtle distinction. **I was drawing a
distinction the evidence never contained**, and each failed rule made me more
confident the distinction was real and merely hard to detect.

Three things kept that alive, and all three are mine:

**I truncated the evidence.** The error printer cut the message to 700
characters before logging it, and the `quotaId` — the only field that decides
the question — sat past the cut. Two of the four files above still show the
damage.

**I tested against the truncation.** The second rule matched `billing`, which
appears in every refusal. The unit test passed because the fixture I tested
against was an abbreviated copy with that word trimmed out of it.

**I read a plausible number as the unit I expected.** "Limit: 20" with a
28-second retry delay reads like a per-minute quota if you already think in
per-minute quotas. The unit was never stated in the part of the message I let
myself see.

## What the code does now

No classification of the refusal text at all. It honours the delay the provider
asks for, retries, and concludes a limit is hopeless only when waiting has
demonstrably failed to clear it — then prints the message **in full**, which is
how the actual quota id finally became visible and the whole thing resolved in
one reading.

The asymmetry is what makes that default safe: retrying a few times against a
per-day cap wastes a handful of calls, while treating a transient limit as
fatal throws away an hour-long run. The right default is the cheap mistake.
