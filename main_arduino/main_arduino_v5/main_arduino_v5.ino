// Description de la version 1 : Structure, broches, initialisation, interruptions, premières fonctions.
// Description de la version 2 : Révision des broches, interruptions, liaison BlueTooth.
// Description de la version 3 : Test complet de la balance, changement de la library HX711.
// Description de la version 4 : Implantation du GLCD et du DRV8835. Ajustement du LCD et du HX711. Affichages GLCD.
// Description de la version 5 : Amélioration du sans-fil avec interruption. Mode veille et buffer. 

// Bibliothèques
#include <IRremote.h>
#include <LiquidCrystal.h>
#include "HX711.h"
#include <Servo.h>
#include <glcd.h>
#include "fonts/allFonts.h"
#include "bitmaps/allBitmaps.h"
#include <avr/power.h>
#include <avr/sleep.h>

// Définition des broches :
// du LCD
const char RS = 22;
const char Enable = 24;
const char D4 = 26;
const char D5 = 28;
const char D6 = 30;
const char D7 = 32;

// du GLCD. /!\ Celles-ci sont fixées dans arduino-1.5.6-r2\libraries\glcd\config\ks0108_Mega.h :
/*
#define glcdCSEL1       33    // CS1 Bit
#define glcdCSEL2       34    // CS2 Bit
#define glcdRW          35    // R/W Bit
#define glcdDI          36    // D/I Bit
#define glcdEN          37    // EN Bit
#define glcdData0Pin    22
#define glcdData1Pin    23
#define glcdData2Pin    24
#define glcdData3Pin    25
#define glcdData4Pin    26
#define glcdData5Pin    27
#define glcdData6Pin    28
#define glcdData7Pin    29
*/
// du buffer chargé du rétroéclairage du GLCD
const char BUFFER_PIN = 7;

// de réception IR
const char RECV_PIN = 8;
// la broche d'émission IR est la PWM 9 (sur le MEGA) (impossible à modifier)
// du module bluetooth : utilisation de UART RX/TX (pin0 et pin1)

// du HX711
const int Dout = A1;
const int Sck = A0;

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

// Variable de mise en veille
char sleepStatus = 0;
unsigned short count = 0;

// Variable d'état actuel Bluetooth
short state = 0 ;

// Constantes de détection de lancement
const unsigned char BUTTON_DETECTED = 0;
const unsigned char IR_DETECTED = 1;
const unsigned char BT_DETECTED = 2;

// Déclaration des objets nécessaires
LiquidCrystal lcd(RS, Enable, D4, D5, D6, D7); //LCD
HX711 scale(Dout, Sck); //HX711 (balance)
IRrecv irrecv(RECV_PIN); //Reception IR
decode_results results; //Decodage et lecture IR
IRsend irsend; //Emission IR
Servo myservo; //Servomoteur

void setup()
{
  balanceCalibrageInit();
  lcd.begin(16, 2); //initialisation d'un lcd 16 colonnes, 2 lignes.
  initLCD(); //initialisation du LCD
  irrecv.enableIRIn(); //activation du récepteur IR
  myservo.attach(SERVO_PIN); //attribution de SERVO_PIN au servo
  myservo.write(0); // position initiale.
  delay(1000); // nécessaire pour réinitialiser la position du servo
  myservo.detach(); // stiffness removed
  pinMode(MOT_PWM0_PIN, OUTPUT); // PWM du moteur 0 en sortie
  pinMode(MOT_PWM1_PIN, OUTPUT); // PWM du moteur 1 en sortie
  pinMode(BARIR_PIN, INPUT); // Barrière infrarouge en entrée sur A2
  pinMode(BUFFER_PIN, OUTPUT);  // Buffer en sortie
  digitalWrite(BUFFER_PIN, HIGH);  // Buffer impédance nulle, backlight = on
  attachInterrupt(0, interruptFIN0, RISING); //attribution du FIN0 en interruption
  attachInterrupt(1, interruptFIN1, RISING); //attribution du FIN1 en interruption
  attachInterrupt(4, interruptBUTTON, RISING); //attribution du BUTTON en interruption
  //glcdNAOintro();  // initialisation du GLCD
  Serial.begin(9600);
}

