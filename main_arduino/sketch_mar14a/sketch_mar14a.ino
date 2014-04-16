#include "HX711.h"

float poids=0;
HX711 scale(A1, A0);

void setup() {
  
  Serial.begin(19200);
  Serial.println("c'est parti mes freres");
  //scale.set_gain(32);
  scale.set_scale();
  scale.tare();
  poids = scale.get_units(10);
  poids = poids/100;
}

void loop() {
  
  Serial.println("Placez un poids");
  scale.set_scale();
  scale.tare();
  delay(1500);
  Serial.println("Calibrage en cours");
  poids = scale.get_units(10);
  poids = poids/100.0;
  Serial.println(poids);
  scale.set_scale(poids);
  poids=0;  
  delay(1000);
  
}
