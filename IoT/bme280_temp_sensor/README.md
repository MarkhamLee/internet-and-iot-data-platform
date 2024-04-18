### BME 280 Connection Instructions

These instructions are specifically for connecting the device to a Raspberry Pi, it's 
possible that they may work with another device (presuming the driver library is even compatible), but I've never tried it. Note: these are standard connection instructions for devices with the SDA and SCL outputs/pins.

* Connect the power pins, suggest using the 5v for the positive lead
* Connect the SDA and SCL pins of the device to the corresponding pins on the Raspberry Pi:
    * SDA is the 2nd pin in the left row of pins when the USB ports are facing towards you
    * SCL is the 3rd pin, same orientation as above

These devices tend to run fairly stable, when connected properly as above I've rarely had issues with bad readings, device connection errors, etc.