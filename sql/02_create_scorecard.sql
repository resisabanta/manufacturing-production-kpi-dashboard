/*CREATE OR REPLACE VIEW vw_tram_scorecard AS*/

WITH base AS (

SELECT
team,
supervisor_name,

kpi_status,
work_quality,

-- Efficiency scoring
CASE
    WHEN kpi_status = 'GOOD' THEN 100
    WHEN kpi_status = 'NORMAL' THEN 80
    WHEN kpi_status = 'WARNING' THEN 50
    WHEN kpi_status = 'CRITICAL' THEN 20
    ELSE 0
END AS efficiency_score,

-- Quality scoring
CASE
    WHEN work_quality = 'PASS' THEN 100
    WHEN work_quality = 'WARNING' THEN 70
    WHEN work_quality = 'REWORK' THEN 40
    WHEN work_quality = 'FAIL' THEN 10
    ELSE 0
END AS quality_score

FROM vw_tram_kpi

),

scored AS (

SELECT
*,

-- Combined score (weighted)
ROUND(
(efficiency_score * 0.5 + quality_score * 0.5)
,2) AS performance_score

FROM base

),

aggregated AS (

SELECT
team,
supervisor_name,

COUNT(*) AS total_jobs,

ROUND(AVG(performance_score),2) AS avg_score,
ROUND(AVG(efficiency_score),2) AS avg_efficiency,
ROUND(AVG(quality_score),2) AS avg_quality,

-- Quality metrics
COUNT(*) FILTER (WHERE work_quality = 'REWORK') AS rework_jobs,
COUNT(*) FILTER (WHERE work_quality = 'FAIL') AS fail_jobs,

ROUND(
COUNT(*) FILTER (WHERE work_quality = 'REWORK')::numeric
/ COUNT(*) * 100
,2) AS rework_rate,

ROUND(
COUNT(*) FILTER (WHERE work_quality = 'FAIL')::numeric
/ COUNT(*) * 100
,2) AS fail_rate

FROM scored
GROUP BY team, supervisor_name

),

final AS (

SELECT
*,

CASE
    WHEN avg_score >= 85 THEN 'EXCELLENT'
    WHEN avg_score >= 70 THEN 'GOOD'
    WHEN avg_score >= 50 THEN 'WARNING'
    ELSE 'CRITICAL'
END AS overall_status

FROM aggregated

)

SELECT *
FROM final
ORDER BY avg_score DESC;