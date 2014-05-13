#include <glcd.h>
#include "fonts/allFonts.h"

#define PIN_TRIGGER 7

void setup() {
  GLCD.Init(NON_INVERTED);
  GLCD.ClearScreen();  
  GLCD.SelectFont(System5x7);
  affichageGLCD(50.0,1);
  pinMode(PIN_TRIGGER,OUTPUT);
}

void loop() {
  unsigned char cptGLCD = 0;
  unsigned char i = 0;
  
  digitalWrite(PIN_TRIGGER,HIGH);
  for (i=0;i<=50;i+=2)
  {
  affichageGLCD (i,1);
  delay(100);
  }

  while (cptGLCD <= 20)
  {
    delay(300);
    cptGLCD++;
    if (digitalRead(PIN_TRIGGER)==HIGH)
    {
      digitalWrite(PIN_TRIGGER,LOW);
    }
    else digitalWrite(PIN_TRIGGER,HIGH);
  }
  cptGLCD=0;
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
    GLCD.GotoXY(54,28);
    GLCD.print("Fin");
    GLCD.CursorTo(4,1);
    GLCD.print("Pesee terminee");
    GLCD.DrawLine(43, 8, 45, 7); // é : accent aigu de pesée
    GLCD.DrawLine(97, 8, 99, 7); // é : accent aigu de terminée
  }
  else
  {
    GLCD.GotoXY(54,28);
    GLCD.print(pourcentPoids, 0);
    GLCD.print("%");
    GLCD.CursorTo(4,1);
    GLCD.print("Pesee en cours");
    GLCD.DrawLine(43, 8, 45, 7); // é : accent aigu
  }
  GLCD.CursorTo(8, 6);
  GLCD.SelectFont(Arial_bold_14);
  GLCD.print(poids, nbDecimale);
  GLCD.print("g");
  GLCD.SelectFont(System5x7);
}

