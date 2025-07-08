/*
This is a provisioning sketch for ESP32 devices, I use it to load the
device with Wi-Fi and MQTT credentials. The first time you run it, it
will spin up a web page for you to enter the Wi-Fi creds  and
then it will load the MQTT creds from your local environment. Finally, it
will send some test data to your MQTT broker to validate that everything
works. Once everything is up and running you need to comment out the bits
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
#include <Preferences.h>  // this is a standard included library, don't add the one listed in packages

#define LED 2

String device_id = "esp_dev_device10";


PicoMQTT::Client mqtt("");

String topic = "/embedded/esp32_setup_verify";

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
    // end Wi-Fi Manager setup 

    // MQTT creds - saving to device
    // Use preferences + "getenv" to load environmental variables and save
    // to the device. In this case, we're loading and saving MQTT creds. 
    // Comment out after saving the data to the device, it won't be needed
    // for subsequent code updates unless you change the creds.

    // Instantiate the preferences class

    // The second time you run this, comment out everything between
    // "Preferences prefs" and "prefs.end()", as there is no need
    // to reload the env variables the second time as they're already
    // stored on the device.
    
    /*
    Preferences prefs;

    prefs.begin("credentials", false);

    // Comment out after you've saved the creds. Note: you can apply
    // the below to any vars you want to store on the device. Just be
    // mindful of the limited space.
    
    const char* mqtt_user = MQTT_USER;
    const char* mqtt_secret = MQTT_SECRET;
    const char* mqtt_host = MQTT_HOST;

    prefs.putString("mqtt_user", mqtt_user);
    prefs.putString("mqtt_secret", mqtt_secret);
    prefs.putString("mqtt_host", mqtt_host);

    Serial.println("MQTT credentials saved");
    Serial.println(mqtt_user);

    prefs.end();
    */

    // load MQTT creds and setup the MQTT client
    Preferences preferences;

    preferences.begin("credentials", false);

    preferences.putString("DEVICE_ID", device_id);

    // get MQTT creds
    String host = preferences.getString("mqtt_host", "");
    String user = preferences.getString("mqtt_user", "");
    String secret = preferences.getString("mqtt_secret", "");

    // MQTT setup
    mqtt.host=host;
    mqtt.port=1883;
    mqtt.username=user;
    mqtt.password=secret;
    mqtt.client_id = device_id;
    mqtt.begin();

    // setup for external devices conn ected to the ESP32, e.g., climate sensors


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
  
  payload["device_id"] = device_id;
  payload["key1"] = 1;
  payload["key2"] = 2;
  payload["key3"] = 3;

  // send MQTT message
  Serial.println("Sending MQTT message: ");
  auto publish = mqtt.begin_publish(topic, measureJson(payload));
  serializeJson(payload, publish);
  publish.send();

  digitalWrite(LED,LOW); // if you don't see blue led flashing for activity, something is wrong.

  // output payload in json format for monitoring and testing, can be commented out
  serializeJsonPretty(payload, Serial);
  Serial.println();


  // sleep interval of two seconds
  delay(5000);
 
}