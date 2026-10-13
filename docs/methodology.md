# Methodology and data dictionary

## Data grain and joins

| Table | Key | Meaning | Relationship |
|---|---|---|---|
| `supervisors` | `supervisor_id` | One supervisor and unique team | Referenced by workers |
| `workers` | `worker_id` | One simulated worker | Many workers per supervisor |
| `tasks` | `task_id` | Task standard and planned labor hours | Referenced by logs and sample issues |
| `work_logs` | `log_id` | One simulated worker/task occurrence | Many logs per task and worker |
| `issues` | `issue_id` | A sample issue associated with a task | Not joined into KPI calculations |

`vw_tram_kpi` joins logs → tasks, logs → workers, workers → supervisors. Keys prevent these joins from multiplying valid log records. The loader verifies that log, task, worker and supervisor teams agree. Joining task-level issues directly to logs could duplicate job records, so they are excluded from KPI totals.

Log IDs remain in the base table; the existing KPI view column layout is retained for compatibility with the Power BI project. The `planned_hours` used in the KPI view comes from the task standard; validation checks that the duplicate value in the CSV agrees.

## KPI definitions

| Metric | Definition | Notes |
|---|---|---|
| Actual hours | `(end_time − start_time)` in hours | SQL derives duration from timestamps |
| Excess time | `actual_hours − planned_hours` | May be negative |
| Excess percentage | `100 × excess_time / planned_hours` | Planned hours must be positive |
| Job efficiency | `100 × planned_hours / actual_hours` | Can exceed 100%; durations must be positive |
| Average job efficiency | Mean of job efficiencies | Each job has equal weight |
| Aggregate efficiency | `100 × SUM(planned_hours) / SUM(actual_hours)` | Equivalent to actual-hour-weighted job efficiency |
| Net excess hours | `SUM(excess_time)` | Underruns offset overruns |
| Positive overrun hours | `SUM(GREATEST(excess_time, 0))` | No offsets from underruns |
| Rework rate | `100 × count(REWORK) / count(all jobs)` | FAIL and WARNING are separate categories |
| Fail rate | `100 × count(FAIL) / count(all jobs)` | Not included in rework rate |
| Overtime proxy | `max(actual_hours − 8, 0)` for each job | Does not aggregate worker shifts or account for overlapping work |

The preview's 92.14% efficiency is the average of per-job ratios. The 88.78% aggregate ratio answers a different question: how much planned labor was earned per actual labor hour across the complete dataset. Neither should be substituted silently for the other. Monthly aggregate efficiency should also be calculated from monthly sums, not averaged from daily percentages.

The SQL KPI view rounds row-level durations and percentages to two decimals. Summary queries use those published row values, matching the existing dashboard convention.

## Classification and scoring

| KPI status | Excess relative to planned time | Efficiency score |
|---|---|---:|
| GOOD | ≤ 0% | 100 |
| NORMAL | > 0% and ≤ 25% | 80 |
| WARNING | > 25% and ≤ 50% | 50 |
| CRITICAL | > 50% | 20 |

| Quality result | Quality score |
|---|---:|
| PASS | 100 |
| WARNING | 70 |
| REWORK | 40 |
| FAIL | 10 |

Each job's composite score is `0.5 × efficiency_score + 0.5 × quality_score`. The scorecard averages job scores per team/supervisor. Overall status uses the rounded team average: EXCELLENT ≥85, GOOD ≥70, WARNING ≥50, otherwise CRITICAL. These points are illustrative business rules; an 80-point efficiency score is not 80% physical efficiency.

## Simulation assumptions

- The committed dataset covers 1 January–31 December 2025 with 15 records per calendar day, including weekends and holidays.
- Tasks and workers are sampled from the same team. A worker can be selected multiple times and assignments can overlap; there is no shift calendar or resource scheduling model.
- Actual task duration is a random multiplier of planned hours. Senior, Mid and Junior categories have different multiplier ranges.
- Quality outcomes are sampled with skill-specific probabilities. The overtime proxy above two hours reduces PASS probability and increases REWORK/FAIL probability by construction.
- Tram unit IDs are randomly selected, without tracking a full assembly sequence or unique task completion.
- Timestamps are timezone-naive simulation values. The calculation assumes continuous work, without breaks or handover effects.
- The existing snapshot has no recorded random seed. New generator runs use an explicit seed and write to a separate filename by default.

These assumptions explain patterns in the dataset. They do not establish real productivity differences between nationalities, workers, teams or supervisors. Nationality is not used in KPI formulas or generation probabilities.

## Interpreting the snapshot

Doors has the highest average job efficiency (98.50%) and lowest rework rate (5.85%). Insulation has the highest rework rate (19.98%) and lowest average job efficiency (86.61%). A useful next analysis would control for task, planned duration and skill mix before attributing differences to a process or team.

Potential real-world actions would begin with validating standard times, checking quality event records and investigating recurring material/tooling delays. No financial savings, root causes or production improvements are claimed from this synthetic dataset.

## Next extensions

1. Add shift calendars and non-overlapping assignments, then calculate overtime per worker/shift.
2. Add defect events keyed to a unique job, with rework duration and reason codes.
3. Compare like-for-like tasks and skill mix; show sample sizes alongside rankings.
4. Add historical task standards so changing a standard does not rewrite past performance.
5. Re-export the Power BI report with explicit labels for net excess and overtime proxy after updating the model in Desktop.
