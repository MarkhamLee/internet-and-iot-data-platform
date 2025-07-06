## Pulling data from a DHT temp sensor with an ESP32

Simple sketch for pulling data from an DHT22 temperature sensor and sending it out via MQTT with an ESP32 microprocessor. A couple of things to keep in mind while using it:

* Connect the center pin of the DHT to pin21 OR change the pin # in the code
* You should use the 5v pins on the ESP32 as you'll be less likely to get read errors
* You'll need to comment out the parts of the code for storing Wi-Fi creds and do the same for storing the MQTT creds Please refer to the [ESP32 device setup folder](../esp32_device_setup/esp32_store_wifi_&_general_creds) for more details.