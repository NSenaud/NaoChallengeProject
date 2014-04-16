#include <glcd.h>
#include "fonts/allFonts.h"

void setup() {
  GLCD.Init(NON_INVERTED);
  GLCD.ClearScreen();  
  GLCD.SelectFont(System5x7);
}

void loop() {
  float i;
  for (i=0;i<51;i++)
  {
     affichageGLCD(i,1);
     delay(100);
  }
  delay(3000);
  i=0;
}

inline void affichageGLCD (float poids, unsigned char nbDecimale)
{
  float pourcentPoids = 0;
  pourcentPoids = int((poids / (50.f))*100);
  GLCD.ClearScreen();
  GLCD.CursorTo(4,1);
  GLCD.print("Pesee en cours");
  GLCD.CursorTo(5,1);
  GLCD.FillRect(14,21,pourcentPoids,21,BLACK);
  GLCD.FillRect(43,24,38,14,WHITE);
  GLCD.GotoXY(54,28);
  if (pourcentPoids >=100)
  {GLCD.print("Fin");}
  else 
  {GLCD.print(pourcentPoids,0);GLCD.print("%");}
  GLCD.CursorTo(8,6);
  GLCD.SelectFont(Arial_bold_14);
  GLCD.print(poids,nbDecimale);
  GLCD.print("g");
  GLCD.SelectFont(System5x7);
}

