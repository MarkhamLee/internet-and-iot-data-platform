// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node.js - TypeScript version of the Finnhub ETL: pulling down daily stock price data 
// and writing it to InfluxDB.

const finnhub = require('finnhub')
import { Point } from '@influxdata/influxdb-client';
import {config, createInfluxClient, sendSlackAlerts, validateJson} from "../utils/utilities"


const getFinanceData = () => {

    const apiKey = finnhub.ApiClient.instance.authentications['api_key']
    apiKey.apiKey = config.finnhubKey 
    const finnhubClient = new finnhub.DefaultApi()

    // get data from the Finnhub API via the Official Finnhub JS library1
    finnhubClient.quote(config.stock, (error: any, data: any, response: any) => {
            
            if (error) {
                const message = "Pipeline failure for Node.js version of Finnhub Stock Price ETL, with error:"
                const fullMessage = message.concat(error)
                console.error(fullMessage)
                sendSlackAlerts(fullMessage)
                // exit process
                return process.exit()

            } else {

                console.log("Finnhub data received")
                const payload = parseData(data)
                writeData(payload)
                

            }        
        });
    return 0
}

// parse and validate the Finnhub data
const parseData = (data: any) => {

    // validate data
    const status = validateJson(data)

    if (status == 1) {

        return process.exit()
        
    }

    const payload = {
        "previous_close": Number(data['pc']),
        "open": Number(data['o']),
        "last_price": Number(data['l']),
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
const writeData = (payload: any) => {   

    const bucket = config.bucket
    const writeClient = createInfluxClient(bucket)
  
    let point = new Point(config.measurement)
            .tag("Finnhub-API", "stock_prices",)
            .floatField('change', payload.change) 
            .floatField('last_price', payload.last_price)
            .floatField('open', payload.open)
            .floatField('previous_close', payload.previous_close)
            
    // write data to InfluxDB
    void setTimeout(() => {
  
        writeClient.writePoint(point);
        console.log("Finnhub stock price data successfully written to InfluxDB")
        }, 1000)
  
    // flush client
    void setTimeout(() => {
  
            // flush InfluxDB client
            writeClient.flush()
        }, 1000)
    
    }

export {getFinanceData, parseData, writeData}