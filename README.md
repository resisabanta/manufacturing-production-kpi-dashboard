# Manufacturing Production KPI Dashboard

This project is a manufacturing analytics portfolio project based on a simulated tram production environment.

## Project Objective

The objective of this project is to monitor manufacturing performance using PostgreSQL, SQL, Python, and Power BI.

The dashboard analyzes:
- Production efficiency
- Planned vs actual labor hours
- Overtime utilization
- Excess production time
- Rework rate
- Critical production jobs
- Team and supervisor performance

## Tools Used

- PostgreSQL
- SQL
- Python
- pandas
- SQLAlchemy
- Power BI
- VS Code

## Dataset

The dataset was generated using Python to simulate realistic tram manufacturing production data.

Main tables:
- tasks
- work_logs
- workers
- supervisors
- issues

## Key KPIs

- Total Jobs
- Average Efficiency %
- Average Excess %
- Total Overtime Hours
- Total Excess Hours
- Rework Rate
- Critical Jobs

## Dashboard Preview

Add dashboard screenshot here.

## Business Insights

- Doors team achieved the highest production efficiency.
- Insulation recorded the highest rework rate.
- Actual labor hours consistently exceeded planned labor hours.
- The dashboard supports production monitoring, quality analysis, and operational decision-making.

## Project Structure

```text
tram_project/
├── data/
├── scripts/
├── sql/
├── dashboard/
├── requirements.txt
└── README.md