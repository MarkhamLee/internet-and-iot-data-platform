### Connection Instructions 

These instructions are specifically for connecting the device to a Raspberry Pi, it's 
possible that they may work with another device (presuming the driver library is even compatible), but I've never tried it.

* Connect the power pins, suggest using the 5v for the positive lead
* Connect the SDA and SCL pins of the device to the corresponding pins on the Raspberry Pi:
    * SDA is the 2nd pin in the left row of pins when the USB ports are facing towards you
    * SCL is the 3rd pin, same orientation as above

#### Additional Details 
* This device needs to run for a good 24 hours before you start getting accurate readings 
* You will likely get random readings that are excessively high, I would often disconnect and reconnect the device when that happened.
* Finding a way to calibrate the device/improve reading consistency is on my to do list