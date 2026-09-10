#ifndef STC_INTERFACE_H
#define STC_INTERFACE_H
#include "common.h"
#ifdef _WIN32
#define LIBRARY_API extern "C" __declspec(dllexport)
#else
#define LIBRARY_API extern "C"
#endif
LIBRARY_API int stc_hide(u32 cover_length, int* cover, float* costs, u32 message_length, u8* message, int* stego);
LIBRARY_API int stc_unhide(u32 stego_length, int* stego, u32 message_length, u8* message);
#endif
