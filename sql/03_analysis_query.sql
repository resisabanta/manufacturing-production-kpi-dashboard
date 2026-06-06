-- =====================================================
-- MANUFACTURING PRODUCTION KPI DASHBOARD
-- BUSINESS ANALYSIS QUERIES
-- =====================================================


-- =====================================================
-- SECTION 1: WORST TASK ANALYSIS
-- Business question:
-- Which production tasks create the highest excess time?
-- =====================================================

SELECT
    item_name,
    category,
    COUNT(*) AS jobs,
    ROUND(AVG(planned_hours), 2) AS avg_planned_hours,
    ROUND(AVG(actual_hours), 2) AS avg_actual_hours,
    ROUND(AVG(excess_time), 2) AS avg_excess_time,
    ROUND(AVG(excess_percent), 2) AS avg_excess_percent
FROM vw_tram_kpi
GROUP BY item_name, category
ORDER BY avg_excess_percent DESC;


-- =====================================================
-- SECTION 2: WORST MODULE ANALYSIS
-- Business question:
-- Which tram module has the worst production efficiency?
-- =====================================================

SELECT
    module,
    COUNT(*) AS jobs,
    ROUND(AVG(excess_time), 2) AS avg_excess_time,
    ROUND(AVG(excess_percent), 2) AS avg_excess_percent
FROM vw_tram_kpi
GROUP BY module
ORDER BY avg_excess_percent DESC;


-- =====================================================
-- SECTION 3: WORKER PERFORMANCE ANALYSIS
-- Business question:
-- Which workers perform best or worst against planned time?
-- =====================================================

SELECT
    worker_name,
    team,
    skill_level,
    COUNT(*) AS jobs,
    ROUND(AVG(excess_time), 2) AS avg_excess_time,
    ROUND(AVG(excess_percent), 2) AS avg_excess_percent,

    COUNT(*) FILTER (WHERE work_quality = 'PASS') AS pass_jobs,
    COUNT(*) FILTER (WHERE work_quality = 'WARNING') AS warning_jobs,
    COUNT(*) FILTER (WHERE work_quality = 'REWORK') AS rework_jobs,
    COUNT(*) FILTER (WHERE work_quality = 'FAIL') AS fail_jobs
FROM vw_tram_kpi
GROUP BY worker_name, team, skill_level
ORDER BY avg_excess_percent ASC;


-- =====================================================
-- SECTION 4: SUPERVISOR PERFORMANCE ANALYSIS
-- Business question:
-- Which supervisors manage teams with better efficiency and quality?
-- =====================================================

SELECT
    supervisor_name,
    team,
    COUNT(*) AS jobs,
    ROUND(AVG(excess_percent), 2) AS avg_excess_percent,

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
GROUP BY supervisor_name, team
ORDER BY avg_excess_percent DESC;


-- =====================================================
-- SECTION 5: OVERTIME DEPENDENCY ANALYSIS
-- Business question:
-- Does overtime reduce or hide production inefficiency?
-- =====================================================

SELECT
    used_overtime,
    COUNT(*) AS jobs,
    ROUND(AVG(overtime_hours), 2) AS avg_overtime_hours,
    ROUND(SUM(overtime_hours), 2) AS total_overtime_hours,
    ROUND(AVG(excess_time), 2) AS avg_excess_time,
    ROUND(AVG(excess_percent), 2) AS avg_excess_percent
FROM vw_tram_kpi
GROUP BY used_overtime
ORDER BY used_overtime;


-- =====================================================
-- SECTION 6: QUALITY DISTRIBUTION
-- Business question:
-- What is the overall quality result distribution?
-- =====================================================

SELECT
    work_quality,
    COUNT(*) AS jobs,

    ROUND(
        COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100,
        2
    ) AS percentage
FROM vw_tram_kpi
GROUP BY work_quality
ORDER BY jobs DESC;


-- =====================================================
-- SECTION 7: QUALITY VS EFFICIENCY MATRIX
-- Business question:
-- Are teams fast but poor quality, or slow but high quality?
-- =====================================================

SELECT
    kpi_status,
    work_quality,
    COUNT(*) AS jobs
FROM vw_tram_kpi
GROUP BY kpi_status, work_quality
ORDER BY kpi_status, jobs DESC;


-- =====================================================
-- SECTION 8: CRITICAL CASE ANALYSIS
-- Business question:
-- Which records require management attention?
-- =====================================================

SELECT
    team,
    supervisor_name,
    worker_name,
    item_name,
    module,
    kpi_status,
    work_quality,
    planned_hours,
    actual_hours,
    excess_time,
    excess_percent,
    overtime_hours
FROM vw_tram_kpi
WHERE kpi_status = 'CRITICAL'
   OR work_quality IN ('REWORK', 'FAIL')
ORDER BY excess_percent DESC;