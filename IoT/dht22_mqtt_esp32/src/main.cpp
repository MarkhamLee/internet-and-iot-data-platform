/*
* Pulls data from a dht22 temperature sensor and then
* Sends it to an MQTT broker
* Includes a http get request to uptime kuma, so
* the status of the device can be monitored. 
*/
#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <WiFiManager.h>
#include <PicoMQTT.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>
#include <Preferences.h>
#include "secrets.h"

#define DHT_SENSOR_PIN 21
#define DHT_SENSOR_TYPE DHT22
#define LED 2

DHT dht_sensor(DHT_SENSOR_PIN, DHT_SENSOR_TYPE);

// MQTT client (host, creds, etc. set in setup)
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

void setup() {
  // Serial and WiFi
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);

  WiFiManager wm;
  wm.setDebugOutput(false);

  // reset settings uncomment this and the Wi-Fi setup lines
  // when you need to reset/change the Wi-Fi parameters
  // wm.resetSettings();

  // parameters for Wi-Fi setup page
  // bool res;
  // res = wm.autoConnect("esp32_dht_node1","password");


  if (!wm.autoConnect("esp32_dht22_node1", "password")) {
    Serial.println("failed to connect and hit timeout");
    ESP.restart();
    delay(1000);
  } else {
    Serial.println("WiFi connected");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  }

  // save environmental variables to local storage
  // one the data is saved you can comment this out
  // config.saveVars();

  // Load all configuration data
  config.loadFromPreferences();

  // MQTT setup using config
  mqtt.host = config.mqttHost;
  mqtt.port = 1883;
  mqtt.username = config.mqttUser;
  mqtt.password = config.mqttSecret;
  mqtt.client_id = config.deviceId;
  mqtt.begin();

  // DHT22 Sensor Setup
  dht_sensor.begin();

  // LED for activity
  pinMode(LED, OUTPUT);
}

void loop() {

  mqtt.loop();

  digitalWrite(LED, HIGH);

  float humi  = dht_sensor.readHumidity();
  float tempC = dht_sensor.readTemperature();

  if (isnan(tempC) || isnan(humi)) {
    Serial.println("Failed to read from DHT sensor!");
    // TODO: add MQTT alert / counter for failures
  } else {

    // Build JSON payload
    JsonDocument payload;
    payload["temperature"] = tempC;
    payload["humidity"]    = humi;

    // measureJson(payload);
    // serializeJsonPretty(payload, Serial);

    // Publish to MQTT using topic from config
    auto publish = mqtt.begin_publish(config.mqttTopic, measureJson(payload));
    serializeJson(payload, publish);
    publish.send();

    digitalWrite(LED, LOW);


    // Send Uptime Kuma heartbeat if configured
    if (config.uptimeKumaUrl.length() > 0) {

      digitalWrite(LED, HIGH);

      // Serial.println("Verifying entered the Kuma loop");
      HTTPClient http;
      http.begin(config.uptimeKumaUrl);
      int httpResponseCode = http.GET();
      http.end();

      digitalWrite(LED, LOW);

    }

  }

  // sleep interval of 15 seconds
  delay(15000);
}