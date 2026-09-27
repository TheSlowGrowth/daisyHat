#pragma once
#include <daisy.h>

inline const char* ToString(daisy::I2CHandle::Result value)
{
    switch (value)
    {
        case daisy::I2CHandle::Result::OK: return "OK";
        case daisy::I2CHandle::Result::ERR: return "ERR";
    }
    return "UNKNOWN";
}
