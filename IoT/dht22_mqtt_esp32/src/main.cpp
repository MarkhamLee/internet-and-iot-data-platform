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

  void loadFromPreferences() {
    Preferences preferences;
    preferences.begin("credentials", false);

    deviceId       = preferences.getString("device_id", "");
    mqttHost       = preferences.getString("mqtt_host", "");
    mqttUser       = preferences.getString("mqtt_user", "");
    mqttSecret     = preferences.getString("mqtt_secret", "");
    mqttTopic      = preferences.getString("mqtt_topic",
                                           "/embedded/esp32_dht22_node1");
    uptimeKumaUrl  = preferences.getString("uptime_kuma_webhook", "");

    preferences.end();

    Serial.println("Configuration loaded from Preferences");
    Serial.print("Device ID: ");
    Serial.println(deviceId);
    Serial.print("MQTT host: ");
    Serial.println(mqttHost);
    Serial.print("MQTT user: ");
    Serial.println(mqttUser);
    Serial.print("MQTT topic: ");
    Serial.println(mqttTopic);
    Serial.print("Uptime Kuma URL: ");
    Serial.println(uptimeKumaUrl);
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


  // uncomment out the preferences class below if/when you need to add 
  // new creds for MQTT, webhooks, etc. 

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

  const char* uptime_kuma_webhook = UPTIME_KUMA_WEBHOOK
  prefs.putString("uptime_kuma_webhook", uptime_kuma_webhook);
  Serial.println("Uptime Kuma data saved");

  prefs.end();
  */


  // Load all configuration data
  config.loadFromPreferences();

  // MQTT setup using config
  mqtt.host      = config.mqttHost;
  mqtt.port      = 1883;
  mqtt.username  = config.mqttUser;
  mqtt.password  = config.mqttSecret;
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

    // Publish to MQTT using topic from config
    auto publish = mqtt.begin_publish(config.mqttTopic, measureJson(payload));
    serializeJson(payload, publish);
    publish.send();

    digitalWrite(LED, LOW);

    // Send Uptime Kuma heartbeat if configured
    if (config.uptimeKumaUrl.length() > 0) {
      HTTPClient http;
      http.begin(config.uptimeKumaUrl);
      int httpResponseCode = http.GET();
      // Optional: log httpResponseCode
      http.end();
    }
  }

  // sleep interval of five seconds
  delay(5000);
}