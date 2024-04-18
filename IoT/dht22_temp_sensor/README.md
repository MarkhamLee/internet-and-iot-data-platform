### DHT22 Temperature & Humidity Sensor

Small container for collecting data from a DHT22 temperature ahd humidity sensor, connected to a Raspberry Pi via GPIO pins. I've tested this code on Raspian and the official Ubuntu distro for Raspberry Pi. 


### Connection Instructions 
* Connect the center pin to pin "104" or the the 4th pin in the left hand row of GPIO pins, when the device's USB and LAN ports are facing towards you. 
* Connect to other two pins to their respective power and ground pins, or:
    * Positive to the first pin on the top right when the device's LAN and USB ports are facing you
    * Ground to the 3rd pin, same orientation as above 
Note: you can connect to any power or ground pins, BUT it's advisible to use the 5v pins, as the device
tends to work better when you do.

