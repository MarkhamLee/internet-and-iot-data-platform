// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down data for current weather
// conditions and writes it to InfluxDB
// Config file that contains interfaces, json schemas, env variables, etc.


// interface for weather data
export interface CurrentWeather {
    
    coord: {
        lon: number,
        lat: number
    },
    weather: [
        {id: number,
         main: string,
         description: string,
         icon: string
        }],
    base: string,
    main: {
        temp: number,
        description: string,
        feels_like: number,
        temp_min: number,
        temp_max: number,
        pressure: number,
        humidity: number,
        speed: number,
    },
    visibility: number,
    wind: {
        speed: number,
        deg: number,
    },
    clouds: {
        all: number
    },
    dt: number,
    sys: {
        type: number,
        id: number,
        country: string,
        sunrise: number,
        sunset: number,}
        timezone: number,
        id: number,
        name: string,
        cod: number,
}

export interface WeatherResponse {
    data: CurrentWeather[],
    status: number,
}

// error message interface
export interface ErrorMessage {

    message: string
    status: number

}

export interface VarConfig {
    bucket: string;
    city: string;
    measurement: string;
    org: string 
    token: string;
    url: string;
    weatherKey: string;
    webHookUrl: string;
    
  }

export const config: VarConfig = {
    
    bucket: process.env.BUCKET as string,
    city: process.env.CITY as string,
    measurement: process.env.WEATHER_MEASUREMENT as string,
    org: process.env.INFLUX_ORG as string,
    token: process.env.INFLUX_KEY as string,
    url: process.env.INFLUX_URL as string,
    weatherKey: process.env.OPENWEATHER_KEY as string,
    webHookUrl: process.env.ALERT_WEBHOOK as string,
    
  };

export const openWeatherSchema = {
    
    "type": "object",
    
    "properties": {
      "coord": {
        "type": "object",
        "properties": {
            "barometric_pressure": {"type": "number"},
            "description": {"type": "string"},
            "feels_like": {"type": "string"},
            "high": {"type": "number"},
            "humidity": {"type": "number"},
            "low": {"type": "number"},
            "temp": {"type": "number"},
            "time_stamp": {"type": "number"},
            "weather": {"type": "string"},
            "wind": {"type": "string"},
            },
    "required": ["description", "feels_like", "high", "humidity",
    "low", "temp", "time_stamp", "weather", "wind"],
    }
   }
}