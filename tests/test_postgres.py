"""Integration checks. TEST_DATABASE_URL must point at an empty disposable database."""
import os
from decimal import Decimal

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

from scripts.build_views import build_views
from scripts.load_data import BASE_DIR, load_data, read_data

pytestmark = pytest.mark.integration


@pytest.fixture(scope='module')
def database():
    url = os.environ.get('TEST_DATABASE_URL')
    if not url:
        pytest.skip('Set TEST_DATABASE_URL to an empty disposable PostgreSQL database')
    engine = create_engine(url)
    with engine.connect() as connection:
        count = connection.scalar(text("SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"))
        if count:
            pytest.fail('Integration tests require an EMPTY dedicated database')
    yield engine
    engine.dispose()


def test_full_pipeline_reload_and_rollback(database):
    frames = read_data()
    load_data(database, frames)
    build_views(database)
    # Reload with dependent views present, then rebuild views: both must be repeatable.
    load_data(database, frames)
    build_views(database)
    with database.connect() as connection:
        assert connection.scalar(text('SELECT count(*) FROM vw_tram_kpi')) == 5475
        assert connection.scalar(text('SELECT count(*) FROM vw_tram_scorecard')) == 6
        assert connection.scalar(text("SELECT count(*) FROM vw_tram_kpi WHERE kpi_status='CRITICAL'")) == 226
        assert connection.scalar(text('SELECT sum(excess_time) FROM vw_tram_kpi')) == Decimal('3780.09')
        assert connection.scalar(text("SELECT count(*) FROM vw_tram_kpi WHERE work_quality='REWORK'")) == 736
        for filename in ['00_database_review.sql', '03_analysis_query.sql', '04_monthly_performance.sql', '05_portfolio_summary.sql']:
            connection.exec_driver_sql((BASE_DIR / 'sql' / filename).read_text())
    # Simulate a database-side rule rejecting a valid CSV during insertion.
    with database.begin() as connection:
        connection.exec_driver_sql('ALTER TABLE public.work_logs ADD CONSTRAINT reject_reload CHECK (actual_hours < 1) NOT VALID')
    with pytest.raises(IntegrityError):
        load_data(database, frames)
    with database.begin() as connection:
        assert connection.scalar(text('SELECT count(*) FROM vw_tram_kpi')) == 5475
        assert connection.scalar(text('SELECT sum(excess_time) FROM vw_tram_kpi')) == Decimal('3780.09')
        connection.exec_driver_sql('ALTER TABLE public.work_logs DROP CONSTRAINT reject_reload')
    # Boundary cases: 0%, 25%, 50%, and >50% excess must land in the intended bands.
    with database.connect() as connection:
        transaction = connection.begin()
        connection.exec_driver_sql("""
            INSERT INTO public.work_logs
            (log_id, task_id, worker_id, team, start_time, end_time, actual_hours,
             planned_hours, overtime_hours, tram_unit, work_quality)
            SELECT 'boundary-' || n, 'T001', 'W002', 'Doors', timestamp '2026-01-01',
                   timestamp '2026-01-01' + hours * interval '1 hour', hours, 3, 0, 'TEST', 'PASS'
            FROM (VALUES (1, 3.00), (2, 3.75), (3, 4.50), (4, 4.51)) AS v(n, hours)
        """)
        result = connection.execute(text("SELECT kpi_status FROM vw_tram_kpi WHERE tram_unit='TEST' ORDER BY actual_hours")).scalars().all()
        assert result == ['GOOD', 'NORMAL', 'WARNING', 'CRITICAL']
        transaction.rollback()
