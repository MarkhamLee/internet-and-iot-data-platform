// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Testing for the Finnhub ETL 
import { getFinnhubData, parseData, writeData} from '../src/main';
import { createFinnhubUrl } from "../utils/utilities"
import {sendSlackAlerts, validateJson} from "../../common/etlUtilities"
import { config, FinnhubSchema } from "../utils/finnhub_config"

// test API call + extracting/parsing data
describe("Validate Finnhub API Call", () => {
    it("Successful API call, data parsed successfully", () => {
        
    // create Finnhub URL
    const finnhubUrl = createFinnhubUrl(config.stock);

    // Get Finnhub data
    getFinnhubData(finnhubUrl)
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
          c: 518.43,
          d: 5.36,
          dp: 1.0447,
          h: 520.44,
          l: 514.01,
          o: 514.46,
          pc: 513.07,
          t: 1712347200
        }

      // check the data
      expect(validateJson(goodData, FinnhubSchema)).toEqual(0)
  })

});


// Test the data validation step by sending bad data 
describe("Validate data format", () => {
  it("Data format validation should fail", () => {
      
      // define bad data payload
      const badData = {
          "c": "Vector W8",
          h: "wrong",
          l: 514.01,
          "d": 2.7, 
          "dp": -1.006, 
          "t": "Cheese"
      }

      // check the data
      expect(validateJson(badData, FinnhubSchema)).toEqual(1)
  })

}); 

// Test that data writes properly to InfluxDB
// This test passes as it's supposed to, but throws a few warnings over tests finishing before 
// logs can complete.
describe("Validate data write", () => {
  test("The data should write to InfluxDB successfully", async () => {
      
      // define good data payload
       const goodData= {
        previousClose: 513.07,
        open: 514.46,
        lastPrice: 514.01,
        change: 1.0447
        }

      const response = await writeData(goodData);
      expect(response).toEqual(0)
  })

});

// Test exception handling for a failed InfluxDB write
// the expection is that a Slack error message is sent and
// a 200 code is returned.
describe("Validate InfluXDB type protection", () => {
  test("The InfluxDB write should fail due to open field being an integer", async () => {
      
      // define bad data payload
       const badData= {
        previousClose: 513.07,
        open: "cheese",
        lastPrice: 514.01,
        change: 1.0447
        }

      const response =  await writeData(badData)
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