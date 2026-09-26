
#pragma once
#include <daisy.h>

inline const char* ToString(daisy::SpiHandle::Result value)
{
    switch (value)
    {
        case daisy::SpiHandle::Result::OK: return "OK";
        case daisy::SpiHandle::Result::ERR: return "ERR";
    }
    return "UNKNOWN";
}