// (C) Markham Lee 2023 - 2025
// internet-and-iot-data-platform
// https://github.com/MarkhamLee/internet-and-iot-data-platform
// ETL that uses the GitHub Octokit node.js library to pull Actions data for 
// a given repo from the GitHub API. 
import {getGitHubActions, parseData, writeData } from '../src/main'
import { buildUrl } from '../utils/utilities'
import { sendSlackAlerts} from "../../common/etlUtilities";
import { config } from '../utils/gh_actions_config'


// get full URL
const fullUrl = buildUrl(config.repoName)

// get the raw data
getGitHubActions(fullUrl)
    .then(result  => {

        if (result == 200 ) {
            console.log('Exiting due to API error')
            process.exit()
        }

        // get the parsed data/
        const payload = parseData(result)

        if (payload == 1) {
            const message = "GitHub actions pipeline failure: data parsing"
            sendSlackAlerts(message, config.webHookUrl)
            process.exit()
        }

        console.info('Data parsed successfully', payload)

        // write data
        writeData(payload)
})
