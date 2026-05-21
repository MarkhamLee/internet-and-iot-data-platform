/*

To be extra safe you can run the first command before the second to
verify if you even need to install the pgcrypto extension. Note: pgcrypto
is installed at the DB level (per database), not globally at the
ostgres instance level.

*/  


-- Command to check if the pgcrypto extension has been installed
-- Not necessary, but if you want to be extra careful
select extname from pg_extension where extname = 'pgcrypto';


-- Only run this if the command above doesn't return anything 
create extension if not exists pgcrypto;


-- Once the above command has been run, run the following to make sure generate UUID works
select gen_random_uuid(); 


/*

If the above returns an UUID you're free to run, in order
- site_monitor_runs.sql
- site_monitor_target_runs.sql 

*/