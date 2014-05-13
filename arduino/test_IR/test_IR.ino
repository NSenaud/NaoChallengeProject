#include <LiquidCrystal.h>
#include <IRremote.h>
const char RS = 22;
const char Enable = 24;
const char D4 = 26;
const char D5 = 28;
const char D6 = 30;
const char D7 = 32;

LiquidCrystal lcd(RS, Enable, D4, D5, D6, D7); //LCD
IRrecv irrecv(8); //Reception IR
decode_results results; //Decodage et lecture IR
IRsend irsend; //Emission IR

void setup() {
  lcd.begin(16,2); //initialisation d'un lcd 16 colonnes, 2 lignes.
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Infrarouge");
  Serial.begin(9600);
  Serial.println("Nao Challenge : programme de detection des codes infrarouge");
  Serial.println(" ");
  irrecv.enableIRIn();
}

void loop() {
  unsigned long codeIR;
  int type;
  Serial.println ("Envoi de la donnee : 0xDD0");
  Serial.println(" ");
  //irsend.sendSony(0xDD0, 12);
  //delay(1000);
  
  
  if  (irrecv.decode(&results))  //enclenchement par Infrarouge
  {
    type = results.decode_type;
    codeIR = results.value;
    Serial.println("Detection !");
    Serial.print("Protocole : ");
    Serial.println(type);
    Serial.print("Valeur : ");
    Serial.println(codeIR);
    Serial.println(" ");
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print(codeIR);
    lcd.setCursor(0,1);
    lcd.print(type);
    irrecv.resume();    
  }

}
