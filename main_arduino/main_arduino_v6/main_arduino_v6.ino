// Description de la version 1 : Structure, broches, initialisation, interruptions, premières fonctions.
// Description de la version 2 : Révision des broches, interruptions, liaison BlueTooth.
// Description de la version 3 : Test complet de la balance, changement de la library HX711.
// Description de la version 4 : Implantation du GLCD et du DRV8835. Ajustement du LCD et du HX711. Affichages GLCD.
// Description de la version 5 : Amélioration du sans-fil avec interruption. Mode veille et buffer. Bluetooth opérationnel.
// Description de la version 6 : Suppression Infrarouge, fin de course, fourche optique, LCD. Ajout du GLCD.

// Bibliothèques, images et polices
#include "HX711.h"
#include <Servo.h>
#include <glcd.h>
#include "fonts/allFonts.h"
#include "bitmaps/allBitmaps.h"

// du GLCD. /!\ Celles-ci sont fixées dans arduino-1.5.6-r2\libraries\glcd\config\ks0108_Mega.h :
/*
#define glcdCSEL1     48    // CS1 Bitw
#define glcdCSEL2     50    // CS2 Bit
#define glcdRW        28    // R/W Bit
#define glcdDI        26    // D/I Bit
#define glcdEN        30    // EN Bit
#define glcdData0Pin    32
#define glcdData1Pin    34
#define glcdData2Pin    36
#define glcdData3Pin    38
#define glcdData4Pin    40
#define glcdData5Pin    42
#define glcdData6Pin    44
#define glcdData7Pin    46
*/
// du buffer chargé du rétroéclairage du GLCD
#define BUFFER_PIN 12

// du HX711
#define Dout A1
#define Sck A0

// du servomoteur
#define SERVO_PIN 12

// de la commande des moteurs
#define MOT_PWM0_PIN 4
#define MOT_PWM1_PIN 6

// du bouton poussoir
#define BUTTON_PIN 19

// Définition des variables globales volatiles nécessaires aux interruptions
volatile boolean BUTTON_ETAT = LOW;

// Variable de mise en veille
char sleepStatus = 0;
unsigned short count = 0;

// Variable d'état actuel Bluetooth
short state = 0 ;

// Constantes de détection de lancement
#define BUTTON_DETECTED 0
#define BT_DETECTED 2

// Déclaration des objets nécessaires
HX711 scale(Dout, Sck); //HX711 (balance)
Servo myservo; //Servomoteur

void setup()
{
  balanceCalibrageInit();
  glcdNAOintro();  // initialisation du GLCD
  myservo.attach(SERVO_PIN); //attribution de SERVO_PIN au servo
  myservo.write(10); // position initiale.
  pinMode(MOT_PWM0_PIN, OUTPUT); // PWM du moteur 0 en sortie
  pinMode(MOT_PWM1_PIN, OUTPUT); // PWM du moteur 1 en sortie
  pinMode(BUFFER_PIN, OUTPUT);  // Buffer en sortie
  digitalWrite(BUFFER_PIN, HIGH);  // Buffer impédance nulle, backlight = on
  attachInterrupt(4, interruptBUTTON, RISING); //attribution du BUTTON en interruption
  Serial.begin(9600);
  delay(1000); // nécessaire pour réinitialiser la position du servo
  myservo.detach(); // stiffness removed
  GLCDBalanceLancement(13); // non detection
}

