#ifndef STC_ML_H
#define STC_ML_H
#include <limits>
#include "common.h"
#include "stc_embed_c.h"
#include "stc_extract_c.h"
typedef unsigned int uint;
typedef unsigned char u8;
const float F_INF=std::numeric_limits<float>::infinity();
const double D_INF=std::numeric_limits<double>::infinity();
float stc_pm1_pls_embed(uint cover_length,int* cover,float* costs,uint message_length,u8* message,uint stc_constraint_height,float wet_cost,int* stego,uint* num_msg_bits,uint &max_trials,float* coding_loss=0);
void stc_ml_extract(uint stego_length,int* stego,uint num_of_layers,uint* num_msg_bits,uint stc_constraint_height,u8* message);
#endif
