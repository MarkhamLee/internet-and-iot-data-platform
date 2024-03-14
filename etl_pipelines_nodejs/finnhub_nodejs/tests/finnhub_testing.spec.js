"use strict";
// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Testing for the Finnhub ETL 
Object.defineProperty(exports, "__esModule", { value: true });
var utilities_1 = require("../utils/utilities");
var main_1 = require("../src/main");
// Test end to end
// There will be a couple of logging errors, as the tests will complete before logging finishes. 
describe("Full pipeline test", function () {
    it("Pipeline should run and return 0", function () {
        expect((0, main_1.getFinanceData)()).toEqual(0);
    });
});
// Validate sending bad data for validation 
describe("Validate data format", function () {
    it("Data format validation should fail", function () {
        var bad_data = {
            "cheese": "cake",
            "wheat": "chex",
            "turquoise": 5011,
            "jeeps": 5309,
        };
        //validate data
        expect((0, utilities_1.validateJson)(bad_data)).toEqual(1);
    });
});
// Validate sending Slack Alert
// This is just to generate a message, i.e., this test always passes
// the tester will need to check their Slack messages to verify the message
// went through.
describe("Test Slack Alerts", function () {
    it("Slack Alert Sent Successfully", function () {
        var message = "Test Slack Alert";
        (0, utilities_1.sendSlackAlerts)(message)
            .then(function (result) {
            expect(result).toEqual(200);
        });
    });
});