void loop()
{
  unsigned long codeIR;
  //unsigned char rcv;
  //GLCDBalanceLancement(13); // non detection
  delay(50);
  count++;
  if (BUTTON_ETAT == HIGH) //enclenchement par bouton poussoir
  {
    //GLCDBalanceLancement(BUTTON_DETECTED);
    LCDBalanceLancement(BUTTON_DETECTED);
    automate();
    BUTTON_ETAT = LOW;
    count = 0;
    initLCD(); //initialisation du LCD
  }
  else if (irrecv.decode(&results))  //enclenchement par Infrarouge
  {
    codeIR = results.value;  //récupération de la valeur IR
    irrecv.resume();
    if (decodageIR(codeIR))  //vérification de la valeur IR : correcte ou non ?
    {
      LCDBalanceLancement(IR_DETECTED);
      //GLCDBalanceLancement(IR_DETECTED);
      automate();
      count = 0;
      initLCD();
    }
  }
    if (count >= 60)
    {
      count = 0;
      lcdVeille();
      //GLCDVeille();
      delay(100);
      sleepNow();
      digitalWrite(BUFFER_PIN, HIGH);
      
      delay(1000);
      initLCD();
    }
}
void serialEvent() {
  unsigned char rcv;
  if (Serial.available() > 0)  //enclenchement par Bluetooth
  {
    rcv = Serial.read();
    Serial.print("RCV : ");
    Serial.println(rcv);
    decodageBT(rcv);
    Serial.print("State : ");
    Serial.println(state);
    if (state == 201)  //vérification de la valeur BT : correcte ou non ?
    {
      Serial.end();
      //GLCDBalanceLancement(BT_DETECTED);
      LCDBalanceLancement(BT_DETECTED);
      automate();
      count = 0;
      state = 0;
      initLCD();
      Serial.begin(9600);
    }
  }
}

void automate ()
{
  // Constantes de valeur PWM sur 8 bits, inutilisé
  const unsigned char PWM75 = 191;  // 75%
  const unsigned char PWM50 = 127;  // 50%
  const unsigned char PWM25 = 63;   // 25%
  const unsigned char PWM10 = 25;   // 10%
  const unsigned char PWM0 = 0;     // 00%

  // Constantes de valeurs de sens pour le moteur, sans unité
  const unsigned char sensVersReservoir = 0;
  const unsigned char sensOpposeReservoir = 1;
  const unsigned char sensArret = 40;

  // Constantes de seuils pour la balance, en g
  const float seuilMax = 50.0;
  const float seuilIntermediaire = 40.0;

  // Constantes de vitesse de moteur sur 8 bits
  const unsigned char vitesseMax = 10;
  const unsigned char vitesseIntermediaire = 110;
  const unsigned char vitesseNulle = 0;

  // Constantes d'angles pour le servomoteur, en °
  const unsigned char servoInitial = 0;
  const unsigned char servoFinal = 180;

  // Compteur d'envoi Bluetooth
  unsigned short cptProcess = 0; // Processing
  unsigned short cptOK = 0;

  // Valeur de la dernière valeur de poids avant l'actionnement du servomoteur
  float poidsActuel;
  float poidsPrecedent;
  float poidsTronque;
  float poidsFinal;

  // Allumage de la balance
  scale.power_up();
  scale.tare();

  // A fond les ballons !
  moteurPWM(vitesseMax, sensVersReservoir);
  poidsActuel = scale.get_units();
  poidsTronque = int (poidsActuel * 10);
  poidsTronque /= 10.0;
  balanceAffichageGrammes(poidsTronque);
  while (poidsActuel <= seuilIntermediaire)  // continuer tant que l'on n'a pas atteint le premier seuil
  {
    poidsActuel = scale.get_units() * (-1);
    poidsTronque = int (poidsActuel * 10);
    poidsTronque /= 10.0;
    if (poidsTronque != poidsPrecedent)
    {
      balanceAffichageGrammes(poidsTronque);
    }
    poidsPrecedent = poidsTronque;
    cptProcess += 1;
    if (cptProcess >= 100)
    {
      cptProcess = 0;
      Serial.println(102, DEC); // Processing
    }
  }
  cptProcess = 0;

  // Doucement, on approche...
  moteurPWM(vitesseIntermediaire, sensVersReservoir);
  while (poidsActuel <= seuilMax)  // continuer tant que l'on n'a pas atteint le seuil maximum
  {
    poidsActuel = scale.get_units() * (-1);
    poidsTronque = int (poidsActuel * 10);
    poidsTronque /= 10.0;
    if (poidsTronque != poidsPrecedent)
    {
      balanceAffichageGrammes(poidsTronque);
    }
    poidsPrecedent = poidsTronque;
    cptProcess += 1;
    if (cptProcess >= 100)
    {
      cptProcess = 0;
      Serial.println(102, DEC); // Processing
    }
  }
  poidsFinal = abs(scale.get_units());
  scale.power_down();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Resultat :");
  lcd.setCursor(0, 1);
  lcd.print(poidsFinal, 1);
  lcd.print("g");

  // Fini ! On recule un peu le moteur afin que rien ne tombe de plus, on éteint la balance.
  moteurPWM(vitesseIntermediaire, sensOpposeReservoir);
  delay(3000);

  // Allez on arrête tout et on vide le réservoir dans la gamelle.
  moteurPWM(vitesseNulle, sensArret);
  myservo.attach(SERVO_PIN); //attribution de SERVO_PIN au servo
  myservo.write(servoFinal);  // alors faire tourner le servomoteur à fond
  myservo.detach();

  Serial.println(200, DEC); // Envoi de code OK
  delay(2000);

  myservo.attach(SERVO_PIN); //attribution de SERVO_PIN au servo
  myservo.write(servoInitial);  // puis le remettre en position initiale.
  delay(1000);
  myservo.detach();
  //FIN0_ETAT = LOW;
  delay(1000);
  initLCD ();
}

