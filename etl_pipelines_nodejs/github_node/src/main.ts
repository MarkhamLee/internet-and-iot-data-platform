// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// ETL that uses the GitHub Octokit node.js library to pull Actions data for 
// a given repo from the GitHub API. 
import { Point } from '@influxdata/influxdb-client';
import { Octokit } from 'octokit';
import { config } from '../utils/gh_actions_config'
import {createInfluxClient, sendSlackAlerts, validateJson}
from "../../common/etlUtilities"


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
        const message = "Pipeline failure alert - API Error GitHub Repo Actions"
        // const fullMessage = (message.concat(JSON.stringify((error.response.data))));
        console.error(message, error.body)

        //send pipeline failure alert via Slack
        return sendSlackAlerts(message, config.webHookUrl)
         
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

    try {

        const writeClient = createInfluxClient(config.bucket, config.url,
            config.token, config.org)
  
        let point = new Point(config.measurement)
                .tag("DevOps Data", "GitHub",)
                .floatField('total_actions', payload.totalActions) 
                .stringField('mostRecentActions', payload.mostRecentAction)
                
        // write data to InfluxDB
        void setTimeout(() => {
      
            writeClient.writePoint(point);
            console.log("GitHub actions data successfully written to InfluxDB")
            }, 1000)
      
        // flush client
        void setTimeout(() => {
      
                // flush InfluxDB client
                writeClient.flush()
            }, 1000)

        return 0
        
    } catch (error: any) {

        const message = "GitHub Repo actions pipeline failure - data dashboard, InfluxDB write failure"
        // const fullMessage = (message.concat(JSON.stringify(error.body)))
        console.error(message, error)


        //send pipeline failure alert via Slack
        const slackResponse = sendSlackAlerts(message, config.webHookUrl)
        return slackResponse

    }    
}

export {getGitHubActions, parseData, writeData}