## Singular ETL Component -  Work in Progress/Experiment

Experimenting Breaking down ETLs into smaller components, this container just retrieves the weather data and then saves it in the container so that it can be picked up by the Orchestration tool - we're using .airflow/return.json as that's the Airflow format, but I should be able to adopt that to Argo Workflow. Next step will be to write a "db write" container that just receives a json and writtes it to a database. This should enable adding new ETLs to be a lot faster, plus make it easier to practice/experiment with writing parts of pipelines in languages other than Python. 

