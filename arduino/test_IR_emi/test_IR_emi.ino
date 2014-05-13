#include <IRremote.h>

IRrecv irrecv(8); //Reception IR
decode_results results; //Decodage et lecture IR
IRsend irsend; //Emission IR
unsigned long code2=0xA50;
unsigned long codeIR;
int type;
unsigned char i;

void setup() {
  Serial.begin(9600);
  Serial.println("Connexion");
  Serial.println(" ");
  delay(1000);
  irrecv.enableIRIn();
}

void loop() {

  if  (irrecv.decode(&results))  //enclenchement par Infrarouge
  {

    type = results.decode_type;
    codeIR = results.value;
    Serial.print("Code recu : ");
    Serial.println(codeIR, HEX);
    Serial.print("Protocole : ");
    Serial.println(type, HEX);
    if (type==2){
    for (i = 0; i < 10; i++) {
      envoi();
    }
    delay(1000);}
    Serial.println("Emission finie");
    
    irrecv.resume();
    Serial.println("Reprise");
    Serial.println(" ");
  }
  else
  {
    for (i = 0; i < 3; i++) {
      envoi2();
    }
    delay(1000);
    Serial.println("Emission finie");

  }
  Serial.print("     Reception ? ");
  Serial.println(irrecv.decode(&results));
  Serial.println(" ");
  
}

void envoi()
{
  irsend.sendSony(codeIR, 12); // ok
  delay(45);
  irrecv.enableIRIn();
}


void envoi2()
{
  irsend.sendSony(code2, 12); // ok
  delay(45);
  irrecv.enableIRIn();
}

