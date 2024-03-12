// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Testing for tracking GitHub actions at the repo level

import { sendSlackAlerts, buildUrl } from "../utils/utilities";
import { getGitHubActions, parseData, writeData } from "../src/main";
import { config } from '../utils/gh_actions_config'


// End to End Test
describe("GitHub API Full pipeline test", () => {
    it("Pipeline should run and return a payload + a 200 code", () => {

        // base URL 
        const repo = 'finance-productivity-iot-informational-weather-dashboard/'

        // get full URL
        const fullUrl = buildUrl(repo)
        console.log(fullUrl)

        getGitHubActions(fullUrl)
        .then(result => {
    
            // get the parsed data/
            const payload = parseData(result)
           
            // get response code from API call
            expect(payload['status']).toEqual(200)
            
            // write data
            expect(writeData(payload)).toEqual(0)

    })                

  });
})