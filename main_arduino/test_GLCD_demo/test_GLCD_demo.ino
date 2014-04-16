#include <glcd.h>
#include "fonts/allFonts.h"
#include "bitmaps/allBitmaps.h"

const char BUFFER_PIN = 7;

void setup() {
  GLCD.Init(NON_INVERTED);   // initialise the library
  GLCD.ClearScreen();
  pinMode(BUFFER_PIN, OUTPUT);
  digitalWrite(BUFFER_PIN, HIGH);
}

void loop() {
  float i;

  GLCD.DrawBitmap(NaoTete, 0, 0, BLACK);
  GLCD.DrawBitmap(NaoLogo, 45, 0, BLACK);
  GLCD.SelectFont(System5x7);
  GLCD.CursorTo(1, 6);
  GLCD.print("IUT de");
  GLCD.CursorTo(1, 7);
  GLCD.print("Cachan");

  delay(2000);
  GLCD.ClearScreen();

  for (i = 0; i < 51; i++)
  {
    affichageGLCD(i, 1);
    delay(100);
  }
  delay(1000);
  i = 0;

  GLCD.ClearScreen();
  /*
  GLCD.DrawBitmap(datamatrix, 32, 0, BLACK);
  GLCD.print("49");
  delay(1000);
  GLCD.ClearScreen();*/

  GLCD.SelectFont(System5x7);
  GLCD.CursorTo(0, 0);

  GLCD.DrawBitmap(datamatrix102, 32, 0, BLACK);
  GLCD.print("102");
  delay(500);
  GLCD.ClearScreen();

  GLCD.DrawBitmap(datamatrix200, 32, 0, BLACK);
  GLCD.print("200");
  delay(500);
  GLCD.ClearScreen();

  GLCD.DrawBitmap(datamatrix201, 32, 0, BLACK);
  GLCD.print("201");
  delay(500);
  GLCD.ClearScreen();

  GLCD.DrawBitmap(datamatrix202, 32, 0, BLACK);
  GLCD.print("202");
  delay(500);
  GLCD.ClearScreen();

  GLCD.DrawBitmap(datamatrix500, 32, 0, BLACK);
  GLCD.print("500");
  delay(500);
  GLCD.ClearScreen();

  GLCD.DrawBitmap(datamatrix507, 32, 0, BLACK);
  GLCD.print("507");
  delay(500);
  GLCD.ClearScreen();

  GLCDveille();
  digitalWrite(BUFFER_PIN, LOW);
  delay(2000);
  digitalWrite(BUFFER_PIN, HIGH);
  GLCD.ClearScreen();


  GLCDBalanceLancement(0);
  delay(1000);
  GLCD.ClearScreen();


  GLCDBalanceLancement(1);
  delay(1000);
  GLCD.ClearScreen();


  GLCDBalanceLancement(2);
  delay(1000);
  GLCD.ClearScreen();

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
inline void affichageGLCD (float poids, unsigned char nbDecimale)
{
  float pourcentPoids = 0;
  pourcentPoids = int((poids / (50.f)) * 100);
  GLCD.ClearScreen();
  GLCD.CursorTo(4, 1);
  GLCD.print("Pesee en cours");
  GLCD.DrawLine(43, 8, 45, 7);
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
void GLCDBalanceLancement (unsigned char natureOrdre)
{
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
