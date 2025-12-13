## Pulling data from a DHT temp sensor with an ESP32

Simple sketch for pulling data from an DHT22 temperature sensor and sending it out via MQTT with an ESP32 microprocessor. A couple of things to keep in mind while using it:

* Connect the center pin of the DHT to pin21 OR change the pin # in the code
* You should use the 5v pins on the ESP32 as you'll be less likely to get read errors
* You'll need to comment out the parts of the code for storing Wi-Fi creds 
* For the secrets for MQTT and Uptime Kuma, create a page called "secrets." and then store the secrets per the example.  
* If you want to use the uptime kuma capabilities, you'll need to do the following:
    * Go into Uptime Kuma and generate a "New Monitor"
    * Generate a monitor of type "push"
    * Copy the push URL
    * Store the url in a secrets.h file - use the secrets_sample.h file as a template 