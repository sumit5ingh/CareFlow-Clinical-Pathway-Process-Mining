# CareFlow – Week 3 Dashboard and Data Preparation

## Overview
This week, I prepared a Power BI dashboard for the CareFlow Clinical Pathway Process Mining project. The dashboard presents patient activity waiting times, transition bottlenecks, frequent transitions, and patient pathway patterns.

## Tools Used
- Power BI Desktop
- CSV files generated from process-mining and waiting-time analysis
- Git and GitHub

## Dashboard Visualizations
- Average waiting time by activity
- Top transition bottlenecks
- Average, median, and maximum waiting time comparison
- Most frequent patient transitions
- Common patient pathways
- Start and end activities
- Patient flow graph
- Rare patient pathways
- Transition percentages and average time gaps

## Key Observations
The dashboard helps identify transitions with longer waiting times and pathways that may require further review. Rework loops, such as X-Ray → Triage, should not automatically be classified as errors. Rare pathways and possible logging issues require further validation.

## Deliverables
- `dashboard/CareFlow_Week3_Dashboard.pbix`
- `screenshots/` – Dashboard screenshots
- `README.md` – Dashboard documentation

## Note
The dashboard's results depend on the imported analysis files. The data source and refresh method should be documented accurately.
