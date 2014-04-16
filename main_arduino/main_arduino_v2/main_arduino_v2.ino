// Description de la version 1 : structure, broches, initialisation, interruptions, premières fonctions.
// Description de la version 2 : Révision des broches, interruptions, liaison BluetTooth,

// Bibliothèques
#include <IRremote.h>
#include <LiquidCrystal.h> 
#include <hx711.h>
#include <Servo.h>

// Définition des broches :
// du LCD
const char RS = 22;
const char Enable = 24;
const char D4 = 26;
const char D5 = 28;
const char D6 = 30;
const char D7 = 32;

// de réception IR
const char RECV_PIN = 8;
// la broche d'émission IR est la PWM 9 (sur le MEGA) (impossible à modifier)
// du module bluetooth : utilisation de UART RX/TX (pin0 et pin1)

// du HX711
const int Dout = A0;
const int Sck = A1;

// du servomoteur
const char SERVO_PIN = 5; 

// de la commande des moteurs
const char MOT_PWM0_PIN = 4;
const char MOT_PWM1_PIN = 6;

// du bouton poussoir
const char BUTTON_PIN = 19;

// des capteurs de barrière infrarouge
const int BARIR_PIN = A2;

// des capteurs de fin de course
const char FIN0_PIN = 2;
const char FIN1_PIN = 3;

// Définition des variables globales volatiles nécessaires aux interruptions

volatile int BUTTON_ETAT = LOW; 
volatile int FIN0_ETAT = LOW;
volatile int FIN1_ETAT = LOW;

// Déclaration des objets nécessaires
LiquidCrystal lcd(RS, Enable, D4, D5, D6, D7); //LCD
Hx711 scale(Dout, Sck); //HX711 (balance)
IRrecv irrecv(RECV_PIN); //Reception IR
decode_results results; //Decodage et lecture IR
IRsend irsend; //Emission IR
Servo myservo; //Servomoteur

void setup() 
{
  balanceAffichageInit(); //initialisation du LCD
  irrecv.enableIRIn(); //activation du récepteur IR
  myservo.attach(SERVO_PIN); //attribution de SERVO_PIN au servo
  Serial.begin(9600); // initialisation du débit série à 9600bauds/s
  pinMode(MOT_PWM0_PIN,OUTPUT); // PWM du moteur 0 en sortie
  pinMode(MOT_PWM1_PIN,OUTPUT); // PWM du moteur 1 en sortie
  pinMode(BARIR_PIN,INPUT); // Barrière infrarouge en entrée sur A2
  attachInterrupt(0,interruptFIN0,RISING); //attribution du FIN0 en interruption
  attachInterrupt(1,interruptFIN1,RISING); //attribution du FIN1 en interruption
  attachInterrupt(4,interruptBUTTON,RISING); //attribution du BUTTON en interruption
}

void loop() 
{
  unsigned long codeIR;
  unsigned short codeBT;
  delay(50);
  if (BUTTON_ETAT==HIGH)  //enclenchement par bouton poussoir
  {
    automate();
    BUTTON_ETAT=LOW;
  }

  else if  (irrecv.decode(&results))  //enclenchement par Infrarouge
  {
    codeIR = results.value;  //récupération de la valeur IR
    irrecv.resume();
    if (decodageIR(codeIR))  //vérification de la valeur IR : correcte ou non ?
    {
      automate();
    }
  }

  else if (Serial.available() > 0)  //enclenchement par Bluetooth
  {
    codeBT = Serial.read();
    if (decodageBT(codeBT))  //vérification de la valeur BT : correcte ou non ?
    {
      automate();
    }
  }
}

