// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// ETL that uses the GitHub Octokit node.js library to pull Actions data for 
// a given repo from the GitHub API. 
import { Point } from '@influxdata/influxdb-client';
import { Octokit } from 'octokit';
import { config, gitHubActionsData, ghPointData } from '../utils/gh_actions_config'
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
        repo: config.repoName, 
        headers: {'X-GitHub-Api-Version': '2022-11-28'}
        })

        console.info('Data received from GitHub')

        return data
        
    
    } catch (error: any) {
        const message = "Pipeline failure alert - API Error GitHub Repo Actions"
        const fullMessage = message.concat(error)
        console.error(fullMessage)

        //send pipeline failure alert via Slack
        const result = await sendSlackAlerts(fullMessage, config.webHookUrl)
        console.error("Slack alert sent for GitHub Actions Pipeline with code:", result)
        return result

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

        const message = "GitHub Actions pipeline failure - data parsing"
        console.error(message)

        return 1
    
    }

}

//method to write data to InfluxDB
// the InfluxDB node.js library doesn't have a clean way of just
// pushing json data to the DB. So, the write methods will have to 
// live in the primary ETL code for now. 
const writeData = async (payload: ghPointData) => {   

    try {

        const writeClient = createInfluxClient(config.bucket, config.url,
            config.token, config.org)
  
        const point = new Point(config.measurement)
                .tag("DevOps Data", "GitHub",)
                .floatField('total_actions', payload.totalActions) 
                .stringField('mostRecentActions', payload.mostRecentAction)
                .stringField('last_action_status', payload.mostRecentAction
                )
                
        // write data to InfluxDB          
        writeClient.writePoint(point)
        writeClient.close().then(() => {
            console.log('Github Actions data successfully written to InfluxDB')
          })
        
        return 0
        
    } catch (error: any) {

        const message = "GitHub Repo actions pipeline failure - InfluxDB "
        const fullMessage = message.concat(error)
        console.error(fullMessage)

        //send pipeline failure alert via Slack
        const result = await sendSlackAlerts(message, config.webHookUrl)
        console.error("Slack alert sent with code:", result)
        return result

        }    
}

export {getGitHubActions, parseData, writeData}