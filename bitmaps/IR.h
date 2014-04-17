#include <inttypes.h>
#include <avr/pgmspace.h>

#ifndef IR_H
#define IR_H

static uint8_t IR[] PROGMEM={
12,11,
/*0x00, 0x06, 0x1C, 0x30, 0x00, 0x9F, 0x9F, 0x00, 
0x30, 0x1C, 0x06, 0x00, 0x04, 0x06, 0x06, 0x06,*/
128, 130, 142, 152, 192, 239, 239, 192, 152, 142, 130, 128,   0,   0,   0,   0,   0, 
};
#endif  //define IR_H 