void automate ()
{ 
  // Constantes de valeur PWM, en %
  const unsigned char PWM75 = 191;  // 75%
  const unsigned char PWM50 = 127;  // 50%
  const unsigned char PWM25 = 63;   // 25%
  const unsigned char PWM10 = 25;   // 10%
  const unsigned char PWM0 = 0;     // 00%

  // Constantes de valeurs de sens pour le moteur, sans unité
  const unsigned char sensVersReservoir = 0;
  const unsigned char sensOpposeReservoir = 1;
  const unsigned char sensArret = 2;

  // Constantes de seuils pour la balance, en g
  const float seuilMax = 50.0;
  const float seuilIntermediaire = 40.0;

  // Constantes d'angles pour le servomoteur, en °
  const unsigned char servoInitial = 0;
  const unsigned char servoFinal = 120;

  // A fond les ballons !
  moteurPWM(PWM50, sensVersReservoir);
  while (scale.getGram() != seuilIntermediaire)  // continuer tant que l'on n'a pas atteint le premier seuil
  {
    balanceAffichageGrammes();
  }

  // Doucement, on approche...
  moteurPWM(PWM25, sensVersReservoir);
  while (scale.getGram() != seuilMax)  // continuer tant que l'on n'a pas atteint le seuil maximum
  {
    balanceAffichageGrammes();  
  }

  // Fini ! On recule un peu le moteur afin que rien ne tombe de plus...
  moteurPWM(PWM10, sensOpposeReservoir);
  delay(3000);

  // Allez on arrête tout et on vide le réservoir dans la gamelle.
  moteurPWM(PWM0, sensArret);
  while (FIN0_ETAT != HIGH)  // tant que fin de course 0 non détecté..
  {
    myservo.write(servoFinal);  // alors faire tourner le servomoteur à fond
  }
  myservo.write(servoInitial);  // puis le remettre en position initiale.
  FIN0_ETAT = LOW;
  delay(3000);
}

void moteurPWM (unsigned char valPWM, unsigned char sens)
{
  switch (sens)
  {
  case 0 :  // sensVersReservoir
    analogWrite(MOT_PWM0_PIN, valPWM);
    analogWrite(MOT_PWM1_PIN, 0);
    break;

  case 1 :  // sensOpposeReservoir
    analogWrite(MOT_PWM0_PIN, 0);
    analogWrite(MOT_PWM1_PIN, valPWM);
    break;

  default :  // sensArret
    analogWrite(MOT_PWM0_PIN, 0);
    analogWrite(MOT_PWM1_PIN, 0);    
    break;
  }
}

void interruptBUTTON ()
{
  BUTTON_ETAT = HIGH;
}

void interruptFIN0 ()
{
  // rôle du capteur de fin de course : renvoyer un flag
  FIN0_ETAT = HIGH;
}
void interruptFIN1 ()
{
  // rôle du capteur de fin de course : renvoyer un flag
  FIN1_ETAT = HIGH;
}

void IRemetteurRC5(unsigned long data, int nbits)
{
  for (int i = 0; i < 3; i++) // pour envoyer un code RC5, le protocole
  {                           // stipule qu'il faut l'envoyer 3 fois.
    irsend.sendRC5(data, nbits); 
    delay(40);
  }
}

char decodageIR (unsigned long codeIR)
{
  char confirm;
  switch (codeIR)
  {
  case 0xA :  // inclure ici les codes IR du Nao
    confirm=1;
    break;

  default :
    confirm=0;
    break;
  }
  return confirm;
}

char decodageBT (unsigned short codeBT)
{
  char confirm;
  switch (codeBT)
  {
  case 0xA :  // inclure ici les codes BT du Nao
    confirm=1;
    break;

  default :
    confirm=0; 
    break;
  }
  return confirm;
}

void balanceAffichageInit ()
{
  lcd.begin(16,2); //initialisation d'un lcd 16 colonnes, 2 lignes.
  lcd.setCursor(0, 0);
  lcd.clear();
}

void balanceAffichageGrammes ()
{
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(scale.getGram(), 1);
  lcd.print(" g"); 
  lcd.print(" "); 
  delay(250);
}

