## Alpha Vantage T-Bill ETL - 


### Folder Contents

This folder contains an ETL pipeline container that will retrieve daily T-Bill Rate data from the Alpha Vantage API and then write the data for the last six days to a PostgreSQL database for viewing via Grafana. 

Also contained with this folder are a small series of unit tests for the end to end process, as well as exception handling for sub-processes such as the API call, data parsing/validation and writing data to the database.



#### Implementation 

To run the container you will to need to sign-up for an Alpha Vantage API key and spin up an instance of PostgreSQL or another database to store the data; if you want to use the Slack alerts for pipeline failures, you will need to sign-up for the Slack API and configure a Slack webhook to receive your alerts. You will also need to populate the following environmental variables:

* ALPHA_KEY: Alpha Advantage API Key
* POSTGRES_USER: user name for Postgres connection
* POSTGRES_PASSWORD: password for Postgres
* POSTGRES_PORT: port for Postgres connection
* DB_HOST: ip address/url for Postgres DB Instance
* DASHBOARD_DB: the database this pipeline will be using
* TBILL_TABLE: the table the data will be written to
* BOND_MATURITY: the type of bond the pipeline will pull data for, e.g., '2year' for a two year T-Bill, '10year' for a ten year one. 
* ALERT_WEBHOOK: Slack web hook for sending messages to my pipeline failure channel

The image builds using some common "library files" contained within this folder's parent, namely: the "alpha_vantage_library" and "etl_library" folders. Please refer to the README in the parent folder for instructions on building the image, so you don't run into issues dealing with the Docker build context. 