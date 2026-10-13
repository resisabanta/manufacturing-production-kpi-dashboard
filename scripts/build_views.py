"""Build KPI and scorecard views in dependency order, in one transaction."""
from pathlib import Path

try:
    from .load_data import get_engine
except ImportError:
    from load_data import get_engine

BASE_DIR = Path(__file__).resolve().parents[1]


def build_views(engine):
    with engine.begin() as connection:
        connection.exec_driver_sql('SET LOCAL search_path TO public')
        for filename in ['01_create_kpi_view.sql', '02_create_scorecard.sql']:
            connection.exec_driver_sql((BASE_DIR / 'sql' / filename).read_text())


if __name__ == '__main__':
    engine = get_engine()
    try:
        build_views(engine)
    finally:
        engine.dispose()
    print('Created vw_tram_kpi and vw_tram_scorecard.')
