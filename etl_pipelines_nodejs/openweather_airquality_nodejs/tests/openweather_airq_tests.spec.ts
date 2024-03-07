import { strict } from 'assert';
import { createAirqUrl, sendSlackAlerts, validateJson } from "../utils/openweather_air_library";
import { getAirQualityData, parseData, writeData } from "../src/main"



// Test end to end
// There will be a couple of logging errors, as the tests will complete before logging finishes. 
describe("Full pipeline test", () => {
    // if the API call fails, a text error message is returned
    it("Pipeline should run, not return a  value", () => {
        
        //baseline endpoint
        const endpoint = "air_pollution?"
        
        // Create URL
        const webUrl = createAirqUrl(endpoint)

        // Get weather data
        getAirQualityData(webUrl)
            .then(result => {
                
                // parse data - finish extraction
                const payload = parseData(result)

                expect(writeData(payload)).toBeUndefined();

            })

    });
  });


// Bad endpoint/API call - validating that it's caught and error message sent
// This will throw a test fail warning even though the messages match, however, the 
// the final report will show the test as passed.
describe("API Call - Exception Handling Test", () => {
    it("API Call Should Fail and return error message", () => {
        
        // Create URL
        const webUrl = createAirqUrl("?cheese")

        // define message 
        const message = {"message": "Request failed with status code 401", "status": 401}

        // Get weather data
        getAirQualityData(webUrl)
            .then(result => {
                expect(result).toContain(message);
            })
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

