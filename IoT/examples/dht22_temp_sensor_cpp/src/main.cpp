/*
* Pulls data from a dht22 temperature sensor
create a JSON payload and then outputs it to console.
Target device is an ESP32 - used PlatformIO to 
deploy the code.
*/
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <ArduinoJson.h>

#define DHT_SENSOR_PIN 21 
#define DHT_SENSOR_TYPE DHT22
#define LED 2


DHT dht_sensor(DHT_SENSOR_PIN, DHT_SENSOR_TYPE);

void setup() {  

    // DHT22 Sensor Setup 
    Serial.begin(9600);
    dht_sensor.begin(); 

    // MQTT setup

}


void loop() {

  digitalWrite(LED,HIGH); // blink on when reading data to show activity, blink off when finished
   // read humidity
  float humi  = dht_sensor.readHumidity();
  // read temperature in Celsius
  float tempC = dht_sensor.readTemperature();

  // check whether the reading is successful or not
  if ( isnan(tempC) || isnan(humi)) {
    Serial.println("Failed to read from DHT sensor!");
    
    // TODO: add logic for sending alerts for device read failures
    // plan is to send them via MQTT to a service on the k8s cluster
    // that would then send out the Slack messages.

  } else {

    // build JSON message for MQTT 

    JsonDocument payload; // define json document 

    //Add data to the JSON document 
    payload["temperature"] = tempC;
    payload["humidity"] = humi;

    serializeJsonPretty(payload, Serial);
    Serial.println();
    digitalWrite(LED,LOW);

  }

  // sleep interval of 30 seconds
  delay(30000);
 
}