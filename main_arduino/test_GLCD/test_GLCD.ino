#include <glcd.h>
#include "fonts/SystemFont5x7.h"
#include "bitmaps/NaoTete.h"
#include "bitmaps/NaoLogo.h"

void setup(){

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

void loop(){ 

 }

