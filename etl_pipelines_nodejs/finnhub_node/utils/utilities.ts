// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant of the Finnhub Stock Price ETL, pulls down current price data for
// a given stock and then writes it to InfluxDB.

import {InfluxDB} from '@influxdata/influxdb-client';
import axios from 'axios';


interface VarConfig {
    bucket: string;
    finnhubKey: string;
    measurement: string;
    org: string; 
    stock: string;
    token: string;
    url: string;
    webHookUrl: string;
    
  }

const config: VarConfig = {
    
    bucket: process.env.BUCKET as string,
    finnhubKey: process.env.FINNHUB_SECRET as string,
    measurement: process.env.FINNHUB_MEASUREMENT_SPY as string,
    org: process.env.INFLUX_ORG as string,
    stock: process.env.STOCK_SYMBOL as string,
    token: process.env.INFLUX_KEY as string,
    url: process.env.INFLUX_URL as string,
    webHookUrl: process.env.ALERT_WEBHOOK as string,
    
  };

// create InfluxDB client
const createInfluxClient = (bucket: string) => {

    const url = config.url
    const token = config.token
    const org = config.org

    const client = new InfluxDB({url, token})
    console.log('InfluxDB client created')

    return client.getWriteApi(org, bucket, 'ns')

    }

const sendSlackAlerts = (message: string) => {

    const payload = JSON.stringify({"text": message})
        
        axios.post(config.webHookUrl, payload)
            .then(function (response) {
                console.log("Slack message sent successfully with code:", response.status);
        })
        
        .catch(function (error) {
            console.error("Slack message failure with error: ", error.response.statusText);
        });
        
    }


export {config, createInfluxClient, sendSlackAlerts}