// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Testing for tracking GitHub actions at the repo level
// TODO: clean-up tear down - doesn't impact tests, but should clean up anyway.
import { buildUrl } from "../utils/utilities";
import { config } from '../utils/gh_actions_config'
import { getGitHubActions, parseData, writeData } from "../src/main";
import { sendSlackAlerts }
from "../../common/etlUtilities"

describe("GitHub API Data Retrieval Test", () => {
    it("Succesful API and a data payload that parses successfully", () => {

        // base URL 
        const repo = config.repoName
        // get full URL
        const fullUrl = buildUrl(repo)

        getGitHubActions(fullUrl)
        .then(result => {
            
            // attempt to parse data and validate fields
            const payload = parseData(result)

            // validate response
            expect(payload).not.toEqual(1)
    
        })          
    })
});


// Test that "good data" writes properly to InfluxDB
describe("Validate data write", () => {
    test("The data should write to InfluxDB successfully", async () => {
        
        // define good data payload
         const goodData= {
            totalActions: 280,
            mostRecentAction: "ETL Testing",
            mostRecentActionStatus: "Complete"
          }

        const response = await writeData(goodData)
        expect(response).toEqual(0)

    })
});


// Test InfluxDB type checking, data write should fail and generate a 
// failure alert that's sent via Slack
describe("Validate InfluxDB type checking", () => {
    test("Data write should fail due to data being the wrong type", async () => {
        
        // Cause the test to fail by putting a string in a field expected to be a float
        // note: putting a float in quotes will stil be seen as a float by InfluxDB

        // define bad data payload
         const badData= {
            totalActions: "string", 
            mostRecentAction: "ETL Testing",
            mostRecentActionStatus: "Complete"
          }

        const response = await writeData(badData)
        expect(response).toEqual(200)

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