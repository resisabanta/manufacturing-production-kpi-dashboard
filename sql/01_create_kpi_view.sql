/*CREATE OR REPLACE VIEW vw_tram_kpi AS*/
WITH source AS (

SELECT
t.task_id,
t.item_name,
t.module,
t.category,
t.planned_hours,

w.worker_id,
w.worker_name,
w.team,
w.skill_level,

wl.start_time,
wl.end_time,
wl.overtime_hours,
wl.tram_unit,
wl.work_quality,

s.supervisor_name

FROM tasks t
JOIN work_logs wl
    ON t.task_id = wl.task_id
JOIN workers w
    ON wl.worker_id = w.worker_id
JOIN supervisors s
    ON w.supervisor_id = s.supervisor_id
),

clean AS (

SELECT
task_id,
item_name,
module,
category,
planned_hours::numeric AS planned_hours,

worker_id,
worker_name,
supervisor_name,
team,
skill_level,

start_time::timestamp AS start_time,
end_time::timestamp   AS end_time,

COALESCE(overtime_hours,0)::numeric AS overtime_hours,
tram_unit,
work_quality

FROM source

),

calc AS (

SELECT
*,

(
EXTRACT(EPOCH FROM (end_time - start_time)) / 3600
)::numeric AS actual_hours,

(
(EXTRACT(EPOCH FROM (end_time - start_time)) / 3600)
- planned_hours
)::numeric AS excess_time

FROM clean

),

business_rules AS (

SELECT
*,


CASE
    WHEN planned_hours = 0 THEN NULL
    ELSE ((excess_time / planned_hours) * 100)::numeric
END AS excess_percent,

CASE
    WHEN excess_time <= 0 THEN 'GOOD'
    WHEN excess_time <= planned_hours * 0.25 THEN 'NORMAL'
    WHEN excess_time <= planned_hours * 0.50 THEN 'WARNING'
    ELSE 'CRITICAL'
END AS kpi_status,

CASE
    WHEN overtime_hours > 0 THEN 'YES'
    ELSE 'NO'
END AS used_overtime

FROM calc

),

final AS (

SELECT
task_id,
item_name,
module,
category,

worker_name,
supervisor_name,
team,
skill_level,
tram_unit,

start_time,
end_time,

ROUND(planned_hours,2) AS planned_hours,
ROUND(actual_hours,2) AS actual_hours,
ROUND(excess_time,2) AS excess_time,
ROUND(excess_percent,2) AS excess_percent,
ROUND(overtime_hours,2) AS overtime_hours,

kpi_status,
used_overtime,
work_quality

FROM business_rules

)

SELECT *
FROM final
ORDER BY excess_percent DESC;