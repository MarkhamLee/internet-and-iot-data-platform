## Finnhub Stock ETL

### Folder Contents 

A Docker ETL container/bot that monitors the [Raspberry Pi locator](https://rpilocator.com/) RSS feed for data/alerts on when online retailers have Raspberry Pi 5 single board computers in stock, and then notifies me via Slack if those updates are less than 24 hours old. It's worth noting that the Raspberry Pi Locator web site displays data on all Raspberry Pi products, but I'm using a pre-filtered URL to only consume data on Raspberry Pi 5 devices. The basic steps/work flow is as follows:

1) Consume the latest RSS feed 
2) If the feed has current entries it will then check the age of those entries vs the current time, and if those entries are younger than a user defined maximum age (I use 24 hours), it will do the following:
    1) Save the data to PostgreSQL so the data shows up on my personal dashboard 
    2) Send me an alert via Slack 
3) If the feed doesn't have entries younger than than the max age, I won't get an alert AND the container will clear out the Postgres table so I'm not being shown data for devices that are probably no longer available. 

I went with a 24-hour max age due to how quickly the devices sell out. 

An item on my to do list is to build a version of this that just sends Slack alerts and doesn't have the Postgres dependency. I.e., build a simpler version that's easier for people to just pick up and use. 

### Deployment 

To deploy this you'll need to do the following:
1) Go to the Raspberry Pi locator web site, go to the RSS section and configure a URL that tracks the products you're interested in. 
2) Sign up for the Slack API, configure a channel for the alerts, and setup a web hook that can receive messages for that channel. 
3) Setup a Postgres instance OR comment out the code/modify the code so it just sends alerts without saving the data. 

Alternatively, you could go into the general ETL folder, and use the Jupyter Notebook I used to prototype the code for this container  as a starting point to build your own bot/etl pipeline per your own specifications/implementation needs. 

The key environmental variables are as follows:

* DASHBOARD_DB: the specific database the data will be written to
* DB_HOST: ip address/url for Postgres DB Instance
* LOCATOR_URL: your pre-filterd RSS feed URL as described above 
* MIN_AGE: expressed in hours, any stock data older than this number will be ignored
* PORT: port for Postgres connection
* POSTGRES_USER: user name for Postgres connection
* POSTGRES_PASSWORD: password for Postgres
* RPI5_TABLE: table the Raspberry Pi stock data will be written to
* WEBHOOK: Slack web hook for receiving alerts 

As with all of my ETL containers, this container pulls files from various library folders as part of the build process, which requires a slightly different Docker build command to ensure the build process has access to all the required files. Please refer to the README file in the parent folder/etl_pipeline folder for more details.

Note: unlike most of my ETL containers I didn't add a function to generate Slack alerts for pipeline failures, the reason for is that is it's fairly common for their to be error or the locator to be temporarily unavailable. I.e., the pipeline fails regularly and the exception handling is able to deal with it gracefully, so there is no need to send myself unecessary alerts for things I can't directly influence/fix.  