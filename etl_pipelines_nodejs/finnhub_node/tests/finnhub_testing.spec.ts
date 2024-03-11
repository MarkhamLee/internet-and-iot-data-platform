// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Testing for the Finnhub ETL 

import { strict } from 'assert';
import { sendSlackAlerts, validateJson } from "../utils/utilities";
import { getFinanceData } from "../src/main"

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
        expect(validateJson(bad_data)).toEqual(1)

    })

});


// Validate sending Slack Alert
// This is just to generate a message, i.e., this test always passes
// the tester will need to check their Slack messages to verify the message
// went through.
describe("Validate Slack Alerts", () => {
    it("Slack alert should be received successfully", () => {

        const message = "Test Slack Alert"

        //validate data
        expect(sendSlackAlerts(message)).toBeUndefined()

    })

});






