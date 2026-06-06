-- =====================================================
-- MONTHLY PERFORMANCE TREND ANALYSIS
-- Purpose:
-- Analyze production performance over time.
-- =====================================================

SELECT
    DATE_TRUNC('month', start_time) AS production_month,

    COUNT(*) AS total_jobs,

    ROUND(AVG(planned_hours), 2) AS avg_planned_hours,
    ROUND(AVG(actual_hours), 2) AS avg_actual_hours,

    ROUND(AVG(excess_time), 2) AS avg_excess_time,
    ROUND(SUM(excess_time), 2) AS total_excess_hours,
    ROUND(AVG(excess_percent), 2) AS avg_excess_percent,

    ROUND(SUM(overtime_hours), 2) AS total_overtime_hours,

    COUNT(*) FILTER (WHERE work_quality = 'PASS') AS pass_jobs,
    COUNT(*) FILTER (WHERE work_quality = 'WARNING') AS warning_jobs,
    COUNT(*) FILTER (WHERE work_quality = 'REWORK') AS rework_jobs,
    COUNT(*) FILTER (WHERE work_quality = 'FAIL') AS fail_jobs,

    ROUND(
        COUNT(*) FILTER (WHERE work_quality = 'REWORK')::numeric
        / COUNT(*) * 100,
        2
    ) AS rework_rate,

    ROUND(
        COUNT(*) FILTER (WHERE work_quality = 'FAIL')::numeric
        / COUNT(*) * 100,
        2
    ) AS fail_rate

FROM vw_tram_kpi
GROUP BY production_month
ORDER BY production_month;