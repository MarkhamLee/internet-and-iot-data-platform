### Asana ETL Container


#### Contained in this folder 
Container for connecting to Asana, retrieving data for a particular project and then writing that data to Postgres. The container is built to only track current tasks, so it will erase all the data in the Postgres table before writing new data to it. To run the container you will need to populate the following environmental variables:

* ALERT_WEBHOOK: Slack web hook for sending messages to my pipeline failure channel
* ASANA_TABLE: Postgres table the data will be written to 
* ASANA_KEY: Asana secret/connection key 
* DASHBOARD_DB: the specific database the data will be written to
* DB_HOST: ip address/url for Postgres DB Instance
* GID: Unique ID for the project being tracked 
* PORT: port for Postgres connection
* POSTGRES_USER: user name for Postgres connection
* POSTGRES_PASSWORD: password for Postgres


You will also need to sign-up for [Slack API access](https://api.slack.com/), create a channel for receiving pipeline failures and then generate a web hook for receiving to send those alerts to. Alternatively, if you're just experimenting, you can just comment out the Slack Alert code. 

Additionally, there are several utility files for writing to Postgres, generating container logs and sending pipeline failure alerts via Slack that are pulled in when the container is built from the "etl_library" folder that are in this folder's parent. I.e. to build the container properly you would have to either pull in those files manually and re-write the Dockerfile OR make sure the folder structure is the same. Building Docker containers in this fashion is slightly tricky, and you'll have to run a slightly different Docker build command than usual, please refer to the README.md in the parent "etl_pipeline" folder for details on how to properly build these containers. 

### Notes on Data Quality

* This ETL doesn't have an explicit data validation step, instead three different Python list comprehensions are used to parse data from the pagination object returned by the Asana API. Meaning: if the data isn't in the right format the data will fail, so the data parsing step also serves as the data validation step. 
