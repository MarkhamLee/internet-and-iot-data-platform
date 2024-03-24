     // (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Config file for Finnhub ETL


// interface for Finnhub data
export interface VarConfig {
  bucket: string;
  finnhubKey: string;
  measurement: string;
  org: string; 
  stock: string;
  token: string;
  url: string;
  webHookUrl: string;
    
};

// For using the Finnhub interface
export const config: VarConfig = {
    
  bucket: process.env.BUCKET as string,
  finnhubKey: process.env.FINNHUB_SECRET as string,
  measurement: process.env.FINNHUB_MEASUREMENT_SPY as string,
  org: process.env.INFLUX_ORG as string,
  stock: process.env.STOCK_SYMBOL as string,
  token: process.env.INFLUX_KEY as string,
  url: process.env.INFLUX_URL as string,
  webHookUrl: process.env.ALERT_WEBHOOK as string,
    
};

// schema for validating the API response from Finnhub
export const FinnhubSchema = {
  
  "type": "object",
  "properties": {
    "c": {"type": "number"},
    "d": {"type": "number"},
    "dp": {"type": "number"},
    "h": {"type": "number"},
    "l": {"type": "number"},
    "o": {"type": "number"},
    "pc": {"type": "number"},
      "t": {"type": "number"},
    },
    "required": ["pc", "o", "l", "dp"],
};

export type finnhubData = {

  c: number;
  d: number;
  dp: number;
  h: number;
  l: number;
  o: number;
  pc: number;
  t: number;

};


export type finnhubPointData = {

  change: number;
  lastPrice: number;
  open: number;
  previousClose: number;

}

export type finnhubApiError = {

  code: number;
  message: string;

}