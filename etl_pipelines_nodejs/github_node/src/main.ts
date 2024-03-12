// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node.js - TypeScript version of the Finnhub ETL: pulling down daily stock price data 
// and writing it to InfluxDB.

import { Point } from '@influxdata/influxdb-client';
import { Octokit } from 'octokit';
import {createInfluxClient, sendSlackAlerts} from "../utils/utilities"
import { config } from '../utils/gh_actions_config'


// retrieve data from tehe GitHub API using the Octokit library
const getGitHubActions = async (gitUrl: string) => {

    try {

        // 
        const octokit = new Octokit({
            auth: config.ghToken
          })

        const data = await octokit.request(gitUrl, { owner: 'MarkhamLee',
        repo: 'finance-productivity-iot-informational-weather-dashboard',
            headers: {
            'X-GitHub-Api-Version': '2022-11-28'
            }
        })

        console.info('Data received from GitHub')
        return data
    
    } catch (error: any) {
        const message = "Pipeline failure alert - GitHub Repo Actions - NodeJS Variant with error: "
        const full_message = (message.concat(JSON.stringify((error.response.data))));
        console.error(full_message)

        //send pipeline failure alert via Slack
        const response = sendSlackAlerts(full_message);
        console.debug('Slack message sent with code:', response)
        return {

            "code": 1,
            "slack_response": response
        }
    }
}

// parse out data - TODO: add exception handling
const parseData = (data: any) => {

    return   {"status": Number(data['status']),
            "totalActions": Number(data['data']['total_count']),
            "mostRecentAction": String(data['data']['workflow_runs'][0]['name'])
    }

}

//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
// TODO: add exception handling 
const writeData = (payload: any) => {   

    const bucket = config.bucket
    const writeClient = createInfluxClient(bucket)
  
    let point = new Point(config.measurement)
            .tag("DevOps Data", "GitHub",)
            .floatField('total_actions', payload.totalActions) 
            .stringField('mostRecentActions', payload.mostRecentAction)
            
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

export {getGitHubActions, parseData, writeData}