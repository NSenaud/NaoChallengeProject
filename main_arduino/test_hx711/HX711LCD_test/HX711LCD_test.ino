#include "HX711.h"
#include <LiquidCrystal.h>

HX711 scale(A1, A0);		// parameter "gain" is ommited; the default value 128 is used by the library
LiquidCrystal lcd(22, 24, 26, 28, 30, 32);

float poids = 0;
void setup() {
  Serial.begin(38400);
  scale.set_scale(1982.f);
  scale.tare();
  lcd.begin(16, 2);
  lcd.clear();
}

void loop() {

  if (scale.get_units()*(-1)>0)
  {
    poids = scale.get_units()*(-1);
  }
  else poids = 0;
  
  if ((scale.get_units()*(-1)>=0.1) && (scale.get_units()*(-1)<=0.3)) 
  {poids=0;}

  scale.power_down();
  delay(10);
  lcd.setCursor(0,0);
  lcd.clear();    
  lcd.print(poids,0);
  lcd.print( " g");
  lcd.setCursor(0,1);
  if (poids > 50)
  {lcd.print("Poids > 50g");}
  else
  {lcd.print("Poids < 50g");}
  scale.power_up();
}
