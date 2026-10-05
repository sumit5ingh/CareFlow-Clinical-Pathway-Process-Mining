# Week 3 Day 5 - Rare Paths & Anomalies

1. **Threshold:** Variants and transitions occurring in less than 1% of cases (out of N total cases) were classified as rare.
2. **Volume:** X of Y variants and Z of W transitions fell below the threshold and were exported to `rare_paths.csv`.
3. **Genuine exceptions:** Cases with multiple X-Ray to Triage loop-backs (rework) are valid by design of the simulation and are likely genuine clinical exceptions, but they need clinician validation.
4. **Data errors:** A transitions showed consecutive duplicate events and B transitions showed reversed order (reverse path far more common). These were flagged as likely data errors.
5. **Timestamps:** C transitions had a zero time gap, which suggests possible timestamp or logging issues.
6. **Teammate review:** Reviewed teammates' questions and fixes: [add what you found]. Next step (Day 6): bottleneck and time-gap analysis on the cleaned paths.