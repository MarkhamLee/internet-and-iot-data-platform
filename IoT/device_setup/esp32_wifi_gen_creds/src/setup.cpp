/*
I build this with Platformio - you may need to change
things for it to work with the Arduino IDE.
This is a provisioning sketch for ESP32 devices, the MQTT
creds are loaded from environmental variables on my local
device,  and I enter in the Wi-Fi credentials on my iPad 
(or any device with Wi-Fi) via the Wi-Fi manager setup
web page, and then all the variables are stored on the
device. Once that's done you can comment out or delete the
lines of code used for loading that data and write your app code
without having to worry about loading Wi-Fi credentials,
MQTT creds, etc.
*/

#include <iostream>
#include <stdlib.h>
#include <Arduino.h>
#include <WiFiManager.h> 
#include <PicoMQTT.h>
#include <ArduinoJson.h>
#include <Preferences.h>  // this is a standard included library, don't add the one listed in packages

#define LED 2


PicoMQTT::Client mqtt("");

String topic = "/embedded/esp32_setup_verify";

void setup() {  

    // start setup for Wi-Fi manager
    WiFi.mode(WIFI_STA); 
 
    Serial.begin(115200);
    
    WiFiManager wm;

    // Supress Debug information
    wm.setDebugOutput(true);
 
    // reset settings - comment out after you've loaded creds
    // Wi-Fi credentials
    wm.resetSettings();

    // parameters for Wi-Fi setup 
    // comment out after you've loaded creds
    // replace "esp_setup" with your desired device ID
    bool res;
    res = wm.autoConnect("esp_setup", "password");
      
    // Auto Connect esp32_node1 will be part of the device name on your WiFi network
    // this block of code is for auto connecting to Wi-Fi
    if (!wm.autoConnect("esp_setup", "password")) {
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

    // MQTT creds - saving to device
    // Use preferences + "getenv" to load environmental variables and save
    // to the device. In this case, we're loading and saving MQTT creds. 
    // Comment out after saving the data to the device, it won't be needed
    // for subsequent code updates unless you change the creds.

    // Instantiate the preferences class
    Preferences prefs;

    prefs.begin("credentials", false);

    // Comment out after you've saved the creds. Note: you can apply
    // the below to any vars you want to store on the device. Just be
    // mindful of the limited space.
    
    const char* mqtt_user =  getenv ("MQTT_USER");
    const char* mqtt_secret = getenv ("MQTT_SECRET");
    const char* mqtt_host = getenv ("MQTT_HOST");

    prefs.putString("mqtt_user", mqtt_user);
    prefs.putString("mqtt_secret", mqtt_secret);
    prefs.putString("mqtt_host", mqtt_host);

    Serial.println("MQTT credentials saved");

    prefs.end();

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
    mqtt.client_id = "esp32_setup_test";
    mqtt.begin();

    // setup pin to flash on activity
    pinMode(LED, OUTPUT);

    // setup for external devices connected to the ESP32, e.g., climate sensors


}


void loop() {

  mqtt.loop();

  digitalWrite(LED,HIGH); // blink on when reading and transmitting, off when finished

  // insert code for reading from sensor


  // build JSON message for MQTT 
  // This is just a sample payload to test/verify that everything is
  // working properly.

  JsonDocument payload; // define json document 

  //Add data to the JSON document
  //Test data to make sure Wi-Fi and MQTT are working  
  payload["key1"] = 1;
  payload["key2"] = 2;
  payload["key3"] = 3;

  // send MQTT message
  auto publish = mqtt.begin_publish(topic, measureJson(payload));
  serializeJson(payload, publish);
  publish.send();
  digitalWrite(LED,LOW); // if the LED isn't blinking, the above isn't working properly

  // output payload in json format - comment out post testing
  serializeJsonPretty(payload, Serial);
  Serial.println();


  // sleep interval of two seconds
  delay(2000);
 
}