# Tram manufacturing dashboard — redesigned project

Open `tram_project.pbip` in Power BI Desktop. Keep both sibling Report and SemanticModel folders beside it. Refresh after opening so the new Reporting Month column and measures use current data. The existing PostgreSQL source remains `localhost`, database `tram_project`; update Data source settings if your installation differs. Credentials are not supplied.

## Pages
1. **Production Overview** — job volume, weighted labor efficiency, positive overrun hours, rework rate, critical jobs; monthly hours and efficiency, team impact and selection-aware summary.
2. **Quality & Rework** — pass/rework/fail rates with job counts, monthly trends, team and task comparisons.
3. **Task Investigation** — tasks ranked by positive overrun impact, with volume, hours and quality evidence. Select a task bar to investigate its teams and tram units. The detail table groups records by task, team and unit; it is not a unique-job audit log.

Month, team and module slicers are synchronized across pages. Reporting Month comes from start_time, formatted YYYY-MM. Quality and KPI status filters are local to Task Investigation. Native page tabs provide navigation. Clear slicers to return to the full dataset.

## Metric definitions
- Overall Efficiency = total planned hours / total actual hours (weighted labor efficiency).
- Average Efficiency % = mean of each job's planned / actual ratio. Jobs with a zero or blank actual denominator return blank and are excluded from this mean.
- Positive Overrun Hours = sum of max(actual - planned, 0) per job.
- Total Excess Hours = total actual - total planned, including early completions.
- Total Overtime Hours retains the imported simulation: hours above 8 per job. This is not measured payroll overtime.
- Quality rates = outcome job count / selected job count. Outcome measures intersect current filters using KEEPFILTERS. No records gives a blank rate, not a misleading zero rate.
- Priority Task identifies the largest positive overrun total in the current context, with alphabetical tie-breaking. It indicates investigation priority, not a causal finding.

All visuals use the fact table. The existing unconnected team scorecard table is retained but not used, so its all-time summaries cannot bypass the new filters. Existing source queries, relationships and automatic date tables remain unchanged. Existing legacy measures/columns remain available for compatibility.

## Validation and limits
Report JSON is checked against Microsoft's published PBIR schemas. All report field references, page bounds and container overlaps are checked. The dashboard PNG previews are rendered from the user-supplied Desktop PDF export. Native visual formatting and DAX execution have not been tested in Power BI Desktop in this environment.

Before publishing: open the project, refresh, check the three pages and synchronized slicers, then check totals against your database. Test a single month/team and a quality selection, and verify the blank-rate behavior for an empty selection. Local model caches are excluded from this repository; refresh the PBIP project after opening. Use the desktop refresh results as authoritative. Synthetic data is suitable for this portfolio demonstration, not operational conclusions.

## Revision 2 — review-driven formatting
Based on the user's Desktop-exported report: split the clipped overview summary into two wrapping callouts; remove crowded monthly column labels; use readable visual field captions; hide duplicate slicer/card labels; include warning rate; enlarge quality and task pages for more table rows and reduce row padding. The detail table is still interactive and may require scrolling. This revision changes the editable PBIP project; the uploaded PBIX and PDF remain unchanged. Reopen the PBIP in Desktop, refresh, then Save As PBIX and export a new PDF. Native rendering of this revision still requires verification.

## Revision 3
Removed the single-color override from the three multi-series comparison charts after reviewing the Desktop export. This restores distinct theme colors for the compared measures. Revision 2 export confirms that the overview text fits and all 15 tasks appear in the summary tables. Detailed records still require interactive scrolling.
