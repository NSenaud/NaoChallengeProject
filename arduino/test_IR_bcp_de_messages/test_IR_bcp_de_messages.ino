#include <IRremote.h>

IRrecv irrecv(8); //Reception IR
decode_results results; //Decodage et lecture IR
IRsend irsend; //Emission IR



void setup() {
  Serial.begin(9600);
  Serial.println("Connexion");
  Serial.println(" ");
  delay(1000);

}

void loop() {
  unsigned short i, j;
short tableau[32] = {
  0xA90,
  0x3B0,
  0xE90,
  0x338,
  0xB38,
  0x738,
  0xF38,
  0xA50,
  0x2F0,
  0xAF0,
  0x2D0,
  0xA70,
  0xCD0,
  0x070,
  0x1D0,
  0x010,
  0x810,
  0x410,
  0xC10,
  0x210,
  0xA10,
  0x610,
  0xE10,
  0x110,
  0xFD0,
  0x910,
  0xDD0,
  0x490,
  0xC90,
  0x090,
  0x890,
  0x290,
};

  for (i = 0; i < 32; i++) {
    for (j = 0; j < 3; j++) {
      irsend.sendSony(tableau[i], 12);
      delay(45);
      Serial.println(tableau[i], HEX);
    }
    delay(1000);
  }
  Serial.println(" ");
}
