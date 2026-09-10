#ifndef STC_EXTRACT_C_H
#define STC_EXTRACT_C_H
#include "common.h"
int stc_extract(const u8 *stego, int stegolength, u8 *message, int messagelength, int constr_height = 10);
#endif