void balanceAffichageGrammes (float poidsTronque)
{
  unsigned char nbDecimale = 1;
  if (poidsTronque > 0.2) // résout les problèmes de poids négatifs et les poussières parasites
  {
    affichageLCD(poidsTronque, nbDecimale); // utilisation du LCD
  }
  else {
    affichageLCD(0, nbDecimale); // utilisation du LCD
  }
  //affichageGLCD(poids,nbDecimale);  // utilisation du GLCD
}

void moteurPWM (unsigned char valPWM, unsigned char sens)
{
  switch (sens)
  {
    case 0 :  // sensVersReservoir
      analogWrite(MOT_PWM0_PIN, valPWM);
      analogWrite(MOT_PWM1_PIN, 255);
      break;

    case 1 :  // sensOpposeReservoir
      analogWrite(MOT_PWM0_PIN, 255);
      analogWrite(MOT_PWM1_PIN, valPWM);
      break;

    default :  // sensArret
      analogWrite(MOT_PWM0_PIN, 0);
      analogWrite(MOT_PWM1_PIN, 0);
      break;
  }
}

void interruptBUTTON () {
  BUTTON_ETAT = HIGH;
}
void  interruptFIN0 ()  {
  FIN0_ETAT = HIGH;
}
void  interruptFIN1 ()  {
  FIN1_ETAT = HIGH;
}

void IRemetteurRC5(unsigned long data, int nbits)
{
  for (int i = 0; i < 3; i++) // pour envoyer un code RC5, le protocole
  { // stipule qu'il faut l'envoyer 3 fois.
    irsend.sendRC5(data, nbits);
    delay(40);
  }
}

char decodageIR (unsigned long codeIR)
{
  char confirm;
  switch (codeIR)
  {
    case 49 :
      confirm = 1;
      break;
    default :
      confirm = 0;
      break;
  }
  return confirm;
}

