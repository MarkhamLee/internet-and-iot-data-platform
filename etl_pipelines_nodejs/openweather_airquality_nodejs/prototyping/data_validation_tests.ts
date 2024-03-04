// quick dirty example and test of the Ajv library for validating json data
// I didn't bother compiling this one, I just ran it with: 
// 'ts-node data-validation_tests.ts'

import Ajv from "ajv";
import { sendSlackAlerts } from "../utils/openweather_air_library";


const airQualitySchema = {
  
    "type": "object",
    "properties": {
        "cheese": {"type": "string"},
        "no": {"type": "number"},
        "no2": {"type": "number"},
        "o3": {"type": "number"},
        "so2": {"type": "number"},
        "pm2_5": {"type": "number"},
        "pm10": {"type": "number"},
        "nnh3": {"type": "number"},
    },
    "required": ["cheese", "pm2_5", "pm10"],

};

const airQualityData  = {
 
    co: 260.35,
    no: 0.38,
    no2: 4.54,
    o3: 72.96,
    so2: 0.87,
    pm2_5: 0.75,
    pm10: 1.75,
    nh3: 0.27

};

 

const ajv = new Ajv();


const valid= ajv.validate(airQualitySchema, airQualityData);

if (valid) {

    console.log("Data validated successfuly");
  
} else {

  const message = "Data pipeline failure, OpenWeather Air Quality (Nodejs Variant): data validation failure"
  console.error(message, ajv.errors);
  sendSlackAlerts(message)

}