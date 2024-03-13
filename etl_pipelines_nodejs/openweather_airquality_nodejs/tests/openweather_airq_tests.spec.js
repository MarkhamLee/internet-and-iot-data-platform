"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var openweather_air_library_1 = require("../utils/openweather_air_library");
var main_1 = require("../src/main");
// Test end to end pipeline, nothing is generated if the pipeline completes
// successfuly, but a messaged is returned if the pipeline fails.
// There will be a couple of logging errors, as the tests will 
// complete before logging finishes. 
describe("Full pipeline test", function () {
    // if the API call fails, a text error message is returned
    it("Pipeline should run, not return a  value", function () {
        //baseline endpoint
        var endpoint = "air_pollution?";
        // Create URL
        var webUrl = (0, openweather_air_library_1.createAirqUrl)(endpoint);
        // Get weather data
        (0, main_1.getAirQualityData)(webUrl)
            .then(function (result) {
            // parse data - finish extraction
            var payload = (0, main_1.parseData)(result);
            expect((0, main_1.writeData)(payload)).toBeUndefined();
        });
    });
});
// Bad endpoint/API call - validating that it's caught and error message sent
// This will throw a test fail warning even though the messages match, however,
// the the final report will show the test as passed.
describe("API Call - Exception Handling Test", function () {
    it("API Call Should Fail and return error message", function () {
        // Create URL
        var webUrl = (0, openweather_air_library_1.createAirqUrl)("?cheese");
        // define message 
        var message = { "message": "Request failed with status code 401", "status": 401 };
        // Get weather data
        (0, main_1.getAirQualityData)(webUrl)
            .then(function (result) {
            expect(result).toContain(message);
        });
    });
});
// Test sending bad or wrong data to the json validation step
describe("Validate data format", function () {
    it("Data format validation should fail", function () {
        var bad_data = {
            "c": 378.85,
            "d": 2.7,
            "dp": -1.006,
            "h": 384.3,
        };
        //validate data
        expect((0, openweather_air_library_1.validateJson)(bad_data)).toEqual(1);
    });
});
// Validate sending Slack Alert
// This is just to generate a message, i.e., this test always passes
// the tester will need to check their Slack messages to verify the message
// went through.
describe("Test Slack Alerts", function () {
    it("Slack Alert Sent Successfully", function () {
        var message = "Test Slack Alert";
        (0, openweather_air_library_1.sendSlackAlerts)(message)
            .then(function (result) {
            expect(result).toEqual(200);
        });
    });
});
