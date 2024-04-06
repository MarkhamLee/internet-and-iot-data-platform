// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Tests for Node variant for the OpenWeather API ETL - pulls down data for 
// current weather conditions and writes it to InfluxDB. The API calls aren't 
// mocked, because I wanted be sure that the tests exactly replicate 
// production.
// Note: There may be a couple of warnings of tests completing before logging
// can complete, but it doesn't impact the tests.

import { createOpenWeatherUrl } from "../utils/openweather_library";
import { getWeatherData, parseData, writeData } from "../src/main"
import {sendSlackAlerts, validateJson} from "../../common/etlUtilities"
import { config, openWeatherSchema } from "../utils/openweather_config"


// Test the API call: getting data from OpenWeather and validating
// that it contains the right fields.
describe("Validate OpenWeather API call", () => {
    test("API call should succeed", () => {
        
    //baseline endpoint
    const endpoint = "weather?"
        
    // Create URL
    const webUrl = createOpenWeatherUrl(endpoint)

    // Call OpenWeather API
    getWeatherData(webUrl)
        .then(result => {

            // parse data - finish extraction
            const payload = parseData(result)

            // check the data, if the data was parsed successfully
            // we won't get a 200 code from an Alert being sent via Slack.
            expect((payload)).not.toEqual(200)

        })

    })

});


// Test the data validation step with good data
describe("Validate good data format", () => {
    test("Data format validation should be successfull", () => {
        
        // define good data payload
         const goodData= {
            barometric_pressure: 1007,
            description: 'broken clouds',
            feels_like: 11.24,
            high: 14.12,
            humidity: 90,
            low: 9.67,
            temp: 11.67,
            time_stamp: 1711154086,
            weather: 'Clouds',
            wind: 4.63
          }

        // check the data
        expect(validateJson(goodData, openWeatherSchema)).toEqual(0)
    })

});


// Test the data validation step by sending bad data 
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
        expect(validateJson(badData, openWeatherSchema)).toEqual(1)
    })

}); 

// Test that data writes properly to InfluxDB
// This test passes as it's supposed to, but throws a few warnings over tests finishing before 
// logs can complete.
describe("Validate data write", () => {
    test("The data should write to InfluxDB successfully", () => {
        
        // define good data payload
         const goodData= {
            barometric_pressure: 1007,
            description: 'broken clouds',
            feels_like: 11.24,
            high: 14.12,
            humidity: 90,
            low: 9.67,
            temp: 11.67,
            time_stamp: 1711154086,
            weather: 'Clouds',
            wind: 4.63
          }

        const response = writeData(goodData);
        expect(writeData(goodData)).toEqual(0)
    })

});

// Validate sending Slack Alert
// This verifies that the proper env var is loaded for the Slack webbhook
// beyond that, you will need to check your Slack channel to verify that
// the message has gone through. 
describe("Test Slack Alerts", () => {
    it("Slack Alert Sent Successfully", async () => {
    
    const message = "Test Slack Alert"

    const response = await sendSlackAlerts(message, config.webHookUrl)
    
    })

});