// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node.js - TypeScript version of the Finnhub ETL: pulling down daily stock price data 
// and writing it to InfluxDB.

import { getFinanceData } from './main';

// run ETL - code is in main.ts/main.js
getFinanceData();