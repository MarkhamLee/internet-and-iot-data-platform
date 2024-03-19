// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// ETL that uses the GitHub Octokit node.js library to pull Actions data for 
// a given repo from the GitHub API. 
import {getGitHubActions, parseData, writeData } from '../src/main'
import { buildUrl } from '../utils/utilities'
import { config, gitHubActionsData, ghPointData } from '../utils/gh_actions_config'

// base URL 
const repo = 'finance-productivity-iot-informational-weather-dashboard/'

// get full URL
const fullUrl = buildUrl(repo)
console.log(fullUrl)

// get the raw data
getGitHubActions(fullUrl)
    .then(result   => {

        // get the parsed data/
        const payload = parseData(result)
        console.info('Data parsed successfully', payload)

        // write data
        writeData(payload)
})