void decodageBT (unsigned char rcv)
{
  switch (state)
  {
    case 0:     // Start state
      break;
    case 1:     // Message type: Information
      break;
    case 2:     // Message type: Success
      break;
    case 5:     // Message type: Distributor Error
      break;
    case 10:    // Message type: Information
      break;
    case 20:    // Message type: Success
      break;
    case 50:    // Message type: Distributor Error
      break;
    case 102:   /* Processing */
      break;
    case 200:   /* OK */
      break;
    case 201:   /* Created */
      break;
    case 202:   /* Accepted */
      break;
    case 500:   /* Problem */
      break;
    case 507:   /* Insufficient Storage */
      break;
  }
  switch (rcv)
  {
      /* End Of Line */
    case 10:         if (state == 102
                           || state == 200
                           || state == 201
                           || state == 202
                           || state == 500
                           || state == 507) state = state;
      else                   state =   0; // Error!
      break;
      /* 0 */
    case 48:         if (state ==  1) state =  10;
      else if (state ==  2) state =  20;
      else if (state ==  5) state =  50;
      else if (state == 20) state = 200;
      else if (state == 50) state = 500;
      else                  state =   0; // Error!
      break;
      /* 1 */
    case 49:         if (state ==  0) state =   1;
      else if (state == 20) state = 201;
      else                  state =   0; // Error!
      break;
      /* 2 */
    case 50:         if (state ==  0) state =   2;
      else if (state == 10) state = 102;
      else if (state == 20) state = 202;
      else                  state =   0; // Error!
      break;
      /* 5 */
    case 53:         if (state ==  0) state =   5;
      else                  state =   0; // Error!
      break;
      /* 7 */
    case 55:         if (state == 50) state = 507;
      else                  state =   0; // Error!
      break;
    default:    state = 0; // Error!
      break;
  }
}

void initLCD ()
{
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Balance prete");
  lcd.setCursor(0, 1);
  lcd.print("Attente ordres");
}

void LCDBalanceLancement (unsigned char natureOrdre)
{
  lcd.clear();
  lcd.setCursor(0, 0);
  switch (natureOrdre)
  {
    case 0 :
      lcd.print("Bouton detecte");
      delay(1000);
      break;

    case 1 :
      lcd.print("Infrarouge");
      lcd.setCursor(0, 1);
      lcd.print("detect");
      delay(1000);
      break;

    case 2 :
      lcd.print("Bluetooth");
      lcd.setCursor(0, 1);
      lcd.print("detecte");
      delay(1000);
      break;
  }
}

void GLCDBalanceLancement (unsigned char natureOrdre)
{
  unsigned char cptOK = 0 ;
  GLCD.SelectFont(SystemFont5x7, BLACK);
  GLCD.DrawBitmap(NaoTete, 0, 22, BLACK);
  GLCD.CursorTo(1, 0);
  GLCD.print("Attente");
  GLCD.CursorTo(3, 1);
  GLCD.print("des");
  GLCD.CursorTo(1, 2);
  GLCD.print("ordres");
  GLCD.FillRect(111, 3, 14, 14, BLACK);
  GLCD.DrawCircle(118, 10, 5, WHITE);
  GLCD.DrawBitmap(IR, 112, 25, BLACK);
  GLCD.DrawBitmap(BT, 110, 40, BLACK);
  GLCD.GotoXY(70, 7);
  GLCD.print("Bouton");
  GLCD.GotoXY(48, 25);
  GLCD.print("Infrarouge");
  GLCD.GotoXY(52, 47);
  GLCD.print("Bluetooth");
  switch (natureOrdre)
  {
    case 0 :  //Bouton
      GLCD.InvertRect(67, 4, 40, 12);
      delay(1000);
      break;

    case 1 :  //IR
      GLCD.InvertRect(46, 23, 63, 12);
      delay(1000);
      break;

    case 2 :  //BT
      GLCD.InvertRect(49, 44, 58, 12);
      // Confirmation de la réception : Accepted
      while (cptOK <= 10)
      {
        cptOK += 1;
        Serial.print(200, DEC); // Envoi de 10 codes OK
        delay(100);
      }
      cptOK = 0;
      break;

    default :
      break;
  }
}

