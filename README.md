# Manufacturing Production KPI Dashboard

A manufacturing analytics portfolio by **Resi Sabanta Belanusa**, built around a simulated tram assembly operation. Python, PostgreSQL and Power BI turn job records into an overview of labor efficiency, quality and team performance.

**Business question:** Which production teams and tasks should a supervisor investigate first when labor overruns and rework rise?

![Power BI manufacturing dashboard showing efficiency, rework and labor-hour trends](dashboard/dashboard-preview.png)

[View the dashboard PDF](dashboard/tram_project.pdf) · [Download the Power BI file](tram_project.pbix) · [Read the KPI definitions](docs/methodology.md) · [Editable Power BI project](powerbi/tram_project.pbip)

> All results below describe the committed synthetic 2025 dataset. They are a portfolio demonstration, not measured results or savings from an employer. The previews are rendered from the three-page Power BI export reviewed on 14 October 2026. Overtime is a per-job simulation proxy; positive overruns and net excess hours are shown separately.

## Dashboard pages

| Page | Purpose |
|---|---|
| Production Overview | Compare planned/actual hours, weighted efficiency and team overrun impact |
| Quality & Rework | Compare all four outcomes, monthly rates and task/team counts |
| Task Investigation | Rank tasks by positive overrun hours and inspect team/unit detail |

Month, team and module slicers are configured to synchronize across pages. Reporting uses the job **start month**. Quality and KPI status filters are local to Task Investigation. Outcome measures respect the current filter selection; rates are blank when no records match.

<details>
<summary>Quality and investigation previews</summary>

![Quality and rework dashboard](dashboard/quality-rework.png)

![Task investigation dashboard](dashboard/task-investigation.png)

</details>

The PDF shows all 15 tasks in the summary tables. The detailed-record table is interactive and its PDF export only includes visible rows. See [report definitions and validation notes](docs/powerbi-report.md).

## Results from the committed snapshot

| Metric | Result | Interpretation |
|---|---:|---|
| Job records | 5,475 | 15 generated records per calendar day in 2025 |
| Average job efficiency | 92.14% | Mean of each job's planned / actual hours |
| Aggregate labor efficiency | 88.78% | Total planned / total actual hours; weights jobs by actual hours |
| Average job excess | 11.07% | Mean of each job's (actual − planned) / planned hours |
| Net excess labor | 3,780.09 hours | 33,676.29 actual − 29,896.20 planned hours |
| Rework rate | 13.44% | 736 REWORK records / 5,475 records; FAIL is separate |
| Critical jobs | 226 | Jobs taking more than 150% of planned hours |

Reproduce these figures with [`sql/05_portfolio_summary.sql`](sql/05_portfolio_summary.sql).

| Team | Job records | Average job efficiency | Rework rate |
|---|---:|---:|---:|
| Doors | 872 | 98.50% | 5.85% |
| Electrical | 970 | 93.73% | 13.81% |
| Interior | 922 | 93.07% | 12.91% |
| Exterior | 904 | 91.09% | 13.38% |
| Mechanical | 871 | 90.05% | 14.24% |
| Insulation | 936 | 86.61% | 19.98% |

**Operational interpretation:** Insulation is a candidate for investigation because it combines the lowest average job efficiency with the highest rework rate. A real investigation would compare task mix, standard times, staffing, material availability and defect causes before proposing corrective actions. Doors provides a comparison group, but these rankings do not establish supervisor effectiveness or causation.

## How the project works

1. Reference CSVs describe tasks, workers, supervisors and sample issues.
2. Python validates the CSVs and loads them into typed PostgreSQL tables with primary keys, foreign keys and checks.
3. SQL builds `vw_tram_kpi` at job-record level and `vw_tram_scorecard` at team/supervisor level.
4. Power BI presents monthly trends, quality distributions and production priorities.

The SQL demonstrates CTEs, joins, conditional rules, filtered aggregates and a window function. The Python workflow demonstrates repeatable generation, validation and a transactional refresh. No proprietary production system is needed to run it.

## Run locally

Prerequisites: **Python 3.12**, a running **PostgreSQL 16** server, and optionally Power BI Desktop on Windows. GitHub Actions tests Python 3.12 with PostgreSQL 16.

### 1. Clone and install

