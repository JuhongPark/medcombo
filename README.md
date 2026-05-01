# MedCombo

## Overview

MedCombo is an educational medication-combination review and safety-awareness prototype. It explores how software might help users review medication combinations more carefully by surfacing potential medication-safety concerns for further review.

The project is intended as an early student prototype, not as a clinical product. Its purpose is to support learning, experimentation, and medication-safety awareness.

## Course Background

MedCombo was started during the topic-selection phase for the MIT 1.001 term project in Engineering Computation and Data Science, taught by Prof. Abel Sanchez and Prof. John R. Williams.

During this phase, several healthcare AI directions were explored, including population-scale drug response analytics, precision medicine, clinical decision support, and pharmacy-related medication safety systems.

## Why This Prototype Was Started

Medication use can become difficult to understand when multiple prescriptions, over-the-counter products, supplements, or combination drugs are involved. Even a simple medication list can raise questions about possible drug-drug interactions, duplicated ingredients, overlapping therapeutic classes, or situations where professional review may be needed.

MedCombo was started to explore whether a lightweight software prototype could make those questions more visible in an educational setting.

## Connection to MIT 1.001

MIT 1.001 emphasizes computational thinking, data analysis, modeling, and engineering problem solving. MedCombo connects to those themes by framing medication-combination review as a data-driven safety-awareness problem.

The prototype offers a possible direction for applying computation to healthcare-related information, while also highlighting the limits of automated decision-support tools in medically sensitive contexts.

## Problem Statement

People may take multiple medications from different sources, including prescriptions, over-the-counter products, and supplements. This can make it difficult to notice duplicated active ingredients, potentially interacting drugs, or medication combinations that deserve review by a doctor, pharmacist, or other licensed medical professional.

The problem explored by MedCombo is how an educational software prototype can organize medication-combination information in a clearer, more safety-aware way without making clinical decisions.

## Prototype Goals

- Help users enter or review a list of medications.
- Surface possible drug-drug interactions for further review.
- Identify duplicated active ingredients when data is available.
- Flag overlapping therapeutic classes where appropriate.
- Indicate cases where professional review may be important.
- Present safety information in a clear and cautious format.
- Support educational exploration of healthcare data and decision-support design.

## What MedCombo Does Not Do

MedCombo does not:

- Prescribe medication.
- Recommend definitive treatment.
- Diagnose medical conditions.
- Replace a doctor, pharmacist, or licensed medical professional.
- Determine whether a medication is safe or unsafe for a specific person.
- Provide emergency medical advice.
- Account for every patient-specific factor, such as age, pregnancy status, allergies, kidney function, liver function, medical history, dosage, timing, genetics, or lab results.

## Initial MVP Features

The initial minimum viable prototype may include:

- Medication list entry.
- Basic medication name normalization.
- Active ingredient lookup where source data is available.
- Drug-drug interaction lookup.
- Duplicate ingredient detection.
- Therapeutic class overlap detection.
- Safety flags with severity or review-needed labels.
- Plain-language explanation fields.
- Clear prompts to consult a licensed medical professional.
- A simple web interface or notebook-based workflow for demonstration.

## Safety and Medical Disclaimer

MedCombo is an educational and decision-support prototype only. It is not a medical device, clinical recommendation system, prescribing tool, diagnostic tool, or substitute for professional medical judgment.

Medication decisions should be made with a doctor, pharmacist, or other licensed medical professional. Users should not start, stop, combine, or change medications based on MedCombo output. For urgent or emergency medical concerns, users should contact emergency services or a qualified medical professional immediately.

Any medication-safety information shown by MedCombo may be incomplete, outdated, incorrect, or not applicable to a specific person.

## Possible Data Sources

Possible data sources for future exploration include:

- RxNorm for normalized medication names and identifiers.
- DailyMed for structured drug labeling information.
- openFDA for public FDA drug data access.
- FDA drug labels and safety communications.
- National Library of Medicine resources.
- Public drug interaction or adverse-event datasets where licensing permits.
- Curated educational datasets created specifically for the prototype.

Any external data source should be reviewed for accuracy, licensing, update frequency, and appropriate use before being used in the prototype.

## Technical Direction

The prototype can begin as a small, transparent application focused on data ingestion, medication normalization, interaction lookup, and safety-aware presentation.

Possible technical components include:

- A Python-based data-processing layer.
- A lightweight web interface for medication entry and results review.
- Structured medication records using normalized identifiers.
- Rule-based checks for duplicate ingredients and class overlaps.
- Source-linked result explanations.
- A cautious display model that distinguishes educational signals from clinical conclusions.

The technical design should prioritize clarity, traceability, and responsible communication over automation that appears more authoritative than the data supports.

## Roadmap

Planned or possible next steps include:

- Define the initial medication data schema.
- Select the first public data source for experimentation.
- Build a medication entry workflow.
- Implement medication name normalization.
- Add duplicate active ingredient detection.
- Add basic interaction lookup.
- Add result explanations and source references.
- Create a small demo dataset for repeatable testing.
- Add tests for safety-rule behavior.
- Document limitations and known gaps.

## Status

MedCombo is in the initial prototype and topic-exploration stage. The project is not ready for real-world medical use and should only be treated as an educational software project.
