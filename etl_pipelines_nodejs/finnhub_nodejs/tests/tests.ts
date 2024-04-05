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
        expect(validateJson(bad_data, FinnhubSchema)).toEqual(1)

    })

});


// Validate sending Slack Alert
// This verifies that the proper env var is loaded for the Slack webbhook
// beyond that, you will need to check your Slack channel to verify that
// the message has gone through. 
describe("Test Slack Alerts", () => {
    it("Slack Alert Sent Successfully", () => {

        const message = "Test Slack Alert"

        sendSlackAlerts(message, config.webHookUrl)
            .then(result => {
                expect(result).toEqual(200)

            })

    })

});


// Validate data write error handling, this data payload should fail
// InfluxDB's error checking and trigger an error
describe("Test DB Write", () => {
    it("InfluxDB fails, generates error", async () => {

        const badPayload = {
            "change": 451,
            "lastPrice": "was high",
            "open": "number",
            "previousClose": "cheese"
        }

        const response = await writeData(badPayload)


    })

});