```bash
git clone https://github.com/resisabanta/manufacturing-production-kpi-dashboard.git
cd manufacturing-production-kpi-dashboard
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Install dependencies and check the data:

```bash
python -m pip install -r requirements.txt
python scripts/load_data.py --validate-only
```

### 2. Create a dedicated database

Using PostgreSQL's `createdb` command (or create the same empty database in pgAdmin):

```bash
createdb -U postgres tram_portfolio
```

Set the connection for your current terminal, replacing `YOUR_PASSWORD` with your local database password. URL-encode special characters in the username/password. Do not commit real credentials.

```powershell
# Windows PowerShell
$env:DATABASE_URL = "postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/tram_portfolio"
```

```bash
# macOS / Linux
export DATABASE_URL='postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/tram_portfolio'
```

**Upgrading the original project:** use a new empty database such as `tram_portfolio`. Earlier versions created unconstrained tables via pandas. The new loader detects those legacy tables and stops instead of modifying their structure. Keep your original database until you have checked the new one, and repoint Power BI to the new database.

### 3. Load, build and query

```bash
python scripts/load_data.py
python scripts/build_views.py
psql -U postgres -d tram_portfolio -f sql/05_portfolio_summary.sql
```

Expected: **5,475 KPI rows**, **6 scorecard rows**, and the summary figures above. The `psql` command prompts for your PostgreSQL password if required; do not pass the SQLAlchemy `postgresql+psycopg2` URL to `psql`.

Both Python commands can be run again. Loading replaces the rows in the project's five tables in one transaction, preserves existing views, and rolls back on failure. Use this only in the dedicated portfolio database. The scripts locate bundled data relative to their own location, so they also work from another working directory.

For further questions, run `sql/03_analysis_query.sql` and `sql/04_monthly_performance.sql` in pgAdmin or `psql`. `sql/00_database_review.sql` is an inspection script to run **after** creating the views.

### 4. Open Power BI

1. Open `tram_project.pbix` in Power BI Desktop.
2. In **Transform data → Data source settings**, change the PostgreSQL server/database to your local server and `tram_portfolio`.
3. Enter your local database credentials and refresh. If the existing queries specify a database directly, update their Source step in Power Query too.
4. Check the headline metrics against `sql/05_portfolio_summary.sql`.

The `.pbix` and PDF are the latest user-saved Desktop versions. For source edits, open `powerbi/tram_project.pbip` with both sibling folders intact. Its source still points to `localhost` / `tram_project`; change it to your database before refreshing. Local caches and user settings are excluded from version control.

All 51 editable report JSON definitions passed Microsoft schema checks; visual references and page bounds were checked. Desktop PDF exports confirm the layout and distinct comparison colors. Interactive slicer synchronization and a clean database refresh still need a Desktop check. Clear filters to confirm 5,475 jobs for the committed snapshot.

## Generate an alternative dataset

```bash
python scripts/generate_data.py --seed 42 --days 365
```

The default output is `data/work_logs_generated.csv`, leaving the original dashboard snapshot intact. The same seed, inputs and Python environment produce the same generated data. The original snapshot was generated without a recorded seed, so it cannot be recreated exactly by using seed 42.

To intentionally replace the working snapshot and refresh PostgreSQL:

```bash
python scripts/generate_data.py --seed 42 --output data/work_logs_big.csv
python scripts/load_data.py
python scripts/build_views.py
```

Then refresh Power BI and update the published metrics and preview. Results from this alternative dataset will differ from those shown above.

## Validation

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

This runs CSV validation and generator tests. PostgreSQL integration tests skip unless `TEST_DATABASE_URL` points to an **empty, disposable test database**. Set it using the same connection format as `DATABASE_URL`, but a different database name. The integration test refuses a non-empty database and leaves the test tables in place; recreate that disposable database before another integration run.

GitHub Actions supplies a fresh PostgreSQL database and checks the full load → views → reload workflow, SQL analysis queries, published KPI totals, KPI boundaries and rollback after a failed refresh.

## Project structure

```text
├── data/                       # Reference CSVs and committed synthetic snapshot
├── scripts/
│   ├── generate_data.py        # Seeded alternative data generation
│   ├── load_data.py            # Validation and atomic PostgreSQL refresh
│   └── build_views.py          # Build views in dependency order
├── sql/
│   ├── 00_create_schema.sql    # Explicit types, keys and constraints
│   ├── 00_database_review.sql  # Inspect the loaded database
│   ├── 01_create_kpi_view.sql
│   ├── 02_create_scorecard.sql
│   ├── 03_analysis_query.sql
│   ├── 04_monthly_performance.sql
│   └── 05_portfolio_summary.sql
├── dashboard/                  # Three-page PDF, page previews and original flowchart
├── powerbi/                    # Editable PBIP, PBIR report and TMDL model
├── docs/powerbi-report.md       # Report behavior and validation notes
├── docs/methodology.md         # Data grain, formulas and limitations
├── tests/                      # Data and PostgreSQL integration checks
├── .github/workflows/validate.yml
├── tram_project.pbix
├── requirements.txt
└── requirements-dev.txt
```

## Scope and limitations

- A row is one simulated worker/task occurrence, not necessarily one unique completed tram component. Repeated task/unit combinations and overlapping worker assignments are possible.
- `overtime_hours = max(actual_hours − 8, 0)` is a **per-job proxy**. It is not shift attendance or payroll overtime and should not be used for staffing/pay calculations.
- Worker skill and overtime explicitly influence generated quality. Correlations reflect these assumptions and cannot prove real-world causal effects.
- Net excess hours allow early completion to offset overruns. The summary query also exposes positive-only overrun hours.
- Efficiency and quality scores use illustrative thresholds and equal 50/50 weights. They are not a validated employee appraisal system.
- Sample issue records are task-level context, not a defect event history. `materials.csv`, `shifts.csv` and the small `work_logs.csv` are legacy examples excluded from the active pipeline.

See [methodology and data dictionary](docs/methodology.md) for exact definitions and sensible next steps.
