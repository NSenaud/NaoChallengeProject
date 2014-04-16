#include <IRremote.h>

IRrecv irrecv(8); //Reception IR
decode_results results; //Decodage et lecture IR
IRsend irsend; //Emission IR

void setup() {
  irrecv.enableIRIn();
  Serial.begin(9600);
  Serial.println("Connexion etablie");
  Serial.println(" ");
}

void loop() {
  
  
  Serial.println("Envoi de la donnee : 0xA70");
  irsend.sendSony(0xA70, 12); // ok
  delay(1000);
  Serial.println("Envoi de la nouvelle donnee : 0xEAD");
  irsend.sendSony(0xEAD, 12); // ok
  delay(1000);
}
