# CareFlow - Ideal Pathway: Day 1 Notes (Member 1)

## 1. What is an ideal pathway?
The ideal pathway is the expected, clinically correct sequence of activities a
patient should normally follow, for example:
Registration -> Triage -> Consultation -> Tests -> Treatment -> Discharge.

It acts as a reference model. Actual patient journeys from the event log are
compared against it to see where they follow the expected flow and where they
deviate.

## 2. Basic idea of conformance checking
Conformance checking compares an ideal model with the actual event log.
- Cases that follow the rules are "conforming".
- Cases that break a rule (a missing required step, wrong order, an
  unexpected transition) are "deviating".

A deviation is not always an error. Some are valid clinical exceptions, such
as rework loops or an emergency patient skipping Triage. So the ideal pathway
needs two things: strict rules (required steps, allowed order) and a list of
accepted exceptions.

## 3. How it will be used in this project
- Compare the Week 3 variants and transitions against the ideal pathway.
- Detect cases with missing required steps or an invalid order of activities.
- Give Member 2 and Member 3 a rule set (as a document and as JSON) they can
  use