# CareFlow Week 3 - Findings Summary

Total cases: **2000** | Variants: **2** | Transitions: **5**

## Top 3 frequent paths
1. Registration -> Triage -> X-Ray -> Doctor Consultation -> Discharge  (1295 cases, 64.75%)
2. Registration -> Triage -> X-Ray -> Triage -> X-Ray -> Doctor Consultation -> Discharge  (705 cases, 35.25%)

## Rare paths (<1% of cases)
- 0 rare variants, 0 rare transitions (see rare_paths.csv)
- Rework loops (e.g. X-Ray -> Triage) are by design of the simulation, but need clinician validation.

## Unexpected transitions / data-quality flags
- Consecutive duplicate events: 0
- Zero time-gap transitions: 0
- Reversed-time transitions: 0
- [Apne observations yahan add karo]
