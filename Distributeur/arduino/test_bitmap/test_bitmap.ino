#include <glcd.h>
#include "fonts/SystemFont5x7.h"
#include "bitmaps/allBitmaps.h"

void setup(){

  GLCD.Init(NON_INVERTED);   // initialise the library
  GLCD.ClearScreen();
  GLCD.SelectFont(SystemFont5x7,BLACK);
  GLCD.DrawBitmap(NaoTete,0,22,BLACK);
  GLCD.CursorTo(1,0);
  GLCD.print("Attente");
  GLCD.CursorTo(3,1);
  GLCD.print("des");
  GLCD.CursorTo(1,2);
  GLCD.print("ordres");
  GLCD.FillRect(111,3,14,14,BLACK);
  GLCD.DrawCircle(118,10,5,WHITE);
  GLCD.DrawBitmap(IR,113,26,BLACK);
  GLCD.DrawBitmap(BT,110,40,BLACK);
  GLCD.GotoXY(70,7);
  GLCD.print("Bouton");
  GLCD.GotoXY(48,26);
  GLCD.print("Infrarouge");
  GLCD.GotoXY(52,47);
  GLCD.print("Bluetooth");
  GLCD.InvertRect(67,4,40,12);
  GLCD.InvertRect(46,23,63,12);
  GLCD.InvertRect(49,44,58,12);
}

void loop()
{

}
