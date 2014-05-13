#include "HX711.h"

// HX711.DOUT	- pin #A1
// HX711.PD_SCK	- pin #A0

float poids128 = 0;
float poidstronque128;

float poids32 = 0;
float poidstronque32;

boolean tare128 = false;
boolean tare32 = false;

boolean doubletare128 = false;
boolean doubletare32 = false;



HX711 scale(A1, A0);		// parameter "gain" is ommited; the default value 128 is used by the library

void setup() {
  Serial.begin(115200);
  Serial.println("Demonstration du capteur de poids pour le distributeur\t");
  Serial.println("Nao Challenge. IUT de Cachan.\t");
}

void loop() {

  static unsigned long temps = 0;

  Serial.print("Lecture t = ");
  Serial.print(temps);
  Serial.println("s");

  petiteBalance();
  grosseBalance();


  temps = temps + 1;
  delay(1000);
  Serial.println(" ");
}

void petiteBalance() {

  scale.set_gain(128);
  scale.set_scale(1982.f);
  if (tare128 == false) {
    scale.tare();
    tare128 = true;
  }
  if (doubletare128 == false) {
    tare128 = false;
    doubletare128 = true;
  }

  poids128 = scale.get_units();

  poidstronque128 = int (poids128 * 10);
  poidstronque128 /= 10;
  Serial.println("Petite balance :");
  Serial.println(poidstronque128, 1);
}

void grosseBalance() {

  scale.set_gain(32);
  scale.set_scale(130.f);
  if (tare32 == false) {
    scale.tare();
    tare32 = true;
  }
    if (doubletare32 == false) {
    tare32 = false;
    doubletare32 = true;
  }

  poids32 = scale.get_units();

  poidstronque32 = int (poids32 * 10);
  poidstronque32 /= 10;
  Serial.println("Grosse balance :");
  Serial.println(poidstronque32, 0);
}
