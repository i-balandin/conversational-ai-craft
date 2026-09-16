# Controlled Specificity: a working framework for client-specific conversational AI

*Ihor Balandin. Working name.*

**The problem it addresses:** making a conversational AI assistant specific to one organisation, its method and its users, while keeping its behaviour controllable, predictable and provable.

Specific and controllable pull against each other. Every nuance added makes behaviour harder to predict, and every generic safeguard makes the assistant less fitted. This framework is a set of practices for getting both. It comes from building and evaluating client-specific assistants, and it is written to transfer to other products, teams and use cases.

**How to read each item:** what it is · where it transfers · what it gives the business · current evidence.

---

## Control architecture

### 1. Structure over rules
**What it is.** Specificity lives in the structure of the conversation (stages, each with a few scoped instructions), not in a long list of rules. A new rule stays only if a test fails without it.
**Transfers to.** Any customised assistant: HR and onboarding assistants, support agents, internal copilots, sales assistants.
**Business value.** Behaviour stays predictable as the assistant is tailored, maintenance gets cheaper, and fixes stop breaking unrelated behaviour.
**Evidence.** That models follow instructions worse as constraints accumulate is established in published benchmarks. The design conclusion is mine and still being tested; an experiment is in this repository. *Note #2.*

### 2. Shared floor, specific layer
**What it is.** Rules that must hold everywhere (safety, escalation, no invented facts) form a small fixed floor. The client's method, style and content form a separate layer on top.
**Transfers to.** Multi-client platforms, agencies, and companies rolling assistants out across many teams.
**Business value.** A client's method can change without putting safety at risk, the floor is reused across products, and each new client means rebuilding one layer instead of the whole assistant.
**Evidence.** A design principle from practice. A modeled example in this repository shows the failure it prevents: a safety rule scoped to one stage misses 3 of 4 off-path conversations, the same rule in the floor misses none, and planned-path tests can't tell them apart. *Note #3.*

## Encoding what makes it specific

### 3. Style as a setting
**What it is.** How directive the assistant is, from open questions to concrete guidance, is treated as a deliberate setting chosen for each use case and checked in evaluation, not left to the model's default.
**Transfers to.** Coaching, mentoring, customer support, advisory and sales: anywhere the right amount of guidance depends on the audience.
**Business value.** The assistant matches what the buyer and users expect. A mismatch here can lose a deal even when the technology is strong.
**Evidence.** From practice, including a case where the style setting, not technical quality, decided the outcome. Not yet written up.

## Verification

### 4. Silent false-pass and the not-applicable answer
**What it is.** Checks tied to stages of a conversation can pass silently when the conversation never reached that stage. Giving such checks a third answer, not applicable, and reporting how many conversations reached each stage removes the false confidence.
**Transfers to.** Any multi-step AI workflow evaluated with stage-based checks: agents, support flows, onboarding and sales assistants.
**Business value.** Go/no-go decisions rest on evidence that measures what everyone assumes it measures.
**Evidence.** Reproducible example in this repository. Scoring whole conversations and not only single replies is standard practice; the silent pass and the not-applicable fix are the part I'm contributing. *Note #1.*

### 5. Detecting silent retrieval failure
**What it is.** An assistant connected to a knowledge base can fail to retrieve anything and still answer convincingly from general knowledge, saying it used the provided material. A test design that catches this separately from answer quality.
**Transfers to.** Any assistant grounded in company documents: internal knowledge assistants, support with documentation, policy and compliance Q&A.
**Business value.** Catches answers that look grounded but aren't, before they cost trust or create compliance risk.
**Evidence.** Observed and measured in practice. A modeled example is in this repository (`examples/silent_retrieval`): a typical answer-quality check passes a confident answer built on nothing and fails the only honest reply, while a grounding check gets both right. Written note still to do.

### 6. A conformance profile for what transcripts can't show
**What it is.** Some quality principles, such as transparency, respect for autonomy or data ethics, leave little or no trace in a conversation transcript. A short conformance profile states per release what was measured, what was attested, under which conditions, with what uncertainty, and at which assurance level: self-declared, evidence-backed or independently reviewed.
**Transfers to.** Regulated settings, AI governance and documentation work, procurement and vendor reviews.
**Business value.** An honest answer to "how do you know it's safe and good?" that separates what was measured from what was declared.
**Evidence.** Proposal drafted in practice. Not yet published.

---

## How the pieces fit

A shared floor keeps every assistant safe. Structure keeps the specific layer controllable. A style setting fits it to its audience. Verification that accounts for incomplete conversations, silent retrieval failures and unmeasurable qualities shows that it actually works. To adapt the framework to a new organisation, you rebuild the specific layer and its tests. The floor and the method stay.

## What this is and isn't

It is a working framework from practice, moving toward a tested method. Items marked as mine are open to challenge; where the underlying effect is already known, I say so. It is not a product or a finished standard.
