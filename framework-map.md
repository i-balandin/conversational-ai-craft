# Controlled Specificity: a working framework for client-specific conversational AI

*Ihor Balandin. Working name.*

**The problem it addresses:** making a conversational AI assistant specific to one organisation, its method and its users, while keeping its behaviour controllable, predictable and provable.

Specific and controllable pull against each other. Every nuance added makes behaviour harder to predict, and every generic safeguard makes the assistant less fitted. This framework is a set of practices for getting both. It comes from building and evaluating client-specific assistants, and it is written to transfer to other products, teams and use cases.

**If you read one item, read item 6 below** — the prompt that actually ran. It is the one that has cost teams the most time in my experience and the one that is easiest to check tomorrow. (Item numbers here are the framework's; the notes have their own numbering, and the two do not line up.)

---

## How to read this

**Each item gives:** what it is · where it transfers · what it gives the business · evidence.

**The evidence line is explicit.** It states a rung, and where a number exists, it states `n`, the unit of analysis and who did the rating. Most practitioner writing omits all three, which is how one afternoon's impression comes to look like a result. The rungs:

| Rung | Means |
|---|---|
| **Observation** | One case, one engagement. It informs judgement; it does not constrain a build. Most items live here, and in work of this kind most items should. |
| **Rule** | A second, independent case — different client, different setup — produced the same lesson. Only now is it phrased as an instruction, and it still carries its scope. |
| **Check** | The rule can be expressed as an assertion a script makes, so it fails loudly instead of going stale silently. |

Where the underlying effect is established in published work, the item cites it and claims only the part that is mine. Where I have not searched the literature properly, the item says so rather than implying novelty by silence.

---

## 0. Where the specific layer comes from

### 1. What a practitioner tells you about their method, and what a recording of it shows
**What it is.** When the assistant is built around one person's practice, the specification almost always comes from that person: a questionnaire, an interview, a document they wrote. Often it is accurate. Someone who has taught their own method for years can describe it more precisely than an observer would, and treating every such account as suspect is both insulting and wrong. But sometimes the account describes the practice as intended rather than as it runs, and that version of the gap is invisible to the person describing it — which is why asking sharper questions does not close it.

The useful part is that **you cannot tell from the description which case you are in**, and the two need very different amounts of work. So rather than deciding in advance, get hold of artefacts of the practice where they exist — a recorded session, a talk, something written in their own voice — and keep one of them out of the build to check against. Where the account and the artefact agree, the description has just become evidence. Where they diverge, you know months before a user does.

This matters because of what is actually being reproduced. It is not a set of behaviours; it is a specificity — a tone, a way of moving through a conversation, a method with its own vocabulary — and every case carries its own. A worked example is worth more here than a rule, which is why the last line of this item is a question rather than a procedure: *what would show me I have this person's practice rather than their account of it?*
**Transfers to.** Brand voice, "this is how our support talks", a sales methodology, any subject-matter-expert assistant — anywhere the person writing the spec is also the person being modelled.
**Business value.** Rework found at acceptance is the most expensive kind, and this particular mismatch is the one sign-off is worst at catching.
**Evidence.** *Observation. Recurs across engagements; no count was kept, so it sits at the observation rung.* The gap itself is old ground: espoused theory versus theory-in-use (Argyris and Schön, 1974), and the limits of introspective access are older still (Nisbett and Wilson, 1977). **What I would add is narrower.** In this work the acceptance criterion is drawn from the same source as the specification — the client reads the transcript and says whether it sounds right — so sign-off inherits whatever the description got wrong and cannot report it. One held-out artefact breaks that circuit, and if the account was accurate all along you have lost an afternoon. *Note #7.*

---

## 1. Control architecture

### 2. Structure over rules
**What it is.** Specificity lives in the structure of the conversation — stages, each with a few scoped instructions — not in a long list of rules. A new rule stays only if a test fails without it.
**Transfers to.** Any customised assistant: HR and onboarding assistants, support agents, internal copilots, sales assistants.
**Business value.** Behaviour stays predictable as the assistant is tailored, maintenance gets cheaper, and fixes stop breaking unrelated behaviour.
**Evidence.** *Observation, stated as a design conclusion. The effect it rests on is established; my own attempt to reproduce it returned a null.* That models follow instructions worse as constraints accumulate is measured in published benchmarks (FollowBench, CFBench, and SEQUOR for multi-turn). The architectural prescription drawn from it is mine. I ran the experiment in this repository — 180 calls, one model, 0 to 40 extra rules, two arms — and it detected nothing: `n = 180 calls; unit = one reply; rated by three mechanical checks`, one of which failed once, at low load. The cause is diagnosable and mine: two of the three criteria could not fail at all, so the measure saturated. Published as it came out, with the data. This item therefore rests on the benchmarks plus practice, and not on evidence of my own. *Note #2.*

### 3. Shared floor, specific layer — and the floor cannot be sited anywhere conditional
**What it is.** Rules that must hold everywhere (safety, escalation, no invented facts) form a small fixed floor. The client's method, style and content form a separate layer on top. The floor may not be placed inside a stage, because a rule inside a stage does not exist outside it. **The same argument now applies to a second substrate: agent memory.** A prohibition stored as a memory entry is subject to an extraction step that summarises for facts and preferences — and negation and scope are exactly what summarisers drop — and to oblique triggers, where the turn that violates the rule does not resemble the rule. A preference that fails to surface costs a little quality. A prohibition that fails to surface is the harm itself.
**Transfers to.** Multi-client platforms, agencies, and any product that keeps things about a user between sessions.
**Business value.** A client's method can change without putting safety at risk; the floor is reused across products; and constraints whose violation is unacceptable stop being filed next to preferences in the same store.
**Evidence.** *Rule, for the stage half: two independent mechanisms, and a modeled example in this repository — a safety rule scoped to one stage misses 3 of 4 off-path conversations in a four-case fixture I wrote, while the same rule in the floor misses none, and planned-path tests cannot tell the two configurations apart. n = 4 authored cases; unit = conversation; rated by construction, not by a person. Observation for the memory half.* Adjacent published work: the instruction hierarchy (Wallace et al., 2024) prioritises instructions by **message role**; this item is about scope across **conversation stages and storage substrates**, which is a different axis and composes with it rather than replacing it. Retrieval-time governance of agent memory is an active area (e.g. MemLineage, 2026), but it addresses untrusted content re-entering as instruction, not the preference/prohibition asymmetry. *Notes #3 and #6.*

---

## 2. Encoding what makes it specific

### 4. Style as a setting, and "too directive" is not one variable
**What it is.** How directive the assistant is, from open questions to concrete guidance, is a deliberate setting chosen per use case and checked in evaluation, not left to the model's default. A complaint about directiveness rarely names the variable that produced it. In the case I have, the objection decomposed into two criteria that are orthogonal to the strength of the advice: **does it state the grounds for the advice when asked**, and **does it revise its position on new information**. Acting on the complaint literally — making the assistant less directive — would have removed the behaviour the same user rated highest, twice.
**Transfers to.** Coaching, mentoring, support, advisory and sales: anywhere the right amount of guidance depends on the audience.
**Business value.** The assistant matches what the buyer and users expect. A mismatch here can lose a deal even when the technology is strong.
**Evidence.** *Observation. n = 2 scored sessions, one user, rated by that user against a ten-category instrument they were given.* A second case from a different setting is sometimes cited alongside this one, but it turns on how directive the product was expected to be in the first place rather than on the same variable, so it supports a different reading and does not promote this to a rule. The known half: people discount algorithmic advice and explanation raises uptake (algorithm aversion, advice-taking), and that users report problems reliably but propose fixes badly is Nielsen's first rule of usability. **One caution belongs inside the criterion.** "Revises its position" rewards sycophancy — an assistant that backs down to keep the user happy rather than because the argument changed — unless you split it in two: revision prompted by new information, and capitulation under pressure. Score those separately, or the criterion will reward the behaviour it was meant to catch.

### 5. Find the noun before you write the rule
**What it is.** A descriptive attribute in a persona imports the whole semantic field of the word used. Prohibiting the symptom fights the attribute that generates it, and naming the forbidden thing makes it more likely, not less. The practical move is diagnostic: before adding a rule against a behaviour, find the term in the prompt that is producing it, and narrow that term by definition rather than banning its output.
**Transfers to.** Any role prompt — "acts as a lawyer", "a background in the military", "came up through sales".
**Business value.** Rule lists stop growing to fight their own earlier lines, which is the maintenance cost item #2 exists to avoid.
**Evidence.** *Observation, subsequently adopted as standing practice; not yet measured.* Both halves of the mechanism are published and recent: style features are entangled rather than orthogonal, so prompting one shifts others (Cho et al., *A Concise Agent is Less Expert*, 2026), and naming a forbidden token primes it, which accounts for the large majority of negative-constraint violations (Rana, *Semantic Gravity Wells*, 2026). **What I have not found written up is the remedy side** — operational narrowing of the loaded term as the move that replaces the prohibition — and that search was shallow, so the claim is that I have not found it, not that it is absent.

---

## 3. Verification

### 6. The prompt you read is not the prompt that ran
**What it is.** The prompt text is usually data rather than code: a row in a database, versioned on its own schedule and put live by an action that leaves no commit. The code that builds the variables moves with your releases. When the two disagree, instructions go missing in either direction and nothing is raised — **dropped**, when the code supplies a variable the deployed template never names, so the value is built correctly and discarded; or **empty**, when the template names a variable nothing supplies. The same gap swallows prose, so a standing instruction written in the repository and never republished is simply not in the system. Add the everyday variants — the draft is not the published version, the branch you read is not the branch that serves — and the rule follows: **log what the code declared, what the template names and what carried a value; never evaluate against the file.** Parse the template rather than grepping it, so a mention inside a comment cannot register as present, and log rather than throw: by the time the check exists the defect is usually already live, and an assertion would take the product down to report something a log line reports just as well.
**Transfers to.** Every LLM product with a deployment step between the prompt and the model, which is every LLM product past its first month.
**Business value.** This is the cheapest class of defect to detect and one of the most expensive to leave running, because nothing errors — output remains fluent and plausible while a whole section of the instructions is absent.
**Evidence.** *Observation, in production; n = 1 system, unit = the deployed template version, established from the codebase rather than from recollection. Of everything in this map, this is the observation I would put most weight on.* Two blocks the code assembled on every conversation — a retrieved-knowledge section and a session-context section — were absent from the deployed template, and so from every prompt the model saw, for **almost six months**, and still live on the day a check for it was first written. The fix is a template republication, which leaves no commit, so the end of it cannot be established from the code and is deliberately left open rather than estimated. The same property is why the *start* was invisible: there is no commit marking that either. A runnable example is in this repository. *Note #4.*

### 7. The vacuous pass and the not-applicable answer
**What it is.** Checks tied to a stage of a conversation can pass silently when the conversation never reached that stage: the check was written to catch a bad ending, there was no ending, so nothing bad was found. Giving such checks a third answer, not applicable, and reporting how many conversations reached each stage, removes the false confidence.
**Transfers to.** Any multi-step AI workflow evaluated with stage-based checks: agents, support flows, onboarding and sales assistants.
**Business value.** Go/no-go decisions rest on evidence that measures what everyone assumes it measures.
**Evidence.** *Check — the remedy is asserted by a script, and the demo in this repository scores real (synthetic) transcripts rather than modelling the outcome.* **There is an older name for it, and it is the one to use:** this is vacuity, known in assertion-based formal verification since the 1990s as antecedent failure — an implication that passes trivially because its precondition never held. Beer et al. report that typically one specification in five passes vacuously during the first formal-verification runs of a new hardware design, and that a vacuous pass always indicates a real problem, in the design, the specification or the environment. My contribution is not the phenomenon; it is that conversation-level evaluation reproduces it, that the antecedent there is a stage the conversation may never reach, and that the remedy has to report stage-reach alongside the score. *Note #1.*

### 8. The judge reads the policy it is judging
**What it is.** When an LLM grades a transcript against criteria, it is usually given the assistant's own prompt as context. That makes the prompt an input to the grade. An absolute stated in the prompt becomes a hard failure everywhere in the rubric, a carve-out has to be repeated in every criterion or it is not honoured, and a criterion outlives the requirement it encoded — so a corrected assistant scores *down* for obeying the client's new instruction. Removing a requirement is a change to the evaluation, not only to the build.
**Transfers to.** Every LLM-as-judge pipeline that passes the system prompt to the judge, which is most of them.
**Business value.** Stops a rubric from silently encoding last quarter's product and penalising this quarter's.
**Evidence.** *Observation, across one family of setups; no count was kept.* Adjacent and documented: evaluator-prompt contamination and stale test cases are named in practitioner evaluation guides. The specific consequence — that an absolute in the policy propagates into every criterion, and that a withdrawn requirement must be swept from the rubric too — is the part I have not seen stated. *Note #5.*

### 9. Audit the instrument before the artefact
**What it is.** A short checklist run on the evaluation setup *before* a test round, not after. Its items are ordinary and individually unremarkable; the point is that they are checked in advance, because each has silently produced a wrong conclusion: the unit of analysis (a per-thread aggregate and a per-session-arc aggregate gave materially different pass rates on the same transcripts, and the per-thread view hid an already-fixed behaviour across three builds); the turn budget as a confound; a test file whose multiple cases the harness merged into one, so the run table reported green on cases that never ran; and criterion staleness, per item #8.
**Transfers to.** Any team whose eval is a config file plus a runner.
**Business value.** Most of what is reported as a model failure in my experience was a measurement failure, and measurement failures are cheaper to fix and more embarrassing to find late.
**Evidence.** *Observation per item. No figures are quoted here: the aggregation case is the only one that has any, and a pass rate means nothing without its denominator and its exclusion rule beside it.* **This is a discipline, not a discovery** — the individual items appear as bullets in vendor evaluation guides. What I am contributing is the checklist and the insistence that it runs first. **One limitation to state plainly:** choosing the unit of analysis *after* seeing which one revealed the effect is outcome-driven re-analysis, whatever the merits of the choice. State the unit before the round.

### 10. Presence is not adequacy, and the omission has a shape
**What it is.** A mechanical conformance harness tests for the presence of tokens. It cannot distinguish a framework that has been *built* from one that has been *mentioned*, so a build missing half of a client's method can pass every check. Two harnesses are needed: one for runtime consistency, and one for fidelity, written from the client's own source document rather than from our notes on it, with every rule attributed to the section it came from. **Report coverage per pillar and never as a total** — an omission is structured, and an average is exactly the operation that hides a structure.
**Transfers to.** Compliance and AI-governance claims of the form "we cover 87% of the policy", which this item argues is a meaningless number.
**Business value.** A coverage claim that survives someone opening the source document and checking a section.
**Evidence.** *Rule.* A harness passing every one of its checks on a build with a major part of the client's method absent, and separately a section of a client's own guide covered at zero while a large battery of checks passed — and that section reversed a change that was about to ship. *No counts are quoted, deliberately: a count of passing checks is not a count of behaviour, which is this item's own argument pointed back at itself.* The lexical-versus-semantic limitation and the argument for per-control rather than aggregate reporting are established in automated compliance checking; **the transfer of that result into prompt-conformance testing is the part I am claiming**, and the sub-practice of tracing every rule to its source section is requirements traceability applied to prompt setups, where it is not standard practice. *Note #8* carries the version of this that applies to a whole framework rather than one document.

### 11. Detecting silent retrieval failure
**What it is.** An assistant connected to a knowledge base can retrieve nothing and still answer convincingly from general knowledge, stating that it used the provided material. A test design that catches this separately from answer quality.
**Transfers to.** Any assistant grounded in company documents: internal knowledge assistants, support with documentation, policy and compliance Q&A.
**Business value.** Catches answers that look grounded but are not, before they cost trust or create compliance risk.
**Evidence.** *Observation, then modeled: the example in this repository is a deterministic model of the test design rather than a measurement.* A typical answer-quality check passes a confident answer built on nothing and fails the only honest reply; a grounding check gets both right. Retrieval must be observed as an event in the trace, never inferred from the assistant's wording. A full note on this item is the next increment.

---

## 4. Warrant: what the assistant is entitled to assert

### 12. The claim with no ground truth, which a groundedness check cannot fail
**What it is.** When personalising, an assistant makes confident assertions about third parties it has never encountered — the user's manager, their team, what those people want — and claims feelings it cannot have. A groundedness or faithfulness metric is structurally powerless here: it compares a claim against provided context, and this claim's referent is not in the context at all, so the metric degrades quietly to vacuity rather than failing. What catches it is a criterion about standing: does the assistant have grounds to assert this, and if not, does it narrow, ask, or abstain.
**Transfers to.** HR, sales, support and advisory assistants — anywhere personalisation invites inference about people who are not in the room.
**Business value.** The failure is invisible to the metric suite most teams already run, and it is the kind a user notices immediately and reports as the assistant "having opinions about my manager".
**Evidence.** *Observation, from one user's written feedback; n = 2 sessions, rated by that user.* Evaluating by warrant rather than factual match is already proposed elsewhere — in the legal domain as a failure of legal warrant rather than of citation (Taranukhin and Shwartz, 2026) — and claimed feeling is documented as deceptive empathy and anthropomorphic deception. **The case I am adding is the one where no ground truth exists at all**, which is the condition under which the standard metric family is not merely wrong but inapplicable.

### 13. A conformance profile for what transcripts cannot show
**What it is.** Some quality principles — transparency, respect for autonomy, data ethics — leave little or no trace in a transcript. A short profile states per release what was measured, what was attested, under which conditions, with what uncertainty, and at which assurance level: self-declared, evidence-backed or independently reviewed.
**Transfers to.** Regulated settings, AI governance and documentation work, procurement and vendor reviews.
**Business value.** An honest answer to "how do you know it is safe and good?" that separates what was measured from what was declared.
**Evidence.** *Proposal, now written up as a method. Proposed once against one published framework; not yet adopted anywhere, so it stays a proposal until it has been.* Its form is an assurance case in the claims-arguments-evidence tradition, and the assurance levels are borrowed from that tradition rather than invented here. The sorting step that makes it usable — every principle tagged by the instrument that can see it, and none entering the eval set without a transcript trace — is the part I would defend. *Note #8.*

---

## How the pieces fit

A shared floor keeps every assistant safe, and it cannot be sited anywhere conditional — not in a stage, not in memory. Structure keeps the specific layer controllable, and the content of that layer has to be elicited from practice rather than from self-report. A style setting fits it to its audience. Verification then has to survive its own failure modes: the prompt that actually ran, conversations that end early, a judge reading the policy, a harness that tests for presence, and a metric family that cannot fail a claim whose referent it was never given. To adapt the framework to a new organisation, you rebuild the specific layer and its tests. The floor and the method stay.

## What this is and isn't

It is a working framework from practice, on its way to a tested method. The evidence lines are worth reading rather than skimming: several items sit at the observation rung, one is a proposal that still needs practical validation, and a couple deliberately quote no figures at all. That spread is what a framework looks like while it is still being built, and saying so is what makes the items that have earned a higher rung worth anything. Where the underlying effect is established elsewhere, the item says so and claims only the remainder — in item #7 the established work is both older and better measured than mine. Everything marked as mine is open to challenge. If you have seen any of it written up, I would rather read that than re-derive it.

It is not a product, and it is not a finished standard.
