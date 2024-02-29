// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node POC for the OpenWeather API- pulls down current weather data
// and writes it to InfluxDB. Experimenting with node.js ETL containers running on
// on Airflow. This is basic POC version, the more polished one will be the 
// TypeScript version in this folder's parent directory with the _ts added to
// the folder name.


const {InfluxDB, Point} = require("@influxdata/influxdb-client");
const axios = require("axios");

// load Bucket (database in InfluxDB parlance) & create InfluxDB client
const bucket = process.env.BUCKET;
writeClient = createInfluxClient(bucket)

// load weather related variables 
weatherKey = process.env.OPENWEATHER_KEY
city = process.env.CITY
const endpoint = "weather?"

// build openweather API URL 
const baseUrl = "http://api.openweathermap.org/data/2.5/"
const units = "&units=metric"
const weatherUrl = baseUrl.concat(endpoint,'appid=',weatherKey,'&q=',city,units)
console.log('Base url created')

// retrieve weather data 
axios.get(weatherUrl)
  .then(res => {
    console.log('Weather data retrieved with status code:', res.status)

    // split out parts of the json 
    const data = res.data.main;
    
    // parse out individual fields 
    payload = {"barometric_pressure": data.pressure,
        "description": res.data.weather[0].description,
        "feels_like": data.feels_like,
        "high": data.temp_max,
        "humidity": data.humidity,
        "low": data.temp_min,
        "temp": data.temp,
        "time_stamp": res.data.dt,
        "weather": res.data.weather[0].main,
        "wind": res.data.wind.speed }

    console.log("InfluxDB payload ready:", payload)
   
    writeData(writeClient, payload)

    })
    .catch(err => {
        message = "Pipeline failure alert: OpenWeather API current weather node.js variant with error: "
        console.log(message.concat(err.message));

        //send Slack failure alert
        sendSlackAlerts(message.concat(err.message))
        });

// creates client for connecting to InfluxDB via the official InfluxDB
// Node/Library 
function createInfluxClient(bucket) {

    const token = process.env.INFLUX_KEY
    const url = process.env.INFLUX_URL
    const org = process.env.INFLUX_ORG

    const client = new InfluxDB({url, token})
    console.log('InfluxDB client created')

    return client.getWriteApi(org, bucket, 'ns')

}

// largely boiler plate code from Influx Data
function writeData(writeClient, payload) {

    measurement = process.env['WEATHER_MEASUREMENT']

    let point = new Point(measurement)
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
function sendSlackAlerts(message) {

    // load Slack webhook
    webHookUrl = process.env.ALERT_WEBHOOK

    payload = JSON.stringify({
        "text": message
    })

    axios.post(webHookUrl, payload)
      .then(function (response) {
        console.log("Slack message sent successfully with code:", response.status);
      })

      .catch(function (error) {
        console.log("Slack message failure with error:",error.code);
      });

    }
