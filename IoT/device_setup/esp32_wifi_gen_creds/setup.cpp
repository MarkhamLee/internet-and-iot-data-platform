/*

This is a provisioning sketch for ESP32 devices, the MQTT
creds are loaded from environmental variables and I enter in the
Wi-Fi credentials on my iPad (or any device with Wi-Fi) and then
stored on the device. Once that's done you can comment out or delete
the lines of code used for loading that data and write your app code
without having to worry about loading Wi-Fi credentials, MQTT creds, etc.

*/
#include <iostream>
#include <stdlib.h>
#include <Arduino.h>
#include <WiFiManager.h> 
#include <PicoMQTT.h>
#include <ArduinoJson.h>
#include <Preferences.h>

#define LED 2


PicoMQTT::Client mqtt("");

String topic = "/embedded/esp32_S5003_airquality";


void setup() {  

    // start setup for Wi-Fi manager & collecting MQTT parametrs 
    WiFi.mode(WIFI_STA); 
 
  
    Serial.begin(115200);
    
    WiFiManager wm;

    // Supress Debug information
    wm.setDebugOutput(false);
 
    // reset settings - comment out after you've loaded creds
    // Wi-Fi credentials
    // wm.resetSettings();

    // parameters for Wi-Fi setup 
    // comment out after you've loaded creds
    // bool res;
    // res = wm.autoConnect("esp32_node1_s5003","password");

    // setup preferences to save the data 
    Preferences prefs;

    prefs.begin("credentials", false);

    // I have the MQTT creds on my dev box as env vars - this allows me to 
    // quickly and easy load them on the ESP32. Comment out after you've
    // loaded the creds.
    //String mqtt_user =  getenv ("MQTT_USER");
    //String mqtt_secret = getenv ("MQTT_SECRET");
    //String mqtt_host = getenv ("MQTT_HOST");

    //prefs.putString("mqtt_user", mqtt_user);
    //prefs.putString("mqtt_secret", mqtt_secret);
    //prefs.putString("mqtt_host", mqtt_host);

    //Serial.println("MQTT credentials saved");

    prefs.end();
      
    // Auto Connect esp32_node will be part of the device name on your WiFi network
    if (!wm.autoConnect("esp32_node1_s5003", "password")) {
        // Did not connect, print error message
        Serial.println("failed to connect and hit timeout");
    
        // try again
        ESP.restart();
        delay(1000);

    } else {

      // Connection Message
      Serial.println("WiFi connected");
      Serial.print("IP address: ");
      Serial.println(WiFi.localIP());

    }

    // end Wi-Fi Manager setup 

    // Plantower S5003 Setup


    // load MQTT creds and setup the MQTT client
    Preferences preferences;

    preferences.begin("credentials", false);

    // get MQTT creds
    String host = preferences.getString("mqtt_host", "");
    String user = preferences.getString("mqtt_user", "");
    String secret = preferences.getString("mqtt_secret", "");

    // MQTT setup
    mqtt.host=host;
    mqtt.port=1883;
    mqtt.username=user;
    mqtt.password=secret;
    mqtt.client_id = "esp32_node1_s5003";
    mqtt.begin();

    // setup pin to flash on activity
    pinMode(LED, OUTPUT);


}


void loop() {

  mqtt.loop();

  digitalWrite(LED,HIGH); // blink on when reading and transmitting, off when finished

  // insert code for reading from sensor


  // build JSON message for MQTT 

  JsonDocument payload; // define json document 

  //Add data to the JSON document 
  payload["pm1"] = 1;
  payload["pm25"] = 2;
  payload["pm10"] = 3;

  // send MQTT message
  auto publish = mqtt.begin_publish(topic, measureJson(payload));
  serializeJson(payload, publish);
  publish.send();
  digitalWrite(LED,LOW);

  // output payload in json format - uncomment for testing
  serializeJsonPretty(payload, Serial);
  Serial.println();


  // sleep interval of five seconds 
  delay(5000);
 
}