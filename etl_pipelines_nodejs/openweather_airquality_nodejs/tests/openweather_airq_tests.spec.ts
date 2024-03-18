// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Test cases for OpenWeather ETL Air Pollution Data
// TODO: clean-up tear down, refactor main scripts to avoid daisy channing async
// calls, E.g., API fails, then sends message to Slack API, simplify that flow.

import {sendSlackAlerts, validateJson} from "../../common/etlUtilities"
import { getAirQualityData, parseData, writeData } from "../src/main"
import { createAirqUrl } from "../utils/openweather_air_library";
import { config, AirQualitySchema} from "../utils/openweather_air_config"


// Test end to end pipeline, nothing is generated if the pipeline completes
// successfuly, but a messaged is returned if the pipeline fails.
// There will be a couple of logging errors, as the tests will 
// complete before logging finishes. 
describe("Full pipeline test", () => {
    // if the API call fails, a text error message is returned
    it("Pipeline should run, not return a  value", async () => {
        
        //baseline endpoint
        const endpoint = "air_pollution?"
            
        // Create URL
        const webUrl = createAirqUrl(endpoint)

        // Get weather data
        const data = await getAirQualityData(webUrl)
       
       
        const data = data['list'][0]['components']
        

        // validate data payload 
        expect(validateJson(result, AirQualitySchema)).toEqual(0) 

        // parse data - finish extraction
        const payload = parseData(result)

        // validate writing data
        expect(writeData(payload)).toEqual(0) 


    })

});

// Bad endpoint/API call - validating that it's caught and error message sent
// This will throw a test fail warning even though the messages match, however,
// the the final report will show the test as passed.
describe("API Call - Exception Handling Test", () => {
    it("API Call Should Fail and return error message", async () => {
        
    // Create URL
    const webUrl = createAirqUrl("?cheese")

    // define message 
    const message = {"message": "Request failed with status code 401",
    "status": {}}

    // attempt API call 
    const result = await getAirQualityData(webUrl)

    // validate response
    expect(result).toMatchObject(message)

    });

});


// Test sending bad or wrong data to the json validation step
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
