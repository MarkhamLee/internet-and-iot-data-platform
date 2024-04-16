// (C) Markham Lee 2023 - 2024
// finance-productivity-IoT-weather-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node.js - TypeScript version of the Finnhub ETL: pulling down daily stock price data 
// and writing it to InfluxDB.
import axios from 'axios';
import { Point } from '@influxdata/influxdb-client';
import {createInfluxClient, sendSlackAlerts, validateJson}
from "../../common/etlUtilities"
import { config, FinnhubSchema,
    finnhubPointData, finnhubData } from '../utils/finnhub_config'


const getFinnhubData = async (finnhubUrl: string): Promise<finnhubData> => {

        try {
        
            const { data } = await axios.get<finnhubData>(finnhubUrl)
            console.log("OpenWeather API call successful", data)
            return data
    
        } catch (error: any){
    
            const message = "OpenWeather API Pipeline Current Weather (Nodejs variant) failure, API connection error: "
            console.error(message, error.message)
            const result = await sendSlackAlerts(message, config.webHookUrl)
            console.error("Slack alert sent for Finnhub API call error, with code", result)
            throw(error.message)
        }
            
    }

// parse and validate the Finnhub data
const parseData = (data: finnhubData) => {

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
const writeData = async (pointData: any) => {   

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

        const message = "Finnhub (Nodejs) pipeline failure, InfluxDB "
        const fullMessage = message.concat(error)
        console.error(fullMessage);

        //send pipeline failure alert via Slack
        const result = await sendSlackAlerts(message, config.webHookUrl)
        console.error("Slack alert sent with code:", result)
        return result
    }       

}

export {getFinnhubData, parseData, writeData}