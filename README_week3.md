# CareFlow - Week 3: Transition Analysis (Member 1)

## Input
- `careflow_event_log_clean_sorted.csv` - columns: `Case_ID`, `Activity_Name`, `Timestamp` (sorted by case, then time)

## Steps (`transition_analysis.py`)
1. **Load** the log, parse timestamps, sort by case and time
2. **Transition counts** (A -> B) with count, cases, average gap -> `transitions.csv`
3. **Start/End activities** and DFG picture -> `start_end_activities.csv`, `dfg_graph.png`
4. **Variants** and frequent paths -> `top_variants.csv`, `top_transitions.csv`
5. **Rare paths** (<1% of cases) + data-error checks -> `rare_paths.csv`
6. **Findings summary** -> `findings_summary.md`

Run: `python transition_analysis.py`

## Outputs
| File | Content |
|---|---|
| transitions.csv | all A -> B transitions with Count, Cases, Avg_Gap_Min |
| start_end_activities.csv | how often each activity starts / ends a case |
| top_variants.csv | top 5 most frequent full paths |
| top_transitions.csv | top 5 most frequent transitions |
| rare_paths.csv | variants/transitions below the 1% threshold |
| dfg_graph.png | directly-follows graph |
| findings_summary.md | top 3 paths, rare paths, unexpected transitions |

## Handoff notes (Member 2 / Member 3)
- **Member 2:** `transitions.csv` has `Avg_Gap_Min` per transition - use it as the starting point for bottleneck / time-gap analysis. Zero-gap transitions are flagged in `findings_summary.md`; treat them as possible logging issues.
- **Member 3:** use `top_variants.csv` and `dfg_graph.png` for visuals / dashboard. `rare_paths.csv` entries need clinician validation before being called errors.
- Rare threshold and TOP_N can be changed at the top of the script (`RARE_THRESHOLD`, `TOP_N`).
- Rework loops (e.g. X-Ray -> Triage) are valid by simulation design; consecutive duplicates and reversed order are likely data errors.
- Requires: `pandas`; `pm4py` + Graphviz only for `dfg_graph.png` (skipped if missing).