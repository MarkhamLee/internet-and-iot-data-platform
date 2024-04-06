// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Testing for tracking GitHub actions at the repo level
// TODO: clean-up tear down - doesn't impact tests, but should clean up anyway.
import { buildUrl } from "../utils/utilities";
import { config } from '../utils/gh_actions_config'
import { getGitHubActions, parseData, writeData } from "../src/main";
import {createInfluxClient, sendSlackAlerts }
from "../../common/etlUtilities"

describe("GitHub API Data Retrieval Test", () => {
    it("Succesful API and a data payload that parses successfully", () => {

        // base URL 
        const repo = 'finance-productivity-iot-informational-weather-dashboard/'
        // get full URL
        const fullUrl = buildUrl(repo)

        getGitHubActions(fullUrl)
        .then(result => {
            
            // attempt to parse data and validate fields
            const payload = parseData(result)

            // validate response
            expect(payload).not.toEqual(200)
    
        })          
    })
})

// Test that data writes properly to InfluxDB, the test passes as it's supposed to, 
// but throws a few warnings over tests finishing before logs be written.
describe("Validate data write", () => {
    test("The data should write to InfluxDB successfully", () => {
        
        // define good data payload
         const goodData= {
            totalActions: 280,
            mostRecentAction: "ETL Testing",
            mostRecentActionStatus: "Complete"
          }
        
        expect(writeData(goodData)).toEqual(0)

    })
});

// Validate sending Slack Alert
// This verifies that the proper env var is loaded for the Slack webbhook
// beyond that, you will need to check your Slack channel to verify that
// the message has gone through. 
describe("Test Slack Alerts", () => {
    it("Slack Alert Sent Successfully", async () => {

    // expect.assertions(1)
    
    const message = "Test Slack Alert - GitHub Actions ETL"

    const response = await sendSlackAlerts(message, config.webHookUrl)
    expect(response).toEqual(200) 
    })

});
