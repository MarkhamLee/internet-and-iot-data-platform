/*
* Pulls data froma dht22 temperature sensor and then
* Sends it to an MQTT broker
*/

#include <iostream>
#include <stdlib.h>
#include <Arduino.h>
#include <ArduinoJson.h>
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

#define DHT_SENSOR_PIN_21 21
#define DHT_SENSOR_TYPE DHT22

DHT dht_sensor(DHT_SENSOR_PIN_21, DHT_SENSOR_TYPE);

#define LED 2

void setup() {
  
  // put your setup code here, to run once:
  Serial.begin(115200);
    
  // setup pin to flash on activity
  pinMode(LED, OUTPUT);

  Serial.println("Activating DHT22 sensor");
  
  // set up for DHT22 sensor 
  dht_sensor.begin();  // initialize sensor


}


void loop() {

  // read humidity
  digitalWrite(LED,HIGH); // blink on when reading and transmitting, off when finished
  float humi  = dht_sensor.readHumidity();
  // read temperature in Celsius
  float tempC = dht_sensor.readTemperature();
  digitalWrite(LED,LOW); // if the blue light is solid/doesn't blink, something is wrong.

  // check whether the reading is successful or not
  if ( isnan(tempC) || isnan(humi)) {
    Serial.println("Failed to read from DHT sensor!");
    
    // TODO: add logic for sending alerts for device read failures
    // initial approach will be to send a MQTT message to count how often this occurs
    // before we spam ourselves with alert messages.

  } else {

    

    // build JSON message for MQTT 

    JsonDocument payload; // define json document 

    //Add data to the JSON document 
    payload["temperature"] = tempC;
    payload["humidity"] = humi;

    measureJson(payload);

    // output payload in json format
    serializeJsonPretty(payload, Serial);
    Serial.println();
    
 
  }

  delay(5000); // delay in ms

}