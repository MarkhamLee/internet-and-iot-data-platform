// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node POC for the OpenWeather API- pulls down current weather data
// and writes it to InfluxDB. Experimenting with node.js ETL containers running on
// on Airflow. TODO: convert to TypeScript, split out InfluxDB client to separate file
// that can be shared with other node.js based ETLs that write to InfluxDB.


const {InfluxDB, Point} = require("@influxdata/influxdb-client");
const axios = require("axios");


// load Bucket (database in InfluxDB parlance) & create InfluxDB client
const BUCKET = process.env.BUCKET;
writeClient = create_influx_client(BUCKET)

// load weather related variables 
WEATHER_KEY = process.env.OPENWEATHER_KEY
const CITY = "&q=seattle"
const ENDPOINT = "weather?"

// build openweather API URL 
const BASE_URL = "http://api.openweathermap.org/data/2.5/"
const UNITS = "&units=metric"
const WEATHER_URL = BASE_URL.concat(ENDPOINT,'appid=',WEATHER_KEY,CITY,UNITS)
console.log('Base url created')

// retrieve weather data 
axios.get(WEATHER_URL)
  .then(res => {
    const headerDate = res.headers && res.headers.date ? res.headers.date : 'no response date';
    console.log('Weather data retrieved with status code:', res.status)

    // split out parts of the json 
    const data = res.data.main;
    
    // parse out individual fields 
    payload = {
        "barometric_pressure": data.pressure,
        "description": res.data.weather[0].description,
        "feels_like": data.feels_like,
        "high": data.temp_max,
        "humidity": data.humidity,
        "low": data.temp_min,
        "temp": data.temp,
        "time_stamp": res.data.dt,
        "weather": res.data.weather[0].main,
        "wind": res.data.wind.speed
    }

    console.log("InfluxDB payload ready:", payload)
   
    write_data(writeClient, payload)

    })
    .catch(err => {
        message = "Pipeline failure alert: OpenWeather API current weather node.js variant with error:"
        console.log(message.concat(err.message));

        //send Slack failure alert
        send_slack_alerts(message.concat(err.message))
        });

// creates client for connecting to InfluxDB via the official InfluxDB
// Node/Library 
function create_influx_client(bucket) {

    const token = process.env.INFLUX_KEY
    const url = process.env.INFLUX_URL
    const org = process.env.INFLUX_ORG

    const client = new InfluxDB({url, token})
    console.log('InfluxDB client created')

    return client.getWriteApi(org, bucket, 'ns')

}


// largely boiler plate code from Influx Data
// TODO: figure out how to write JSON directly
// TODO: move to utilities file
// TODO: improve exception handling, the Influx library handles auth errors
// in a way that they don't really register as errors/aren't picked up
// by try/catch 
function write_data(writeClient, payload) {

    MEASUREMENT = process.env['WEATHER_MEASUREMENT']
    console.log(MEASUREMENT)

    let point = new Point(MEASUREMENT)
            .tag("OpenWeatherAPI", "current_weather",)
            .floatField('temp', payload.temp)
            .floatField('wind', payload.wind)
            .floatField('barometric_pressure', payload.barometric_pressure)
            .floatField('humidity', payload.humidity)
            .floatField('low', payload.low)
            .floatField('high', payload.high)
            .floatField('feels_like', payload.feels_like)
            .intField('time_stamp', payload.time_stamp)
            .stringField('description', payload.description)
            .stringField('weather', payload.weather)
            
    // write data to InfluxDB
    void setTimeout(() => {

        writeClient.writePoint(point);
        console.log("Weather data successfully written to InfluxDB")

        }, 1000)


    // flush client
    void setTimeout(() => {

            // flush InfluxDB client
            writeClient.flush()
        }, 1000)
        
    }

// method to send Slack alerts 
// TODO: move to utilities file for all Node.js ETLs
function send_slack_alerts(message) {

    // load Slack webhook
    WEBHOOK_URL = process.env.ALERT_WEBHOOK

    headers = {'Content-type': 'application/json'}

    payload = JSON.stringify({
        "text": message
    })

    axios.post(WEBHOOK_URL, json=payload)
      .then(function (response) {
        console.log("Slack message sent successfully with code:", response.status);
      })

      .catch(function (error) {
        console.log("Slack message failure with error: ", error.response.statusText);
      });

    }
