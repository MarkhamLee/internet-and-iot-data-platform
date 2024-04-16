// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Test cases for OpenWeather ETL Air Pollution Data
import {sendSlackAlerts, validateJson} from "../../common/etlUtilities"
import { getAirQualityData, parseData, writeData } from "../src/main"
import { createAirqUrl } from "../utils/openweather_air_library";
import { config, AirQualitySchema} from "../utils/openweather_air_config"


// Test API call, getting data from OpenWeather and validating that
// it is in the correct format. 
describe("Full OpenWeather Air Pollution API Call", () => {
    // if the API call fails, a text error message is returned
    it("API call should succeed", () => {
        
        //baseline endpoint
        const endpoint = "air_pollution?"
            
        // Create URL
        const webUrl = createAirqUrl(endpoint)

        // Get weather data
        getAirQualityData(webUrl)
            .then(result => {

                // parse data - finish extraction
                const payload = parseData(result)

                // check the data, if the data was parsed successfully
                // we won't get a 200 code from an Alert being sent via Slack.
                expect((payload)).not.toEqual(200)

            })
    })

});


// Test the data validation step by sending bad data
describe("Validate data format", () => {
    it("Data format validation should fail", () => {

    const bad_data = {
        "c": 378.85,
        "d": 2.7, 
        "dp": -1.006, 
        "h": 384.3, 
    }

    //validate data
    expect(validateJson(bad_data, AirQualitySchema)).toEqual(1)

    })

});

// Test the data validation step with good data
describe("Validate good data format", () => {
    test("Data format validation should be successfull", () => {
        
        // define good data payload
        const goodData = { co: 320.44, pm2_5: 2.64, pm10: 4.15 }

        // check the data
        expect(validateJson(goodData, AirQualitySchema)).toEqual(0)
    })

});


// Test that data writes properly to InfluxDB
describe("Validate data write", () => {
    test("The data should write to InfluxDB successfully", async () => {
        
        // define good data payload
        const goodData = { co: 320.44, pm2_5: 2.64, pm10: 4.15 }

        const response = await writeData(goodData)
        expect(response).toEqual(0)
    })

});


// Test that InfluxDB's type checking rejects bad data E.g., strings in a float field
// and exception handling generates a Slack alert
// change the type in the writeData method to "any" so you can test
// this case and then change it back before pushing to prod.
describe("Test InfluxDB type checking", () => {
    test("The InfluxDB data write should fail", async () => {
        
        // define good data payload
        const badData = { co: "string", pm2_5: 2.64, pm10: 4.15 }

        const response = await writeData(badData) //change type to any to tes t this case
        expect(response).toEqual(200)
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
    expect(response).toEqual(200)

    })

});