// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down data for current weather
// conditions and writes it to InfluxDB
// These tests aren't mocked and either run the actual pipeline or test out certain
// features like writing data, validating data, sending out alerts, etc., so that we
// can be sure a valid test here = the ETL will work in real life/production.
// TODO: clean up the tests a bit so the console message are written before the tests complete


import { createOpenWeatherUrl,
    sendSlackAlerts, validateJson } from "../utils/openweather_library";
import { getWeatherData, parseData, writeData } from "../src/main"
import { strict } from 'assert';
import { timerGame } from "./lib/timerGame"

jest.useFakeTimers();



// Bad endpoint/API call - validating that it's caught and error message sent
// Will show an error in console, but shows as passed in the final stats 
describe("API Call - Exception Handling Test", () => {
    it("API Call Should Fail and return error message", async () => {
        
        // Create URL
        const webUrl = createOpenWeatherUrl("?cheese")

        // define message 
        const message = {"message": "Request failed with status code 401",
        "status": {}}

        // attempt API call
        const result = await getWeatherData(webUrl)

        // validate response
        expect(result).toMatchObject(message);

    });

  });


/*
// Validate sending bad data for validation 
describe("Validate data format", () => {
    it("Data format validation should fail", () => {
        
        // define bad data payload
        const badData = {
            "c": 378.85,
            "d": 2.7, 
            "dp": -1.006, 
            "h": 384.3, 
            "l": 377.44, 
            "o": 383.76, 
            "pc": 382.7, 
            "t": 170129160
        }

        // check the data
        const response = validateJson(badData)

        // validate response
        expect(response).toEqual(200)

    })

});
*/


/* 
// Validate sending Slack Alert
// This is just to generate a message, i.e., this test always passes
// unless the wrong webhook is used, it's purpose to is to validate
// that the method to send Slack messages works.
describe("Test Slack Alerts", () => {
    it("Slack Alert Sent Successfully", async () => {

    // expect.assertions(1)
    
    const message = "Test Slack Alert"

    const response = await sendSlackAlerts(message)
    expect(response).toEqual(200)

    })

});
*/