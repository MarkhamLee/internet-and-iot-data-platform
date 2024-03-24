// (C) Markham Lee 2023 - 2024
// finance-productivity-IoT-weather-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node.js - TypeScript version of the Finnhub ETL: pulling down daily stock price data 
// and writing it to InfluxDB.

const finnhub = require('finnhub')
import { Point, InfluxDB, HttpError } from '@influxdata/influxdb-client';
import {createInfluxClient, sendSlackAlerts, validateJson}
from "../../common/etlUtilities"
import { config, FinnhubSchema,
    finnhubPointData, finnhubData } from '../utils/finnhub_config'


const getFinnhubData = async () => {

    const apiKey = finnhub.ApiClient.instance.authentications['api_key']
    apiKey.apiKey = config.finnhubKey 
    const finnhubClient = new finnhub.DefaultApi()

    // get data from the Finnhub API via the Official Finnhub JS library1
   finnhubClient.quote(config.stock, (error: string, data: finnhubData,
        response: unknown) => {
            
            if (error) {
                const message = "Pipeline failure for Finnub ETL (nodejs variant), API failure"
                const fullMessage = message.concat(error)
                console.error(fullMessage)
                //send pipeline failure alert via Slack
                sendSlackAlerts(fullMessage, config.webHookUrl)
                .then(result => {
                    return result 
                })

            } else {
                console.log("Finnhub data received", data)
                return data
                
                // const payload = parseData(data)
                // const resp = writeData(payload)
                // return 0
            }        
        });
        return 0
}

// parse and validate the Finnhub data
const parseData = (data: finnhubData) => {

    // validate data
    const status = validateJson(data, FinnhubSchema)

    if (status == 1) {

        return process.exit()
        
    }

    const payload = {
        "previousClose": Number(data['pc']),
        "open": Number(data['o']),
        "lastPrice": Number(data['l']),
        "change": Number(data['dp'])
    }

    console.log("InfluxDB payload ready", payload)
   
    return payload
}

// method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now - as it will have to be
// customized for each payload.
const writeData = (pointData: finnhubPointData) => {   

    try {

        const writeClient = createInfluxClient(config.bucket, config.url,
            config.token, config.org)

        let point = new Point(config.measurement)
                .tag("Finnhub-API", "stock_prices",)
                .floatField('change', pointData.change) 
                .floatField('last_price', pointData.lastPrice)
                .floatField('open', pointData.open)
                .floatField('previous_close', pointData.previousClose)
                
        // write data to InfluxDB          
        writeClient.writePoint(point)
        writeClient.close().then(() => {
            console.log('Finnhub stock price data successfully written to InfluxDB')
          })
        
        return 0

    } catch (error: any) {

        const message = "OpenWeather API Pipeline Current Weather (Nodejs variant) failure, InfluxDB write error: "
        const fullMessage = (message.concat(JSON.stringify(error.body)));
        console.error(fullMessage);

        //send pipeline failure alert via Slack
        sendSlackAlerts(fullMessage, config.webHookUrl)
            .then(result => {
                return result 
            })
    }

}

export {getFinnhubData, parseData, writeData}