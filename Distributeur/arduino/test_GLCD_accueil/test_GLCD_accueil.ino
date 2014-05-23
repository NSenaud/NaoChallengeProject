#include <glcd.h>
#include "fonts/allFonts.h"
#include "bitmaps/allBitmaps.h"

void setup() {
  GLCD.Init(NON_INVERTED);   // initialise the library
  GLCD.ClearScreen();
  GLCD.DrawBitmap(NaoTete, 0,0, BLACK);
  GLCD.DrawBitmap(NaoLogo, 45,0, BLACK);
  GLCD.SelectFont(System5x7);
  GLCD.CursorTo(1,6);
  GLCD.print("IUT de");
  GLCD.CursorTo(1,7);
  GLCD.print("Cachan"); 

}

void loop() {
  delay(2000);

}
