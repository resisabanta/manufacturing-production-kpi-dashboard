-- Reproduce the README metrics from the committed 2025 snapshot.
SELECT
    COUNT(*) AS total_jobs,
    ROUND(AVG(planned_hours / NULLIF(actual_hours, 0)) * 100, 2) AS average_job_efficiency_pct,
    ROUND(SUM(planned_hours) / NULLIF(SUM(actual_hours), 0) * 100, 2) AS aggregate_efficiency_pct,
    ROUND(AVG(excess_percent), 2) AS average_excess_pct,
    SUM(planned_hours) AS planned_hours,
    SUM(actual_hours) AS actual_hours,
    SUM(excess_time) AS net_excess_hours,
    SUM(GREATEST(excess_time, 0)) AS positive_overrun_hours,
    SUM(overtime_hours) AS overtime_proxy_hours,
    ROUND(100.0 * COUNT(*) FILTER (WHERE work_quality = 'REWORK') / NULLIF(COUNT(*), 0), 2) AS rework_rate_pct,
    COUNT(*) FILTER (WHERE kpi_status = 'CRITICAL') AS critical_jobs
FROM public.vw_tram_kpi;

SELECT
    team,
    COUNT(*) AS jobs,
    ROUND(AVG(planned_hours / NULLIF(actual_hours, 0)) * 100, 2) AS average_job_efficiency_pct,
    ROUND(100.0 * COUNT(*) FILTER (WHERE work_quality = 'REWORK') / NULLIF(COUNT(*), 0), 2) AS rework_rate_pct
FROM public.vw_tram_kpi
GROUP BY team
ORDER BY average_job_efficiency_pct DESC;
