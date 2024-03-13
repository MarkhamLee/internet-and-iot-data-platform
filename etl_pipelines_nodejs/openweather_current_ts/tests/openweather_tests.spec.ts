// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down data for current weather
// conditions and writes it to InfluxDB
// TODO: clean up the tests a bit so the console message are written before the tests complete


import { createOpenWeatherUrl, sendSlackAlerts, validateJson } from "../utils/openweather_library";
import { getWeatherData, parseData, writeData } from "../src/main"
import { strict } from 'assert';

// Test end to end
// There will be a couple of logging errors, as the tests will complete before logging finishes. 
// If the test fails an error message (string) is returned.
describe("Full pipeline test", () => {
    it("Pipeline should run, not return a  value", () => {
        
        //baseline endpoint
        const endpoint = "weather?"
        
        // Create URL
        const webUrl = createOpenWeatherUrl(endpoint)

        // Get weather data
        getWeatherData(webUrl)
            .then(result => {
                
            // parse data - finish extraction
            const payload = parseData(result)

            test("Validate Payload was parsed properly", () => {
                // get response code from API call
                expect(validateJson(payload)).rejects.toEqual(0)

            })

            test("Validate that the data was written successfully", () => {
                // write data
                expect(writeData(payload)).toEqual(0)

            })

    })
  })

})



// Bad endpoint/API call - validating that it's caught and error message sent
// Will show an error in console, but shows as passed in the final stats 
describe("API Call - Exception Handling Test", () => {
    it("API Call Should Fail and return error message", () => {
        
        // Create URL
        const webUrl = createOpenWeatherUrl("?cheese")

        // define message 
        const message = "Request failed with status code 401"

        // Get weather data
        getWeatherData(webUrl)
            .then(result => {

                expect(result).toContain(message);
            })
    });

  });


// Validate sending bad data for validation 
describe("Validate data format", () => {
    it("Data format validation should fail", () => {

        const bad_data = {
            "c": 378.85,
            "d": 2.7, 
            "dp": -1.006, 
            "h": 384.3, 
            "l": 377.44, 
            "o": 383.76, 
            "pc": 382.7, 
            "t": 170129160
        }

        //validate data
        expect(validateJson(bad_data)).toEqual(1)

    })

});


// Validate sending Slack Alert
// This is just to generate a message, i.e., this test always passes
// the tester will need to check their Slack messages to verify the message
// went through.
describe("Test Slack Alerts", () => {
    it("Slack Alert Sent Successfully", () => {

        const message = "Test Slack Alert"

        sendSlackAlerts(message)
            .then(result => {
                expect(result).toEqual(200)

            })

    })

});
