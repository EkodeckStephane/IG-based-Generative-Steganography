#ifndef COMMON_H
#define COMMON_H

#include <string>

typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;

extern u32 mats[];

class stc_exception : public std::exception {
public:
    stc_exception(std::string message, u32 error_id) { this->message = message; this->error_id = error_id; }
    virtual ~stc_exception() throw() {}
    virtual const char* what() const throw() { return message.c_str(); }
    u32 error_id;
private:
    std::string message;
};

u32 *getMatrix(int width, int height);

#endif
