#include <glcd.h>
#include "fonts/allFonts.h"
#include "bitmaps/allBitmaps.h"


void setup() {
  GLCD.Init(NON_INVERTED);
  GLCD.ClearScreen();
  GLCD.SelectFont(System5x7);
}

void loop() {
  GLCDdatamatrice(102);
  delay(1000);
  GLCDdatamatrice(200);
  delay(1000);
  GLCDdatamatrice(201);
  delay(1000);
  GLCDdatamatrice(202);
  delay(1000);
  GLCDdatamatrice(500);
  delay(1000);
  GLCDdatamatrice(507);
  delay(1000);
}

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
