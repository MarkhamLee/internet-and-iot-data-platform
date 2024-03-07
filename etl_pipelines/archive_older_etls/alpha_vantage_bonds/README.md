## Alpha Vantage T-Bill ETL

### Folder Contents

This folder contains an ETL pipeline container that will retrieve the daily T-Bill rate from the Alpha Vantage API, run a SQL query to compare it to what's already present in a PostgreSQL database and provided the retrieved data is newer than what's already in Postgres, write the most recent rate to the DB. The container is expected to be used in conjunction with another process (see Alpha Vantage bond load folder) that would have already loaded several weeks worth of T-Bill data into Postgres.


#### The Data 

* The Alpha Vantage API can provide daily T-Bill rates going back to the mid 70s. For the purposes of this pipeline, only about 2 1/2 years worth of data was loaded via the one-time load process. 
* Alpha Vantage can also provided stock, commodities, economic indicators and a host of other data related to the economy and financial markets, you can read more [here](https://www.alphavantage.co/documentation/).
* The free version of the API is limited to 26 requests per day, so be careful when testing and setup your scheduling accordingly.  

#### Implementation 

To run the container you will to need to sign-up for an Alpha Vantage API key, and spin up an instance of PostgreSQL or another database to store the data, and if you want to use the Slack alerts for pipeline failures, you will need to sign-up for the Slack API and configure a Slack webhook to receive your alerts. You will also need to populate the following environmental variables:

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

