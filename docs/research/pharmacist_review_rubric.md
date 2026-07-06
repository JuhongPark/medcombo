# Pharmacist Review Packet Rubric

## Purpose

This rubric defines how pharmacists, clinicians, medication safety reviewers, or
trained evaluators should review MedCombo packet output during product
development. The goal is not to prove clinical benefit. The goal is to find
whether the packet is useful, bounded, and clear enough to support a
professional medication review conversation.

## Review Unit

Evaluate one generated review packet at a time. A packet should include:

- medication list readiness
- unresolved identity items
- missing dose, frequency, route, or formulation details
- duplicate active ingredient signals
- curated interaction review signals
- supplements and other out-of-scope items
- health context to ask about
- pharmacist questions
- evidence appendix

## Rating Scale

Use a 1 to 5 rating for each criterion.

- 1 means harmful or unusable.
- 2 means materially incomplete or misleading.
- 3 means usable with important caveats.
- 4 means useful with minor issues.
- 5 means highly useful and clearly bounded.

## Core Criteria

### Usefulness

Does the packet help a pharmacist or clinician start a medication review faster?

Look for:

- visible medication identity status
- clear missing details
- relevant questions
- signal explanations that are easy to scan

### Misleading Wording

Does any text imply that MedCombo has cleared the regimen, completed a safety
screen, or made a medication decision?

Flag any wording that suggests:

- complete interaction coverage
- medication combinations are cleared
- personalized clinical risk has been estimated
- the user should change medication use without professional review

### Missing Clinical Context

Does the packet show which patient-specific context is missing or only recorded
without being interpreted?

Look for:

- age, pregnancy, kidney function, liver function, weight, bleeding history, or
  allergy context when relevant
- clear separation between recorded context and interpreted risk

### Priority Appropriateness

Are prompt, routine, unknown, and information priorities understandable and
proportionate to the demo evidence?

Flag:

- over-prioritized low-information signals
- under-prioritized identity uncertainty
- unclear difference between signal priority and medication risk

### Source Clarity

Can the reviewer see which rule, evidence record, or source supports each
signal?

Look for:

- source IDs near signals
- evidence concern text
- source appendix
- explicit curated demo limitation

### Follow-Up Question Quality

Would the generated questions help a pharmacist or clinician clarify the list?

Look for:

- questions tied to missing identity or details
- questions tied to specific review signals
- questions that avoid telling the user what medication action to take

## Required Reviewer Notes

For each packet, collect:

- overall usefulness score
- most useful packet section
- most misleading or confusing wording
- missing context needed before professional review
- inappropriate priority, if any
- unclear source or evidence note, if any
- one suggested improvement to the pharmacist questions

## Stop Conditions

Stop the evaluation and mark the packet as unacceptable if it:

- says the list is cleared
- tells the user to start, stop, combine, or change medication use
- hides unknown or ambiguous products
- hides source limitations around review signals
- presents a safety score or risk score

## Current Fixture Link

The executable fixture set is stored in
`data/benchmarks/pharmacist_packet_cases.json`. Tests should confirm expected
sections, readiness labels, review questions, and unsafe wording guardrails.
