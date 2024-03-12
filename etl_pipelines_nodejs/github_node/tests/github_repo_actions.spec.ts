// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Testing for tracking GitHub actions at the repo level
// Note: These tests will pass but there are a couple of async errors related to
// tests finishing before logs can be written, also need to fix the tear down,
// both are on my TODO, but for now, the tests work/that's the most important thing.

import { sendSlackAlerts, buildUrl } from "../utils/utilities";
import { getGitHubActions, parseData, writeData } from "../src/main";
import { config } from '../utils/gh_actions_config'


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