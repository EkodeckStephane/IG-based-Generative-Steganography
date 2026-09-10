#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <random>
#include "common.h"
u32 mats[] = {0};
u32 *getMatrix(int width, int height) {
    u32 *cols=(u32*)malloc(width*sizeof(u32));
    if(height==10 && width==2){cols[0]=519; cols[1]=885; return cols;}
    if(height==10 && width==3){cols[0]=579; cols[1]=943; cols[2]=781; return cols;}
    if(height==10 && width==4){u32 v[4]={685,663,947,805}; for(int i=0;i<4;i++) cols[i]=v[i]; return cols;}
    if(height==10 && width==5){u32 v[5]={959,729,679,609,843}; for(int i=0;i<5;i++) cols[i]=v[i]; return cols;}
    int i,j; u32 r,mask,bop; std::mt19937 rnd(1);
    mask=(1 << (height-2))-1; bop=(1 << (height-1))+1;
    if((1 << (height-2)) < width){
        for(i=0;i<width;i++){r=((rnd() & mask)<<1)+bop; cols[i]=r;}
    } else {
        for(i=0;i<width;i++){
            for(j=-1;j<i;){r=((rnd() & mask)<<1)+bop; for(j=0;j<i;j++) if(cols[j]==r) break;}
            cols[i]=r;
        }
    }
    return cols;
}
