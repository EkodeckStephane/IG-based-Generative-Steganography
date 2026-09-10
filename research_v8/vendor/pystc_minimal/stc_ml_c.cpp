#include "stc_ml_c.h"
#include <cmath>
#include <algorithm>
#include <cstring>
#include <random>
#include <vector>
#include <stdexcept>

static inline uint mod_i(int x,int m){int tmp=x-(x/m)*m+m;return (uint)(tmp%m);}
static void randperm(uint n,uint seed,uint* perm){std::mt19937 rnd(seed);for(uint i=0;i<n;i++)perm[i]=i;for(uint i=0;i<n;i++){uint j=rnd()%(n-i);uint tmp=perm[i];perm[i]=perm[i+j];perm[i+j]=tmp;}}
static double entropy_for_lambda(uint n,const std::vector<double>& c,double lambda){const double L2=std::log(2.0);double h=0;for(uint i=0;i<n;i++){double z=0,d=0;for(uint j=0;j<4;j++){double rho=c[j*n+i];double q=std::isinf(rho)?0.0:std::exp(-lambda*rho);z+=q;if(q>0)d+=rho*q;}if(z>0){h += lambda*d/z + std::log(z);} }return h/L2;}
static double get_lambda_entropy(uint n,const std::vector<double>& c,double payload,double initial=2.0){double l1=0,l3=initial,p1=n*2.0,p3=payload+1;int j=0;while(p3>payload){l3*=2;p3=entropy_for_lambda(n,c,l3);if(++j>20)break;}while((p1-p3)/n > payload/n*1e-2){double l2=l1+(l3-l1)/2;double p2=entropy_for_lambda(n,c,l2);if(p2<payload){l3=l2;p3=p2;}else{l1=l2;p1=p2;}}return l1+(l3-l1)/2;}
static void embed_trial(uint n,const std::vector<double>& prob0,u8* message,uint h,uint &num_msg_bits,uint* perm,u8* stego,uint &trial,uint max_trials){bool success=false;std::vector<u8> cover(n);std::vector<double> cost(n);while(!success){randperm(n,num_msg_bits,perm);for(uint i=0;i<n;i++){double p=prob0[i];cover[perm[i]]=(p<0.5)?1:0;double mx=std::max(p,1-p);cost[perm[i]]=-std::log((1.0/mx)-1.0);if(std::isnan(cost[perm[i]]))cost[perm[i]]=D_INF;}std::memcpy(stego,cover.data(),n);try{if(num_msg_bits)stc_embed(cover.data(),n,message,num_msg_bits,(void*)cost.data(),true,stego,h);success=true;}catch(stc_exception& e){if(e.error_id!=4)throw;num_msg_bits--;trial++;if(trial>max_trials)throw stc_exception("Maximum number of trials in layered construction exceeded (2).",6);}}}
float stc_pm1_pls_embed(uint cover_length,int* cover,float* costs,uint message_length,u8* message,uint h,float wet_cost,int* stego,uint* num_msg_bits,uint &max_trials,float* coding_loss){
 uint n=cover_length+4-(cover_length%4);std::vector<int> vals(4*cover_length);std::vector<double> c(4*n,D_INF);for(uint i=0;i<n;i++)c[i]=0.0;
 for(uint i=0;i<cover_length;i++){float cc[4]={costs[3*i],costs[3*i+1],costs[3*i+2],wet_cost};int vv[4]={cover[i]-1,cover[i],cover[i]+1,cover[i]+2};for(int t=0;t<4;t++){uint s=mod_i(vv[t],4);vals[4*i+s]=vv[t];c[s*n+i]=cc[t];}}
 for(uint i=0;i<n;i++){double mn=D_INF;for(uint j=0;j<4;j++)mn=std::min(mn,c[j*n+i]);if(std::isfinite(mn))for(uint j=0;j<4;j++)if(std::isfinite(c[j*n+i]))c[j*n+i]-=mn;}
 uint m_actual=std::min(2*cover_length,message_length);double lambda=get_lambda_entropy(n,c,m_actual,2.0);std::vector<double> p(4*n);for(uint i=0;i<n;i++){double z=0;for(uint j=0;j<4;j++){double q=std::isinf(c[j*n+i])?0.0:std::exp(-lambda*c[j*n+i]);p[j*n+i]=q;z+=q;}for(uint j=0;j<4;j++)p[j*n+i]/=z;}
 std::vector<double> p10(cover_length),p20(cover_length);std::vector<u8> s1(cover_length),s2(cover_length);std::vector<uint> perm1(cover_length),perm2(cover_length);for(uint i=0;i<cover_length;i++)p20[i]=p[i]+p[i+n];num_msg_bits[1]=message_length/2;uint trial=0;embed_trial(cover_length,p20,message,h,num_msg_bits[1],perm2.data(),s2.data(),trial,max_trials);for(uint i=0;i<cover_length;i++){if(s2[perm2[i]]==0)p10[i]=p[i]/(p[i]+p[i+n]);else p10[i]=p[i+2*n]/(p[i+2*n]+p[i+3*n]);}num_msg_bits[0]=m_actual-num_msg_bits[1];embed_trial(cover_length,p10,message+num_msg_bits[1],h,num_msg_bits[0],perm1.data(),s1.data(),trial,max_trials);
 float distortion=0;for(uint i=0;i<cover_length;i++){uint s=2*s2[perm2[i]]+s1[perm1[i]];stego[i]=vals[4*i+s];distortion+=costs[3*i + (stego[i]-cover[i]+1)];}max_trials=trial;if(coding_loss)*coding_loss=0;return distortion;
}
void stc_ml_extract(uint n,int* stego,uint layers,uint* num_msg_bits,uint h,u8* message){std::vector<u8> bits(n);std::vector<uint> perm(n);u8* ptr=message;for(uint l=layers;l>0;l--){if(num_msg_bits[l-1]){randperm(n,num_msg_bits[l-1],perm.data());for(uint i=0;i<n;i++)bits[perm[i]]=mod_i(stego[i],1<<l)>>(l-1);stc_extract(bits.data(),n,ptr,num_msg_bits[l-1],h);ptr+=num_msg_bits[l-1];}}}
