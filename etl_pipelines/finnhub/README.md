### Finnhub ETL container 

#### What's here?
A container for pulling stock price data from the Finnhub API and then writing that data to InfluxDB. 

#### The Data 
The Finnhub API provides the folowing data points:

* c: current price
* d: change in USD
* dp: percent change
* h: high price of the day
* l: low price of the day
* o: open price of the day
* pc: previous close price

The "stock_prices_payload.json" file is used to validate the payload that comes back from the API, as far as ensuring it has the right fields and the right data type in each field. 

You can read more about the Finnhub Stock Price API [here](https://finnhub.io/docs/api/quote)

#### Data Quality & Testing
* The json validate library is used to ensure that the returned data payload is correct in terms of the right fields being present, and the data in those fields being the right data type. This is critical as InfluxDB has tight type checking and once a field has been written in a particular format e.g., a float, subsequent writes of a different data type will be rejected, e.g.,an integer. 
* The test.py file will run a series of unit tests, checking both primary and secondary functionality:
    * The end to end ETL workflow, if any part of the process fails, the entire test fails 
    * Validating that the appropriate error messages and alerts are sent in response to a bad or failed API call
    * Testing the data validation process, i.e, comparing a provided "bad" data payload with the ETL's JSON schema, followed by checking that the appropriate error messages and alerts are generated. 
* Alerts are sent via Slack related to any "pipeline failure issue", whether it's an API call failing, data validation failing, DB write issues, etc.


#### Deployment
To deploy/run/use the container you will need to sign-up for the Finnhub API and get an API key, you're able to hit the API 60/second with the free version, which should be sufficient for most personal use cases. Additionally, please make note that the container uses the finnuhb python library, so you'll need to install that into your python virtual environment if you plan to use this outside of a Docker container. Finally, if you want to receive broken pipeline/pipeline error alerts, you'll need to sign up for the Slack API, and then configure a channel and a wehbhook for receiving messages. 

The container requires the following environmental variables, when I deployed this on my Kubernetes cluster I used config maps and Kubernetes secrets for all of them. 

* ALERT_WEBHOOK: webhook to send pipeline failure alerts to Slack 
* BUCKET: InfluxDB's term for a database 
* FINNHUB_SECRET: Finnhub API key
* FINNHUB_MEASUREMENT_SPY: basically the table in InfluxDB you'll be storing data in.
* INFLUX_KEY: API key for InfluxDB 
* INFLUX_ORG: org name for your InfluxDB instance 
* INFLUX_URL: ip address or URL for your InfluxDB instance 
* STOCK_SYMBOL: Symbol for the stock you want to retrieve data for 


As with all of my ETL containers, this container pulls files from various library folders as part of the build process, which requires a slightly different Docker build command to ensure the build process has access to all the required files. Please refer to the README file in the parent folder/etl_pipeline folder for more details.