#include <Arduino.h>
#include <PMserial.h>

#define RXD2 16   // ESP32 RX2 -> PMS TXO)
#define TXD2 17   // ESP32 TX2 -> PMS RXO)
#define LED 2 // for flashing the LED on and off 

SerialPM pms(PMSx003, Serial2);

void setup() {
  Serial.begin(115200);
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2);  // explicit pins
  pms.init();

  Serial.println("PMserial PMS5003 + ESP32 demo...");
}


void loop() {

  digitalWrite(LED,HIGH); 

  pms.read();
  if (pms) {
    Serial.print("PM1.0: "); Serial.println(pms.pm01);
    Serial.print("PM2.5: "); Serial.println(pms.pm25);
    Serial.print("PM10:  "); Serial.println(pms.pm10);
    Serial.println();
  } else {
    Serial.print("PMS status: ");
    Serial.println(pms.status);   // will show e.g. ERROR_TIMEOUT etc.
  }

  digitalWrite(LED,LOW);

  delay(2000);
}
