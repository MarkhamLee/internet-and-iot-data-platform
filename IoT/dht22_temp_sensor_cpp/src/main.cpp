/*
* Pulls data from a dht22 temperature sensor and then
* Sends it to an MQTT broker
*/
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <WiFiManager.h> 
#include <PicoMQTT.h>
#include <ArduinoJson.h>
#include <Preferences.h>

#define DHT_SENSOR_PIN 21 
#define DHT_SENSOR_TYPE DHT22
#define LED 2

DHT dht_sensor(DHT_SENSOR_PIN, DHT_SENSOR_TYPE);

PicoMQTT::Client mqtt("");

String topic = "/embedded/esp32_dht22_node1";

void setup() {  

    // start setup for Wi-Fi manager & collecting MQTT parametrs 
    WiFi.mode(WIFI_STA); 
 
  
    Serial.begin(115200);
    
    WiFiManager wm;

    // Supress Debug information
    wm.setDebugOutput(false);
 
    // reset settings uncomment this and the Wi-Fi setup lines
    // when you need to reset/change the Wi-Fi parameters
    // wm.resetSettings();

    // parameters for Wi-Fi setup page
    // bool res;
    // res = wm.autoConnect("esp32_dht_node1","password");
      
    // Auto Connect esp32_node will be part of the device name on your WiFi network
    if (!wm.autoConnect("esp32_dht22_node1", "password")) {
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

    // One time setup item (like Wi-Fi manager) for loading
    // MQTT creds from environmental variables and saving them
    // the device. IF you use this without having run the setup
    // sketch, run the below, then comment out as it won't be
    // needed again unless you change the MQTT creds.

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

    prefs.end();

    */

    // load MQTT creds from device storage via the Preferences library
    // and then use them to setup the MQTT client.
    Preferences preferences;
    preferences.begin("credentials", false);

    // get MQTT creds
    String host = preferences.getString("mqtt_host", "");
    String user = preferences.getString("mqtt_user", "");
    String secret = preferences.getString("mqtt_secret", "");
    Serial.println("MQTT Credentials Loaded");


    // MQTT setup
    mqtt.host=host;
    mqtt.port=1883;
    mqtt.username=user;
    mqtt.password=secret;
    mqtt.client_id = "esp32_node1";
    mqtt.begin();


    // DHT22 Sensor Setup 
    Serial.begin(9600);
    dht_sensor.begin(); 

    // setup pin to flash on activity
    pinMode(LED, OUTPUT);


}

void loop() {

  mqtt.loop();

  // read humidity
  digitalWrite(LED,HIGH); // blink on when reading and transmitting, off when finished
  float humi  = dht_sensor.readHumidity();
  // read temperature in Celsius
  float tempC = dht_sensor.readTemperature();

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

    // send MQTT message
    auto publish = mqtt.begin_publish(topic, measureJson(payload));
    serializeJson(payload, publish);
    publish.send();
    digitalWrite(LED,LOW); // if ou don't see blue led flashing for activity, something is wrong.

    // output payload in json format - uncomment for testing
    // serializeJsonPretty(payload, Serial);
    // Serial.println();

  }

  // sleep interval of five seconds 
  delay(5000);
 
}