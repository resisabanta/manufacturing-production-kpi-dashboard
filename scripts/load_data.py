import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

# detect project root safely
BASE_DIR = Path(__file__).resolve().parents[1]

# data folder
DATA_DIR = BASE_DIR / "data"

# PostgreSQL connection
engine = create_engine("postgresql+psycopg2://postgres:abcd@localhost:5432/tram_project")

# read csv files
tasks = pd.read_csv(DATA_DIR / "tasks.csv")
workers = pd.read_csv(DATA_DIR / "workers.csv")
logs = pd.read_csv(DATA_DIR / "work_logs_big.csv")
issues = pd.read_csv(DATA_DIR / "issues.csv")
supervisors = pd.read_csv(DATA_DIR / "supervisors.csv")
# upload to postgres
tasks.to_sql("tasks", engine, if_exists="replace", index=False)
workers.to_sql("workers", engine, if_exists="replace", index=False)
logs.to_sql("work_logs", engine, if_exists="replace", index=False)
issues.to_sql("issues", engine, if_exists="replace", index=False)
supervisors.to_sql("supervisors", engine, if_exists="replace", index=False)

print("Data loaded successfully")