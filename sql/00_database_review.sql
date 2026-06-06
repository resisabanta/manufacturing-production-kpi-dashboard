/*
========================================================
SCRIPT: 00_database_review.sql
PURPOSE:
Review existing tram production database structure.

List Table

issues
supervisors
tasks
work_logs
workers

BUSINESS REASON:
Before building KPI dashboards, an analyst must understand
which tables contain production, worker, time, quality, and team data.
========================================================
*/

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'vw_tram_kpi'
ORDER BY ordinal_position;

SELECT * FROM vw_tram_kpi