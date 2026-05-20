## Quick notes on table creation 

* You'll need the pgcrypto extension to generate the random UUIDs for the monitoring tables. So use the pgcrypto.sql file before you run the two site monitor sql files. 
* You should run the site_monitor_runs.sql file before the site_monitor_target_runs.sql file 
* Run page_watch_current.sql before page_watch_event.sql

