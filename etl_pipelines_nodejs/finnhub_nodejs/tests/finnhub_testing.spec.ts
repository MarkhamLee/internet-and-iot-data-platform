// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Testing for the Finnhub ETL 
// TODO: clean-up tear down, refactor main scripts to avoid daisy channing async
// calls, E.g., API fails, then sends message to Slack API, simplify that flow.

import { getFinanceData } from "../src/main"
import {sendSlackAlerts, validateJson} from "../../common/etlUtilities"
import { config, FinnhubSchema } from "../utils/finnhub_config"

// Test end to end
// There will be a couple of logging errors, as the tests will complete before logging finishes. 
describe("Full pipeline test", () => {
    it("Pipeline should run and return 0", () => {
        
        expect(getFinanceData()).toEqual(0)


  });
})







