"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down data for current weather
// conditions and writes it to InfluxDB
// TODO: clean up the tests a bit so the console message are written before the tests complete
Object.defineProperty(exports, "__esModule", { value: true });
var openweather_library_1 = require("../utils/openweather_library");
var main_1 = require("../src/main");
// Test end to end
// There will be a couple of logging errors, as the tests will complete before logging finishes. 
// If the test fails an error message (string) is returned.
describe("Full pipeline test", function () {
    it("Pipeline should run, not return a  value", function () {
        //baseline endpoint
        var endpoint = "weather?";
        // Create URL
        var webUrl = (0, openweather_library_1.createOpenWeatherUrl)(endpoint);
        // Get weather data
        (0, main_1.getWeatherData)(webUrl)
            .then(function (result) {
            // parse data - finish extraction
            var payload = (0, main_1.parseData)(result);
            test("Validate Payload was parsed properly", function () {
                // get response code from API call
                expect((0, openweather_library_1.validateJson)(payload)).rejects.toEqual(0);
            });
            test("Validate that the data was written successfully", function () {
                // write data
                expect((0, main_1.writeData)(payload)).toEqual(0);
            });
        });
    });
});
// Bad endpoint/API call - validating that it's caught and error message sent
// Will show an error in console, but shows as passed in the final stats 
describe("API Call - Exception Handling Test", function () {
    it("API Call Should Fail and return error message", function () {
        // Create URL
        var webUrl = (0, openweather_library_1.createOpenWeatherUrl)("?cheese");
        // define message 
        var message = "Request failed with status code 401";
        // Get weather data
        (0, main_1.getWeatherData)(webUrl)
            .then(function (result) {
            expect(result).toContain(message);
        });
    });
});
// Validate sending bad data for validation 
describe("Validate data format", function () {
    it("Data format validation should fail", function () {
        var bad_data = {
            "c": 378.85,
            "d": 2.7,
            "dp": -1.006,
            "h": 384.3,
            "l": 377.44,
            "o": 383.76,
            "pc": 382.7,
            "t": 170129160
        };
        //validate data
        expect((0, openweather_library_1.validateJson)(bad_data)).toEqual(1);
    });
});
// Validate sending Slack Alert
// This is just to generate a message, i.e., this test always passes
// the tester will need to check their Slack messages to verify the message
// went through.
describe("Test Slack Alerts", function () {
    it("Slack Alert Sent Successfully", function () {
        var message = "Test Slack Alert";
        (0, openweather_library_1.sendSlackAlerts)(message)
            .then(function (result) {
            expect(result).toEqual(200);
        });
    });
});
