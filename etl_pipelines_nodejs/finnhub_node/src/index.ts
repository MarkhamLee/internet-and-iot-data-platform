// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node.js - TypeScript version of the Finnhub ETL: pulling down daily stock price data 
// and writing it to InfluxDB.

import { Point } from '@influxdata/influxdb-client';
import finnhub from 'finnhub'
import {config, createInfluxClient, sendSlackAlerts} from "../utils/utilities"

const api_key = finnhub.ApiClient.instance.authentications['api_key'];
api_key.apiKey = config.finnhubKey 
const finnhubClient = new finnhub.DefaultApi()


finnhubClient.quote(config.stock, (error: any, data: any, response: any) => {
    
    if (error) {
        console.error(error)

    } else {
        console.log(data)

        const payload = {
            "previous_close": Number(data['pc']),
            "open": Number(data['o']),
            "last_price": Number(data['l']),
            "change": Number(data['dp'])
        }
            
        writeData(payload)


    }        


});

//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
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
        console.log("Weather data successfully written to InfluxDB")
        }, 1000)
  
  
    // flush client
    void setTimeout(() => {
  
            // flush InfluxDB client
            writeClient.flush()
        }, 1000)
    
    }
  