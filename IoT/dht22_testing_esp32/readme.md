## Testing DHT22 Sensors with an ESP32

Simple sketch to verify that a DHT22 sensor works, it pulls data from the sensors and then outputs the data via serial, which can monitor via serial monitor in VS Code. I built this because sometimes you get a few duds when you order a large number of DHT22s, and this sketch allows me to check as to whether or not it's the sensor or wire causing a data read issue vs it being my code. 

A couple of additional notes:

* Connect the data pin to pin21 on the board OR change the code accordingly 
* The blue light should be blinking on and off if the data is being read successsfully, a solid blue light suggests something is wrong/broken. 
* While the 3.3v pin "should" work, I've found the DHT22s are lot more reliable if you use the 5v pins
* Despite a couple of sensors arriving DOA from time to time, if they work out of the box they should be able to run continuously for years without problems. I have several I put into service in late summer of '23 and I've yet to have any issues. *knock on wood*

