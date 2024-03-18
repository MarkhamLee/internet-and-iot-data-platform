// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Testing for the Finnhub ETL 
// TODO: clean-up tear down, refactor main scripts to avoid daisy channing async
// calls, E.g., API fails, then sends message to Slack API, simplify that flow.

import { getFinanceData } from "../src/main"
import {sendSlackAlerts, validateJson} from "../../common/etlUtilities"
import { config, FinnhubSchema } from "../utils/finnhub_config"

// Test end to end
// There will be a couple of logging errors, as the tests will complete before logging finishes. 
describe("Full pipeline test", () => {
    it("Pipeline should run and return 0", () => {
        
        expect(getFinanceData()).toEqual(0)


  });
})

// Validate sending bad data for validation 
describe("Validate data format", () => {
    it("Data format validation should fail", () => {

        const bad_data = {
            "cheese": "cake",
            "wheat": "chex", 
            "turquoise": 5011, 
            "jeeps": 5309, 
        }

        //validate data
        expect(validateJson(bad_data, FinnhubSchema)).toEqual(1)

    })

});


// Validate sending Slack Alert
// This verifies that the proper env var is loaded for the Slack webbhook
// beyond that, you will need to check your Slack channel to verify that
// the message has gone through. 
describe("Test Slack Alerts", () => {
    it("Slack Alert Sent Successfully", () => {

        const message = "Test Slack Alert"

        sendSlackAlerts(message, config.webHookUrl)
            .then(result => {
                expect(result).toEqual(200)

            })

    })

});





