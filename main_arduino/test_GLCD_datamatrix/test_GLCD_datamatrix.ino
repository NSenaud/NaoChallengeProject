#include <glcd.h>
#include "fonts/allFonts.h"
#include "bitmaps/datamatrix.h"

void setup() {
  GLCD.Init(NON_INVERTED);
  GLCD.ClearScreen();
  GLCD.SelectFont(System5x7);
  GLCD.DrawBitmap(datamatrix,32,0,BLACK);
}

void loop() {
  delay(5000);
}
