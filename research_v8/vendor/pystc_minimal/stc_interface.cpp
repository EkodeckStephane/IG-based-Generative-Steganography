#include <iostream>
#include <iomanip>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include "stc_ml_c.h"
#include "stc_interface.h"
#include <Python.h>
extern "C" PyMODINIT_FUNC PyInit_stc_extension(void) {
    static struct PyModuleDef moduledef = {PyModuleDef_HEAD_INIT,"stc_extension",NULL,-1,NULL,NULL,NULL,NULL,NULL};
    return PyModule_Create(&moduledef);
}
u32 h = 10;
LIBRARY_API int stc_hide(u32 cover_length, int* cover, float* costs, u32 message_length, u8* message, int* stego) {
    const u32 n = cover_length; u32 m = message_length; u32 trials = 10;
    unsigned int* num_msg_bits = new unsigned int[2];
    stc_pm1_pls_embed(n, cover, costs, m, message, h, 2147483647, stego, num_msg_bits, trials, 0);
    delete[] num_msg_bits; return 0;
}
LIBRARY_API int stc_unhide(u32 stego_length, int* stego, u32 message_length, u8* message) {
    unsigned int* num_msg_bits = new unsigned int[2];
    num_msg_bits[1] = (u32)(message_length/2); num_msg_bits[0] = message_length-num_msg_bits[1];
    stc_ml_extract(stego_length, stego, 2, num_msg_bits, h, message); return 0;
}