void loop()
{
  delay(50);
  count++;
  GLCD.SetDot(66, 31, BLACK);

  if (BUTTON_ETAT == HIGH) //enclenchement par bouton poussoir
  {
    digitalWrite(BUFFER_PIN, HIGH);
    GLCDBalanceLancement(BUTTON_DETECTED);
    automate();
    BUTTON_ETAT = LOW;
    count = 0;
  }

  if (count >= 600)  // 600*50ms = 3000ms = 30s avant mise en veille.
  {
    digitalWrite(BUFFER_PIN, LOW);
    GLCDveille();
    delay(100);
    count = 0;
    //sleepNow();
  }
}
void serialEvent()
{
  unsigned char rcv;
  if (Serial.available() > 0)  //enclenchement par Bluetooth
  {
    rcv = Serial.read();
    Serial.println(rcv);  // J'ai reçu "rcv" : est-ce correct, jeune Nao ?
    decodageBT(rcv);
    Serial.println(state);  // J'en déduit que je suis dans "state", est-ce bon jeune Nao ?
    if (state == 201)  //vérification de la valeur BT : correcte ou non ?
    {
      digitalWrite(BUFFER_PIN, HIGH);
      Serial.println(202, DEC);
      Serial.end();
      GLCDBalanceLancement(BT_DETECTED);
      automate();
      count = 0;
      state = 0;
      glcdNAOintro();
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
  const unsigned char servoInitial = 10;
  const unsigned char servoFinal = 180;

  // Compteur d'envoi Bluetooth
  unsigned short cptProcess = 0; // Processing
  unsigned char cptGLCD = 0;

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
    GLCD.SetDot(24, 8, BLACK);
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
      Serial.begin(9600);
      Serial.println(102, DEC); // Processing
      Serial.println(poidsTronque,DEC); // Poids en cours
      Serial.end();
    }
  }
  cptProcess = 0;

  // Doucement, on approche...
  moteurPWM(vitesseIntermediaire, sensVersReservoir);
  while (poidsActuel <= seuilMax)  // continuer tant que l'on n'a pas atteint le seuil maximum
  {
    GLCD.SetDot(24, 8, BLACK);
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
      Serial.begin(9600);
      Serial.println(102, DEC); // Processing
      Serial.println(poidsTronque,DEC); // Poids en cours
      Serial.end();
    }
  }
  poidsFinal = abs(scale.get_units());
  scale.power_down();
  affichageGLCD(poidsFinal, 1); // pas besoin de fonction spécial résultat sur GLCD.

  // Fini ! On recule un peu le moteur afin que rien ne tombe de plus.
  moteurPWM(vitesseIntermediaire, sensOpposeReservoir);

  while (cptGLCD <= 5)
  {
    GLCD.SetDot(24, 8, BLACK);
    delay(300);
    cptGLCD++;
    if (digitalRead(BUFFER_PIN) == HIGH)
      digitalWrite(BUFFER_PIN, LOW);
    else
      digitalWrite(BUFFER_PIN, HIGH);
  }
  cptGLCD = 0;

  // Allez on arrête tout et on vide le réservoir dans la gamelle. On confirme la fin.
  moteurPWM(vitesseNulle, sensArret);
  myservo.attach(SERVO_PIN); //attribution de SERVO_PIN au servo
  myservo.write(servoFinal);  // alors faire tourner le servomoteur à fond
  Serial.begin(9600);
  Serial.println(200, DEC); // Envoi de code OK
  Serial.end();

  while (cptGLCD <= 10)
  {
    GLCD.SetDot(24, 8, BLACK);
    delay(500);
    cptGLCD++;
    if (digitalRead(BUFFER_PIN) == HIGH)
      digitalWrite(BUFFER_PIN, LOW);
    else
      digitalWrite(BUFFER_PIN, HIGH);
  }
  cptGLCD = 0;

  myservo.attach(SERVO_PIN); //attribution de SERVO_PIN au servo
  myservo.write(servoInitial);  // puis le remettre en position initiale.

  while (cptGLCD <= 5)
  {
    GLCD.SetDot(24, 8, BLACK);
    delay(300);
    cptGLCD++;
    if (digitalRead(BUFFER_PIN) == HIGH)
      digitalWrite(BUFFER_PIN, LOW);
    else
      digitalWrite(BUFFER_PIN, HIGH);
  }
  cptGLCD = 0;

  myservo.detach();

  while (cptGLCD <= 3)
  {
    GLCD.SetDot(24, 8, BLACK);
    delay(300);
    cptGLCD++;
    if (digitalRead(BUFFER_PIN) == HIGH)
      digitalWrite(BUFFER_PIN, LOW);
    else
      digitalWrite(BUFFER_PIN, HIGH);
  }
  cptGLCD = 0;
  GLCDBalanceLancement(13); // non detection
  digitalWrite(BUFFER_PIN, HIGH);  // Buffer impédance nulle, backlight = on
}

void balanceAffichageGrammes (float poidsTronque)
{
  unsigned char nbDecimale = 1;
  if (poidsTronque > 0.2) // résout les problèmes de poids négatifs et les poussières parasites
  {
    affichageGLCD(poidsTronque, nbDecimale); // utilisation du GLCD
  }
  else {
    affichageGLCD(0, nbDecimale); // utilisation du GLCD
  }
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

void decodageBT (unsigned char rcv)
{
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

void GLCDBalanceLancement (unsigned char natureOrdre)
{
  unsigned char cptOK = 0 ;
  GLCD.ClearScreen();
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
      delay(1000);
      break;

    default :
      break;
  }
}

void affichageGLCD (float poids, unsigned char nbDecimale)
{
  float pourcentPoids = 0;
  pourcentPoids = int((poids / (50.f)) * 100);
  GLCD.ClearScreen();
  GLCD.CursorTo(5, 1);
  GLCD.FillRect(14, 20, pourcentPoids, 22, BLACK);
  GLCD.FillRect(43, 24, 38, 14, WHITE);
  if (pourcentPoids >= 100)
  {
    GLCD.GotoXY(54, 28);
    GLCD.print("Fin");
    GLCD.CursorTo(4, 1);
    GLCD.print("Pesee terminee");
    GLCD.DrawLine(43, 8, 45, 7); // é : accent aigu de pesée
    GLCD.DrawLine(97, 8, 99, 7); // é : accent aigu de terminée
  }
  else
  {
    GLCD.GotoXY(54, 28);
    GLCD.print(pourcentPoids, 0);
    GLCD.print("%");
    GLCD.CursorTo(4, 1);
    GLCD.print("Pesee en cours");
    GLCD.DrawLine(43, 8, 45, 7); // é : accent aigu
  }
  GLCD.CursorTo(8, 6);
  GLCD.SelectFont(Arial_bold_14);
  GLCD.print(poids, nbDecimale);
  GLCD.print("g");
  GLCD.SelectFont(System5x7);
}

void balanceCalibrageInit()
{
  scale.set_scale(1950.f); // valeur empirique de calibrage
  scale.tare();
  scale.power_down();
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
}

void GLCDveille()
{
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

/*void sleepNow()
{
  set_sleep_mode(SLEEP_MODE_IDLE);
  sleep_enable();
  power_adc_disable();
  power_spi_disable();
  power_timer0_disable();
  power_timer1_disable();
  power_timer2_disable();
  power_timer3_disable();
  power_timer4_disable();
  power_timer5_disable();
  power_twi_disable();
  sleep_mode();
  sleep_disable();
  power_all_enable();
}*/

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
