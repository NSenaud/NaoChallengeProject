      // Description de la version : structure, broches, initialisation, interruptions, premières fonctions.
      // Bibliothèques
      #include <IRremote.h>
      #include <LiquidCrystal.h> 
      #include <hx711.h>
      #include <Servo.h>
      
      // Définition des broches :
      // du LCD
      const char RS = 22;
      const char Enable = 24;
      const char D7 = 26;
      const char D6 = 28;
      const char D5 = 30;
      const char D4 = 32;
      
      // de réception IR
      const char RECV_PIN = 8;
      // la broche d'émission IR est la PWM 9 (sur le MEGA) (impossible à modifier)    
      
      // du HX711
      const int Dout = A0;
      const int Sck = A1;
      
      // du servomoteur
      const char SERVO_PIN = 5; 
      
      // du pont en H
      const char BRIDGE_PIN = 4;
      
      // du bouton poussoir
      const char BUTTON_PIN = 21;
      
      // des capteurs de barrière infrarouge
      const int BARIR_PIN = A2;
      
      // des capteurs de fin de course
      const char FIN0_PIN = 2;
      const char FIN1_PIN = 3;
      
      // Définition des variables globales et états
      
      volatile char BUTTON_ETAT = LOW; 
      volatile char FIN0_ETAT = LOW;
      volatile char FIN1_ETAT = LOW;

      // Déclaration des objets nécessaires
      LiquidCrystal lcd(RS, Enable, D4, D5, D6, D7); //LCD
      Hx711 scale(Dout, Sck); //HX711 (balance)
      IRrecv irrecv(RECV_PIN); //Reception IR
      decode_results results;  //Decodage et lecture IR
      IRsend irsend;  //Emission IR
      Servo myservo;
      
      void setup() 
      { 
        balanceAffichageInit();  //initialisation du LCD
        irrecv.enableIRIn();  //activation du récepteur IR
        myservo.attach(SERVO_PIN);  //attribution de SERVO_PIN au servo
        pinMode(BRIDGE_PIN,OUTPUT);  // PWM pont en H en sortie
        pinMode(BARIR_PIN,INPUT);  // Barrière infrarouge en entrée sur A2
        pinMode(BUTTON_PIN,INPUT); // BUTTON et FIN0 et FIN1 en entrée
        pinMode(FIN0_PIN,INPUT);
        pinMode(FIN1_PIN,INPUT);
        attachInterrupt(0,interruptFIN0,RISING);  //attribution du FIN0 en interruption
        attachInterrupt(1,interruptFIN1,RISING);  //attribution du FIN1 en interruption
        attachInterrupt(2,interruptBUTTON,RISING);  //attribution du BUTTON en interruption
      } 
       
      void loop() 
      {
        if(BUTTON_ETAT==HIGH)
        {
           //lancer le programme en mode manuel
           BUTTON_ETAT=LOW;
        }
        /* else if (nao_nous_a_envoyé_lordre_de_distribuer_les_croquettes)
        {
          //lancer le programme en mode automatique
        }
        */
      }
            
      void interruptBUTTON ()
      {
        BUTTON_ETAT = HIGH;
      }
      
      void interruptFIN0 ()
      {
        // rôle du capteur de fin de course : renvoyer un flag
        FIN0_ETAT = !FIN0_ETAT;
      }
      void interruptFIN1 ()
      {
        // rôle du capteur de fin de course : renvoyer un flag
        FIN1_ETAT = !FIN1_ETAT;
      }

      void IRemetteurRC5(unsigned long data, int nbits)
      {
        for (int i = 0; i < 3; i++) // pour envoyer un code RC5, le protocole
        {                           // stipule qu'il faut l'envoyer 3 fois.
          irsend.sendRC5(data, nbits); 
          delay(40);
        }        
      }
      
      unsigned long IRrecepteurDecode()  //vérifier si les fcts sont faites par interrupt
      {
        unsigned long code;
        if (irrecv.decode(&results)) 
        {
          code = results.value;
          irrecv.resume(); // Receive the next value
        }
        return code;
      }
      
      void balanceAffichageInit ()
      {
       lcd.begin(16,2); //initialisation d'un lcd 16 colonnes, 2 lignes.
       lcd.setCursor(0, 0);
      }
      
      void balanceAffichageGrammes ()
      {
       lcd.setCursor(0,0); 
       lcd.print(scale.getGram(), 1);
       lcd.print(" g"); 
       lcd.print(" "); 
       delay(200);
      }