void affichageLCD (float poids, unsigned char nbDecimale)
{
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print(poids, nbDecimale); // affichage du poids avec nbDecimale
  lcd.print( " g");
  lcd.setCursor(0, 1);
  if (poids > 50.0) // Condition de seuil de 50g
  {
    lcd.print("Poids > 50g");
  }
  else
  {
    lcd.print("Poids < 50g");
  }
}

void affichageGLCD (float poids, unsigned char nbDecimale)
{
  float pourcentPoids = 0;
  pourcentPoids = int((poids / (50.f)) * 100);
  GLCD.ClearScreen();
  GLCD.CursorTo(4, 1);
  GLCD.print("Pesee en cours");
  GLCD.DrawLine(43, 8, 45, 7); // é : accent aigu
  GLCD.CursorTo(5, 1);
  GLCD.FillRect(14, 20, pourcentPoids, 22, BLACK);
  GLCD.FillRect(43, 24, 38, 14, WHITE);
  GLCD.GotoXY(54, 28);
  if (pourcentPoids >= 100)
  {
    GLCD.print("Fin");
  }
  else
  {
    GLCD.print(pourcentPoids, 0);
    GLCD.print("%");
  }
  GLCD.CursorTo(8, 6);
  GLCD.SelectFont(Arial_bold_14);
  GLCD.print(poids, nbDecimale);
  GLCD.print("g");
  GLCD.SelectFont(System5x7);
}

void balanceCalibrageInit()
{
  scale.set_scale(1965.f); // valeur empirique de calibrage
  scale.tare();
}

void glcdNAOintro()
{
  GLCD.Init(NON_INVERTED);
  GLCD.ClearScreen();
  GLCD.DrawBitmap(NaoTete, 0, 0, BLACK);
  GLCD.DrawBitmap(NaoLogo, 45, 0, BLACK);
  GLCD.SelectFont(System5x7);
  GLCD.CursorTo(1, 6);
  GLCD.print("IUT de");
  GLCD.CursorTo(1, 7);
  GLCD.print("Cachan");
  delay(2000);
}

void lcdVeille()
{
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Veille");
}

void GLCDveille()
{
  digitalWrite(BUFFER_PIN, LOW);
  GLCD.ClearScreen();
  GLCD.DrawBitmap(NaoVeille, 42, 23, BLACK);
  GLCD.SelectFont(Arial_bold_14);
  GLCD.CursorTo(9, 0);
  GLCD.print("Z");
  GLCD.CursorTo(8, 1);
  GLCD.print("Z");
  GLCD.SelectFont(System5x7);
  GLCD.GotoXY(46, 10);
  GLCD.print("Veille");
}

void sleepNow()
{
  set_sleep_mode(SLEEP_MODE_IDLE);
  sleep_enable();
  power_adc_disable();
  power_spi_disable();
  power_timer0_disable();
  power_timer1_disable();
  power_timer2_disable();
  power_twi_disable();
  sleep_mode();
  sleep_disable();
  power_all_enable();
}

void GLCDdatamatrice(int numeroDatamatrice)
{
  GLCD.SelectFont(System5x7);
  GLCD.CursorTo(0, 0);
  GLCD.ClearScreen();
  switch (numeroDatamatrice)
  {
    case 102 :  // Processing
      GLCD.DrawBitmap(datamatrix102, 32, 0, BLACK);
      GLCD.print("102");
      break;

    case 200 :  // OK
      GLCD.DrawBitmap(datamatrix200, 32, 0, BLACK);
      GLCD.print("200");
      break;

    case 201 :  // Created
      GLCD.DrawBitmap(datamatrix201, 32, 0, BLACK);
      GLCD.print("201");
      break;

    case 202 :  // Accepted
      GLCD.DrawBitmap(datamatrix202, 32, 0, BLACK);
      GLCD.print("202");
      break;

    case 500 :  // Internal Server Error
      GLCD.DrawBitmap(datamatrix500, 32, 0, BLACK);
      GLCD.print("500");
      break;

    case 507 :  // Insufficient storage
      GLCD.DrawBitmap(datamatrix507, 32, 0, BLACK);
      GLCD.print("507");
      break;
  }
}
