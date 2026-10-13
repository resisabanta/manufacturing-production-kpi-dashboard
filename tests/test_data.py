import pandas as pd
import pytest

from scripts.generate_data import generate_data
from scripts.load_data import read_data, validate_data, get_engine


def test_snapshot_is_valid():
    frames = read_data()
    assert len(frames['work_logs']) == 5475
    assert len(frames['tasks']) == 15


@pytest.mark.parametrize(('table', 'column', 'value', 'error'), [
    ('work_logs', 'worker_id', 'MISSING', 'Unknown reference'),
    ('work_logs', 'actual_hours', -1, 'must be positive'),
    ('work_logs', 'end_time', pd.Timestamp('2024-01-01'), 'Timestamp duration'),
    ('work_logs', 'work_quality', 'UNKNOWN', 'Unknown work quality'),
    ('work_logs', 'team', 'Wrong team', 'teams must match'),
    ('work_logs', 'planned_hours', 99, 'task standard'),
    ('work_logs', 'overtime_hours', float('inf'), 'non-finite'),
    ('tasks', 'planned_hours', 0, 'must be positive'),
])
def test_rejects_invalid_data(table, column, value, error):
    frames = read_data()
    frames[table].loc[0, column] = value
    with pytest.raises(ValueError, match=error):
        validate_data(frames)


def test_rejects_duplicate_log_ids():
    frames = read_data()
    frames['work_logs'].loc[1, 'log_id'] = frames['work_logs'].loc[0, 'log_id']
    with pytest.raises(ValueError, match='duplicate log_id'):
        validate_data(frames)


def test_generator_is_repeatable_and_valid():
    first = generate_data(seed=42, days=3)
    pd.testing.assert_frame_equal(first, generate_data(seed=42, days=3))
    assert not first.equals(generate_data(seed=43, days=3))
    frames = read_data()
    frames['work_logs'] = first
    validate_data(frames)
    assert len(first) == 45


def test_connection_requires_configuration(monkeypatch):
    monkeypatch.delenv('DATABASE_URL', raising=False)
    with pytest.raises(ValueError, match='Set DATABASE_URL'):
        get_engine()
