// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node.js - TypeScript version of the Finnhub ETL: pulling down daily stock price data 
// and writing it to InfluxDB.

import { getFinnhubData} from './main';
import { config, FinnhubSchema, finnhubPointData, finnhubData } from '../utils/finnhub_config'
import { sendSlackAlerts,  validateJson} from "../../common/etlUtilities";

// run ETL function in main.ts/main.js
getFinnhubData();
