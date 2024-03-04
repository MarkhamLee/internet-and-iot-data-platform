// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down air pollution data from
// the OpenWeather API writes it to InfluxDB
// Config file that contains interfaces, json schemas, env variables, etc.

// interface for air quality data
// this help us avoid type errors during development.
export interface AirQualityMetrics {
    
    coord: {
        lon: number,
        lat: number
    },
    list: [
        main: {aqi: number},
        components: {
            no: number,
            no2: number,
            temp: number,
            o3: number,
            so2: number,
            pm2_5: number,
            pm10: number,
            nh3: number,
            }],
    dt: number}

// for using the Air Quality Metrics interface
export interface AirResponse {
    data: AirQualityMetrics[],
    status: number
}

// error message interface
export interface ErrorMessage {

    message: string
    status: number

}

// this interface allows us to define all the environmental variables
export interface VarConfig {
    bucket: string;
    city: string;
    lat: string;
    long: string;
    measurement: string;
    org: string 
    token: string;
    url: string;
    weatherKey: string;
    webHookUrl: string;
    
  }

// this combined with the above allow us to retriev all the environmental
// variables and make them available to any script that imports this file. 
export const config: VarConfig = {
    
    bucket: process.env.BUCKET as string,
    city: process.env.CITY as string,
    lat: process.env.LAT as string,
    long: process.env.LONG as string,
    measurement: process.env.AIR_QUALITY_MEASUREMENT as string,
    org: process.env.INFLUX_ORG as string,
    token: process.env.INFLUX_KEY as string,
    url: process.env.INFLUX_URL as string,
    weatherKey: process.env.OPENWEATHER_KEY as string,
    webHookUrl: process.env.ALERT_WEBHOOK as string,
    
  };

  // this is the schema that we use to validate that the data
  // received from the API is correct.
  export const airQualitySchema = {
  
    "type": "object",
    "properties": {
        "co": {"type": "number"},
        "no": {"type": "number"},
        "no2": {"type": "number"},
        "o3": {"type": "number"},
        "so2": {"type": "number"},
        "pm2_5": {"type": "number"},
        "pm10": {"type": "number"},
        "nnh3": {"type": "number"},
    },
    "required": ["co", "pm2_5", "pm10"],
};