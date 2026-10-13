"""Validate and atomically refresh portfolio tables without dropping dependent views."""
import argparse
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, inspect, text

BASE_DIR = Path(__file__).resolve().parents[1]
TABLES = {
    'supervisors': ('supervisors.csv', 'supervisor_id'),
    'tasks': ('tasks.csv', 'task_id'),
    'workers': ('workers.csv', 'worker_id'),
    'issues': ('issues.csv', 'issue_id'),
    'work_logs': ('work_logs_big.csv', 'log_id'),
}
REQUIRED = {
    'supervisors': 'supervisor_id supervisor_name team',
    'tasks': 'task_id tram_type module item_name item_id category planned_hours priority',
    'workers': 'worker_id worker_name nationality team skill_level experience_years supervisor_id',
    'issues': 'issue_id task_id issue_type severity description',
    'work_logs': 'log_id task_id worker_id team start_time end_time actual_hours planned_hours overtime_hours tram_unit work_quality',
}


def read_data(data_dir=BASE_DIR / 'data'):
    frames = {name: pd.read_csv(Path(data_dir) / filename) for name, (filename, _) in TABLES.items()}
    validate_data(frames)
    return frames


def validate_data(frames):
    for name, (_, key) in TABLES.items():
        frame = frames[name]
        if set(frame.columns) != set(REQUIRED[name].split()):
            raise ValueError(f'{name}: unexpected or missing columns')
        if frame.empty or frame.isna().any().any():
            raise ValueError(f'{name}: empty table or missing values')
        if frame[key].duplicated().any():
            raise ValueError(f'{name}: duplicate {key}')
    tasks, workers, supervisors, logs = (frames[n] for n in ('tasks', 'workers', 'supervisors', 'work_logs'))
    for child, col, parent in [
        (workers, 'supervisor_id', supervisors),
        (logs, 'task_id', tasks), (logs, 'worker_id', workers),
        (frames['issues'], 'task_id', tasks),
    ]:
        if not child[col].isin(parent[col]).all():
            raise ValueError(f'Unknown reference: {col}')
    for frame, columns in [(tasks, ['planned_hours']), (workers, ['experience_years']),
                           (logs, ['actual_hours', 'planned_hours', 'overtime_hours'])]:
        for col in columns:
            frame[col] = pd.to_numeric(frame[col], errors='raise')
            if not frame[col].map(lambda x: float('-inf') < x < float('inf')).all():
                raise ValueError(f'{col}: non-finite values')
    if (tasks.planned_hours <= 0).any() or (logs.planned_hours <= 0).any() or (logs.actual_hours <= 0).any():
        raise ValueError('Planned and actual hours must be positive')
    if (logs.overtime_hours < 0).any() or (logs.overtime_hours > logs.actual_hours).any():
        raise ValueError('Overtime must be between zero and actual hours')
    if (workers.experience_years < 0).any() or (workers.experience_years % 1 != 0).any():
        raise ValueError('Experience years must be non-negative integers')
    if not workers.skill_level.isin(['Junior', 'Mid', 'Senior']).all():
        raise ValueError('Unknown skill level')
    if not logs.work_quality.isin(['PASS', 'WARNING', 'REWORK', 'FAIL']).all():
        raise ValueError('Unknown work quality')
    for col in ['start_time', 'end_time']:
        logs[col] = pd.to_datetime(logs[col], errors='raise')
        if logs[col].isna().any() or logs[col].dt.tz is not None:
            raise ValueError('Timestamps must be valid, timezone-naive simulation times')
    duration = (logs.end_time - logs.start_time).dt.total_seconds() / 3600
    if (duration <= 0).any() or ((duration - logs.actual_hours).abs() > 0.00001).any():
        raise ValueError('Timestamp duration does not match actual hours')
    task_index = tasks.set_index('task_id')
    worker_index = workers.set_index('worker_id')
    supervisor_index = supervisors.set_index('supervisor_id')
    if ((logs.planned_hours - logs.task_id.map(task_index.planned_hours)).abs() > 0.00001).any():
        raise ValueError('Log planned hours differ from the task standard')
    if not (logs.team.eq(logs.task_id.map(task_index.category)) & logs.team.eq(logs.worker_id.map(worker_index.team))).all():
        raise ValueError('Log, task and worker teams must match')
    if not workers.team.eq(workers.supervisor_id.map(supervisor_index.team)).all():
        raise ValueError('Worker and supervisor teams must match')


def get_engine():
    url = os.environ.get('DATABASE_URL')
    if not url:
        raise ValueError('Set DATABASE_URL to your dedicated PostgreSQL portfolio database; see README.md')
    engine = create_engine(url)
    if engine.dialect.name != 'postgresql':
        raise ValueError('This project requires PostgreSQL')
    return engine


def load_data(engine, frames):
    validate_data(frames)
    with engine.begin() as connection:
        inspector = inspect(connection)
        for name, (_, key) in TABLES.items():
            if inspector.has_table(name, schema='public'):
                if inspector.get_pk_constraint(name, schema='public')['constrained_columns'] != [key]:
                    raise ValueError('Legacy tables detected. Use a new empty database as described in README.md.')
        connection.exec_driver_sql((BASE_DIR / 'sql/00_create_schema.sql').read_text())
        # One transaction preserves views and rolls back the entire refresh on failure.
        for name in reversed(TABLES):
            connection.execute(text(f'DELETE FROM public."{name}"'))
        for name in TABLES:
            frames[name].to_sql(name, connection, schema='public', if_exists='append', index=False,
                                method='multi', chunksize=500)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=BASE_DIR / 'data')
    parser.add_argument('--validate-only', action='store_true', help='Check CSV files without a database')
    args = parser.parse_args()
    frames = read_data(args.data_dir)
    if not args.validate_only:
        engine = get_engine()
        try:
            load_data(engine, frames)
        finally:
            engine.dispose()
    print(f"{'Validated' if args.validate_only else 'Loaded'} {len(frames['work_logs']):,} work logs and four reference tables.")


if __name__ == '__main__':
    main()
