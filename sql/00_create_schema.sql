-- Use a dedicated portfolio database. Tables persist across reloads.
CREATE TABLE IF NOT EXISTS public.supervisors (
    supervisor_id text PRIMARY KEY,
    supervisor_name text NOT NULL,
    team text NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS public.tasks (
    task_id text PRIMARY KEY,
    tram_type text NOT NULL,
    module text NOT NULL,
    item_name text NOT NULL,
    item_id text NOT NULL,
    category text NOT NULL,
    planned_hours numeric(12,2) NOT NULL CHECK (planned_hours > 0),
    priority text NOT NULL
);
CREATE TABLE IF NOT EXISTS public.workers (
    worker_id text PRIMARY KEY,
    worker_name text NOT NULL,
    nationality text NOT NULL,
    team text NOT NULL,
    skill_level text NOT NULL CHECK (skill_level IN ('Junior', 'Mid', 'Senior')),
    experience_years integer NOT NULL CHECK (experience_years >= 0),
    supervisor_id text NOT NULL REFERENCES public.supervisors(supervisor_id)
);
CREATE TABLE IF NOT EXISTS public.issues (
    issue_id text PRIMARY KEY,
    task_id text NOT NULL REFERENCES public.tasks(task_id),
    issue_type text NOT NULL,
    severity text NOT NULL,
    description text NOT NULL
);
CREATE TABLE IF NOT EXISTS public.work_logs (
    log_id text PRIMARY KEY,
    task_id text NOT NULL REFERENCES public.tasks(task_id),
    worker_id text NOT NULL REFERENCES public.workers(worker_id),
    team text NOT NULL,
    start_time timestamp NOT NULL,
    end_time timestamp NOT NULL CHECK (end_time > start_time),
    actual_hours numeric(12,2) NOT NULL CHECK (actual_hours > 0),
    planned_hours numeric(12,2) NOT NULL CHECK (planned_hours > 0),
    overtime_hours numeric(12,2) NOT NULL CHECK (overtime_hours BETWEEN 0 AND actual_hours),
    tram_unit text NOT NULL,
    work_quality text NOT NULL CHECK (work_quality IN ('PASS', 'WARNING', 'REWORK', 'FAIL'))
);
CREATE INDEX IF NOT EXISTS work_logs_start_time_idx ON public.work_logs(start_time);
CREATE INDEX IF NOT EXISTS work_logs_task_id_idx ON public.work_logs(task_id);
CREATE INDEX IF NOT EXISTS work_logs_worker_id_idx ON public.work_logs(worker_id);
