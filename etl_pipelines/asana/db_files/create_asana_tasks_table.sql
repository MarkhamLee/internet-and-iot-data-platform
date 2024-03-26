CREATE TABLE IF NOT EXISTS asana_data (
  "task_name" text PRIMARY KEY,
  "created" text,
  "last_modified" text,
  "task_age" numeric,
  "task_idle" numeric
) 