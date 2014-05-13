#include <glcd.h>
#include "fonts/allFonts.h"
#include "bitmaps/allBitmaps.h"

#include <IRremote.h>

IRrecv irrecv(8); //Reception IR
decode_results results; //Decodage et lecture IR
IRsend irsend; //Emission IR

void setup() {
  GLCD.Init(NON_INVERTED);   // initialise the library
  GLCD.ClearScreen();
  GLCD.SelectFont(System5x7);
  GLCD.print("infrarouge reception");
  irrecv.enableIRIn();
}

void loop() {
  unsigned long codeIR;
  int type;
  if  (irrecv.decode(&results))  //enclenchement par Infrarouge
  {
    
    type = results.decode_type;
    codeIR = results.value;
    GLCD.ClearScreen();
    GLCD.print("infrarouge reception");
    GLCD.CursorTo(1,3);
    GLCD.print(codeIR);
    GLCD.CursorTo(1,5);
    GLCD.print(type);
    irrecv.resume();    
  }

}
