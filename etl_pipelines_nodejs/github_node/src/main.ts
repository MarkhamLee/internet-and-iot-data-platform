// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// ETL that uses the GitHub Octokit node.js library to pull Actions data for 
// a given repo from the GitHub API. 
import { Point } from '@influxdata/influxdb-client';
import { Octokit } from 'octokit';
import { config, gitHubActionsData, ghPointData, gitResponse } from '../utils/gh_actions_config'
import {createInfluxClient, sendSlackAlerts}
from "../../common/etlUtilities"


// retrieve data from the GitHub API using the Octokit library
const getGitHubActions = async (gitUrl: string) => {

    try {

        // create Octokit object 
        const octokit = new Octokit({
            auth: config.ghToken
          })

        const data = await octokit.request(gitUrl, { owner: 'MarkhamLee',
        repo: 'finance-productivity-iot-informational-weather-dashboard', 
        headers: {'X-GitHub-Api-Version': '2022-11-28'}
        })

        console.info('Data received from GitHub')

        return data
        
    
    } catch (error: any) {
        const message = "Pipeline failure alert - API Error GitHub Repo Actions"
        console.error(message, error.body)

        //send pipeline failure alert via Slack
        sendSlackAlerts(message, config.webHookUrl)
            .then(result => {
                
                return result
            })
        // this helps us avoid the return type being "type | undefined", which then
        // creates havoc with all the downline methods using that data.
        throw(message)
    }
}

// parse out data - TODO: add exception handling
const parseData = (data: gitHubActionsData) => {

    try {

        return {"status": Number(data['status']),
        "totalActions": Number(data['data']['total_count']),
        "mostRecentAction": String(data['data']['workflow_runs'][0]['name']),
        "mostRecentActionStatus": String(data['data']['workflow_runs'][0]['status']),
        }
        
    } catch (error: any) {

        const message = "GitHub Actions pipeline failureb - data parsing"
        console.error(message)
        
        //send pipeline failure alert via Slack
        sendSlackAlerts(message, config.webHookUrl)
            .then(result => {
                
                return result
            })
        throw(message)
    
    }

}

//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
const writeData = (payload: ghPointData) => {   

    try {

        const writeClient = createInfluxClient(config.bucket, config.url,
            config.token, config.org)
  
        let point = new Point(config.measurement)
                .tag("DevOps Data", "GitHub",)
                .floatField('total_actions', payload.totalActions) 
                .stringField('mostRecentActions', payload.mostRecentAction)
                .stringField('last_action_status', payload.mostRecentAction
                )
                
        // write data to InfluxDB          
        writeClient.writePoint(point)
        writeClient.close().then(() => {
            console.log('Weather data successfully written to InfluxDB')
          })
        
        return 0
        
    } catch (error: any) {

        const message = "GitHub Repo actions pipeline failure - InfluxDB write failure"
        console.error(message, error)


        //send pipeline failure alert via Slack
        sendSlackAlerts(message, config.webHookUrl)
            .then(result => {
                
                return result
            })

        throw(message)

        }    
}

export {getGitHubActions, parseData, writeData}