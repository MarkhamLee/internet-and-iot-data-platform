// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Testing for tracking GitHub actions at the repo level
// TODO: clean-up tear down, refactor main scripts to avoid daisy channing async
// calls, E.g., API fails, then sends message to Slack API, simplify that flow.

import { buildUrl } from "../utils/utilities";
import { config } from '../utils/gh_actions_config'
import { getGitHubActions, parseData, writeData } from "../src/main";
import {createInfluxClient, sendSlackAlerts, validateJson}
from "../../common/etlUtilities"



// End to End Test
describe("GitHub API Full pipeline test", () => {
    it("Pipeline should run and return a payload + a 200 code", () => {

        // base URL 
        const repo = 'finance-productivity-iot-informational-weather-dashboard/'


        // get full URL
        const fullUrl = buildUrl(repo)

        getGitHubActions(fullUrl)
        .then(result => {
            // get the parsed data/
            const payload = parseData(result)
    
            test("Validate Payload was parsed properly", () => {
                // get response code from API call
                expect(payload['status']).toEqual(200)

            })
           
            test("Validate that the data was written successfully", () => {
                // write data
                expect(writeData(payload)).toEqual(0)

            })
        })                
    })
})


// testing failed API call
describe("GitHub failed API call test", () => {

    // base URL 
    const repo = 'not-a-real-repo'

    // get full URL
    const fullUrl = buildUrl(repo)

    test("API call fails and triggers alert message via Slack", () => {

        getGitHubActions(fullUrl)
            .then(result => {
                expect(result).toEqual(200)
            })
    }) 
})

// TODO test exception handling for failed InfluxDB writes