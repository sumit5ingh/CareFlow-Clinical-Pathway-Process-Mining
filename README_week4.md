# CareFlow Week 4: Ideal Pathway Definition

## Input
- `careflow_event_log_clean_sorted.csv` (Case_ID, Activity_Name, Timestamp)
- Week 3 outputs (`transitions.csv`, `top_variants.csv`) for comparison

## Rules summary
- Stages: Registration -> Triage -> Tests -> Consultation -> Treatment -> Discharge
- Required: Registration, Triage, Consultation, Discharge | Optional: Tests, Treatment
- Registration is always first, Discharge always last, no backward moves
- Exceptions: emergency Triage skip, repeat tests, multiple consultations

## Output files
- `ideal_pathway_stages.md`, `required_vs_optional.md`, `allowed_transitions.csv`
- `exceptions.md`, `ideal_pathway_rules.md`, `ideal_pathway.json`
- `validation_report.txt` (1295/2000 cases follow the ideal pathway)

## Handoff notes for next members
- Use `ideal_pathway.json` directly for conformance checking
  (`allowed_transitions`, `forbidden_transitions`, `activity_to_stage`)
- `allowed_transitions.csv` has a `seen_in_data` column to spot violations quickly
- If activity names change, update the keywords in `STAGES` and rerun the script
