// (C) Markham Lee 2023 - 2024
// productivity-music-stocks-weather-IoT-dashboard
// https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
// Node variant for the OpenWeather API ETL - pulls down current weather data
// and writes it to InfluxDB
// Work in progress, testing basic functionality
// TODO: Slack alerts for failures, more robust exception handling, split out InfluxDB
// client to separate file that can be shared with other node.js based ETLs that 
// write to InfluxDB.


const {InfluxDB, Point} = require("@influxdata/influxdb-client");
const axios = require("axios");

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
    console.log('Status Code:', res.status);

    const data = res.data.main;
    const wind = res.data.wind.speed 

    console.log('Weather data retrieved')

    const { temp } = data
    const { humidity } = data
    const { pressure } = data

    write_data(writeClient, temp, wind, pressure, humidity)

    })
    .catch(err => {
        console.log('Error: ', err.message);
        });


function create_influx_client(bucket) {

    const token = process.env.INFLUX_KEY
    const url = process.env.INFLUX_URL
    const org = process.env.INFLUX_ORG

    const client = new InfluxDB({url, token})
    console.log('InfluxDB client created')

    return client.getWriteApi(org, bucket, 'ns')

}


// create write client - largely boiler plate code from Influx Data
// TODO: catch errors 
// TODO: look into writing JSON directly 
function write_data(writeClient, temp, wind, pressure, humidity) {

    MEASUREMENT = process.env['WEATHER_MEASUREMENT']

    let point = new Point(MEASUREMENT)
            .tag('Weather ETL')
            .floatField('temp', temp) //form of field name, value
            .floatField('wind_speed', wind)
            .floatField('pressure', pressure)
            .floatField('humidity', humidity)
    
    // write
    void setTimeout(() => {
            
            // write data
            writeClient.writePoint(point)
            console.log("Weather data successfully written to InfluxDB")
        }, 1000)
    
    // flush 
    void setTimeout(() => {

            // flush InfluxDB client
            writeClient.flush()
        }, 1000)
    
    }