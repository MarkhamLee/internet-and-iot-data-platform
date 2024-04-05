// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Shared config file for Node.js ETLs


export type pointData = {

  point: object
  
};

export const influx = {

    "type": "object",
    "properties": {
        "writePoint": {"type": "object"},
        "flush": {"type": "object"},

    }
    
};