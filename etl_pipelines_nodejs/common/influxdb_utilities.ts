// (C) Markham Lee 2023 - 2024
// finance-productivity-IoT-weather-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// InfluXDB utilities for Node.js ETL pipelines

import { InfluxDB } from '@influxdata/influxdb-client';


// define type for write client 

type influxdb = {

    getWriteApi: object
    flush: object
    close: object
    writePoint: object
}



// create InfluxDB client
const createInfluxClient = (bucket: string, url: string,
    token: string, org: string) => {


    const client = new InfluxDB({url, token})
    console.log('InfluxDB client created')

    return client.getWriteApi(org, bucket, 'ns')

}

// write data to InfluxDB
const writeData = (pointData: object, writeClient: influxdb) => {   

  
    // write data to InfluxDB
    void setTimeout(() => {
  
        writeClient.writePoint(pointData);
        console.log("Finnhub stock price data successfully written to InfluxDB")
        }, 1000)
  
    // flush client
    void setTimeout(() => {
  
            // flush InfluxDB client
            writeClient.flush()
        }, 1000)
    
    }

export {createInfluxClient, writeData}