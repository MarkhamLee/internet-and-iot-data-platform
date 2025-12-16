/*
This is a provisioning sketch for ESP32 devices, I use it to load the
device with Wi-Fi creds, MQTT config data and an Uptime Kuma heartbeat 
webook for use in monitoring the device's status. The first time you run
it, it will spin up a web page for you to enter the Wi-Fi creds and
then it will load the MQTT creds from your local environment. Next, it
will send some test data to your MQTT broker and a "heartbeat" to Uptime
Kuma to make sure everything works.

Once everything is up and running you need to comment out the bits
around loading the Wi-Fi creds and then comment out the bit about pulling
the env vars and then re-load it to the device, you're doing this so the
next time you plug in the device it won't erase creds or look for env vars
that might not be available. Once complete you have a device that provided
keep the bits around connecting to Wi-Fi and loading the MQTT vars in 
your new sketches, can be use to build new IoT devices. Also: if you 
don't need MQTT or need to store different data, just alter those parts
of the code to fit your use case. 

Final note: I built this with the Platformio plugin in VS Code so you'll
need to tweak things for this to work with a different IDE. 
*/

#include <iostream>
#include <stdlib.h>
#include <Arduino.h>
#include <WiFiManager.h> 
#include <PicoMQTT.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <Preferences.h>  // this is a standard included library, don't add the one listed in packages
#include "secrets.h"

#define LED 2

PicoMQTT::Client mqtt("");


// Holds all device configuration loaded from NVS
class DeviceConfig {
public:
  String deviceId;
  String mqttHost;
  String mqttUser;
  String mqttSecret;
  String mqttTopic;
  String uptimeKumaUrl;


  void saveVars() {

    Preferences prefs;

    prefs.begin("credentials", false);
    prefs.clear(); 
    
    prefs.putString("mqttUser", MQTT_USER);
    prefs.putString("mqttSecret", MQTT_SECRET);
    prefs.putString("mqttHost", MQTT_HOST);
    prefs.putString("mqttTopic", MQTT_TOPIC);

    Serial.println("MQTT credentials saved");
    // Serial.println(mqttUser);

    prefs.putString("deviceId", DEVICE_ID);
    Serial.println("Device ID saved: ");
    // Serial.println(deviceId);

    prefs.putString("uptimeKumaUrl", UPTIME_KUMA_WEBHOOK);
    Serial.println("Uptime Kuma data saved");

    prefs.end();

  }

  void loadFromPreferences() {
    Preferences preferences;
    preferences.begin("credentials", false);

    deviceId = preferences.getString("deviceId", "");
    mqttHost = preferences.getString("mqttHost", "");
    mqttUser = preferences.getString("mqttUser", "");
    mqttSecret = preferences.getString("mqttSecret", "");
    mqttTopic  = preferences.getString("mqttTopic", "");
    uptimeKumaUrl  = preferences.getString("uptimeKumaUrl", "");

    preferences.end();

    Serial.println("Configuration loaded from Preferences");
    Serial.print("Device ID: ");
    Serial.println(deviceId);
    Serial.print("MQTT user: ");
    Serial.println(mqttUser);
    Serial.print("MQTT topic: ");
    Serial.println(mqttTopic);

  }
};

DeviceConfig config;


// I use this same setup method for all of my ESP32 sketches

void setup() {  

    // setup pin to flash on activity
    pinMode(LED, OUTPUT);

    // start setup for Wi-Fi manager
    WiFi.mode(WIFI_STA); 
 
    Serial.begin(115200);
    
    WiFiManager wm;

    // Supress Debug information
    // wm.setDebugOutput(true);
 
    // reset settings - comment out after you've loaded creds
    // Wi-Fi credentials
    // wm.resetSettings();

    // parameters for Wi-Fi setup 
    // comment out after you've loaded creds
    // replace "esp_setup" with your desired device ID
    // bool res;
    // res = wm.autoConnect("esp_dev_device10", "password");
      
    // Auto Connect esp32_node1 will be part of the device name on your WiFi network
    // this block of code is for auto connecting to Wi-Fi
    digitalWrite(LED,HIGH);
    if (!wm.autoConnect("esp_dev_device10", "password")) {
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

    digitalWrite(LED,LOW);

    // save environmental variables to local storage
    // one the data is saved you can comment this out
    // config.saveVars();

    // Load all configuration data
    config.loadFromPreferences();

    // load MQTT creds and setup the MQTT client
    config.loadFromPreferences();

    // MQTT setup using config
    mqtt.host = config.mqttHost;
    mqtt.port = 1883;
    mqtt.username = config.mqttUser;
    mqtt.password = config.mqttSecret;
    mqtt.client_id = config.deviceId;
    mqtt.begin();

    // setup for external devices connected to the ESP32, e.g., climate sensors

}

void loop() {

  mqtt.loop();

  digitalWrite(LED,HIGH); // blink on when reading and transmitting, off when finished

  // insert code for reading from a sensor

  // build JSON message for MQTT 
  // This is just a sample payload to test/verify that everything is
  // working properly.

  JsonDocument payload; // define json document 

  //Add data to the JSON document
  //Test data to make sure Wi-Fi and MQTT are working  
  
  payload["device_id"] = config.deviceId;
  payload["key1"] = 1;
  payload["key2"] = 2;
  payload["key3"] = 3;

  // send MQTT message
  Serial.println("Sending MQTT message: ");
  auto publish = mqtt.begin_publish(config.mqttTopic, measureJson(payload));
  serializeJson(payload, publish);
  publish.send();

  digitalWrite(LED,LOW); // if you don't see blue led flashing for activity, something is wrong.

  digitalWrite(LED,HIGH); 

  // output payload in json format for monitoring and testing, can be commented out
  serializeJsonPretty(payload, Serial);
  Serial.println();

  // send Uptime Kuma Heartbeat 
  HTTPClient http;
  http.begin(config.uptimeKumaUrl);
  int httpResponseCode = http.GET();

  Serial.print("HTTP Response code: ");
  Serial.println(httpResponseCode);
  http.end();

  digitalWrite(LED,LOW);


  // sleep interval of two seconds
  delay(2000);
 
}