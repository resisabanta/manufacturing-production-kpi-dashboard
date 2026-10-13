"""Generate a deterministic alternative dataset; the original snapshot is preserved by default."""
import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]


def generate_data(seed=42, days=365):
    if days < 1:
        raise ValueError("days must be positive")
    rng = random.Random(seed)
    # ======================
    # LOAD DATA
    # ======================
    tasks = pd.read_csv(BASE_DIR / "data/tasks.csv")
    workers = pd.read_csv(BASE_DIR / "data/workers.csv")
    tasks["team"] = tasks["category"]
    # group by team
    workers_by_team = {
        team: df.to_dict("records")
        for team, df in workers.groupby("team")
    }

    tasks_by_team = {
        team: df.to_dict("records")
        for team, df in tasks.groupby("team")
    }

    # ======================
    # CONFIG
    # ======================
    start_date = datetime(2025, 1, 1)
    rows = []
    log_id = 1

    # ======================
    # FUNCTIONS
    # ======================

    def get_efficiency_multiplier(skill):
        """Skill affects working speed"""
        if skill == "Senior":
            return rng.uniform(0.85, 1.1)
        elif skill == "Mid":
            return rng.uniform(0.9, 1.3)
        else:  # Junior
            return rng.uniform(1.0, 1.6)


    def generate_quality(skill, overtime):
        """Quality depends on skill + overtime"""

        base = {
            "Senior": {"PASS": 0.8, "WARNING": 0.15, "REWORK": 0.04, "FAIL": 0.01},
            "Mid": {"PASS": 0.65, "WARNING": 0.2, "REWORK": 0.12, "FAIL": 0.03},
            "Junior": {"PASS": 0.5, "WARNING": 0.25, "REWORK": 0.2, "FAIL": 0.05}
        }

        probs = base[skill].copy()

        # penalty if overtime high
        if overtime > 2:
            probs["PASS"] -= 0.1
            probs["REWORK"] += 0.07
            probs["FAIL"] += 0.03

        # normalize
        total = sum(probs.values())
        for k in probs:
            probs[k] /= total

        r = rng.random()
        cumulative = 0
        for status, prob in probs.items():
            cumulative += prob
            if r <= cumulative:
                return status

        return "PASS"


    # ======================
    # MAIN LOOP
    # ======================

    for day in range(days):
        current_day = start_date + timedelta(days=day)

        for _ in range(15):

            # Choose a team first
            team = rng.choice(list(tasks_by_team.keys()))

            # Choose a worker and task from the same team
            worker = rng.choice(workers_by_team[team])
            task = rng.choice(tasks_by_team[team])

            planned = float(task["planned_hours"])

            # efficiency based on skill
            multiplier = get_efficiency_multiplier(worker["skill_level"])
            actual = round(planned * multiplier, 2)

            # working time
            start_hour = rng.randint(6, 13)
            start_min = rng.randint(0, 59)

            start_time = current_day.replace(hour=start_hour, minute=start_min)
            end_time = start_time + timedelta(hours=actual)

            # Per-job proxy, not payroll overtime; see docs/methodology.md.
            overtime = max(0, actual - 8)

            # quality based on skill + overtime
            work_quality = generate_quality(worker["skill_level"], overtime)

            rows.append({
                "log_id": f"L{log_id:07}",
                "task_id": task["task_id"],
                "worker_id": worker["worker_id"],
                "team": team,
                "start_time": start_time,
                "end_time": end_time,
                "actual_hours": actual,
                "planned_hours": planned,
                "overtime_hours": round(overtime, 2),
                "tram_unit": f"UNIT{rng.randint(1,200):03}",
                "work_quality": work_quality
            })

            log_id += 1


    return pd.DataFrame(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--days", type=int, default=365)
    parser.add_argument("--output", type=Path, default=BASE_DIR / "data/work_logs_generated.csv")
    args = parser.parse_args()
    frame = generate_data(args.seed, args.days)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False)
    print(f"Generated {len(frame):,} rows with seed {args.seed}: {args.output}")


if __name__ == "__main__":
    main()
