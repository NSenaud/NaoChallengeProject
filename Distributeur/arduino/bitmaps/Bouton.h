#include <inttypes.h>
#include <avr/pgmspace.h>

#ifndef Bouton_H
#define Bouton_H

static uint8_t Bouton[] PROGMEM={
18, 18, 
0xFF, 0xFF, 0xFF, 0x7F, 0x1F, 0x0F, 0x0F, 0x07, 0x07, 0x07, 0x07, 0x0F, 0x0F, 0x1F, 0x7F, 0xFF,
0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xF8, 0xE0, 0xC0, 0xC0, 0x80, 0x80, 0x80, 0x80, 0xC0, 0xC0, 0xE0,
0xF8, 0xFF, 0xFF, 0xFF, 0x6B, 0x67, 0x6F, 0x03,
};
#endif  //define Bouton_H 