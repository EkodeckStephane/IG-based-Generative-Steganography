#ifndef STC_EMBED_C_H
#define STC_EMBED_C_H
#include "common.h"
double stc_embed(const u8 *cover, int coverlength, const u8 *message, int messagelength, const void *profile, bool usedouble, u8 *stego, int constr_height = 10);
#endif
