### Key Setup Notes

* If you arrange your dags into sub-folders like I do, you'll need to reference your python scripts as folder_name.module_name e.g,, if you're importing a script of common functions you wrote called common_methods.py you'd have to import it as folder_name.common_methods 
* I store all my key constants, variables, keys, etc., in the Airflow key-value store as environmental variables, but for testing/re-use you could always just use a secrets.py or similar file instead. 