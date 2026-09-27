#pragma once
#include <daisy.h>

inline const char* ToString(daisy::UartHandler::Result value)
{
    switch (value)
    {
        case daisy::UartHandler::Result::OK: return "OK";
        case daisy::UartHandler::Result::ERR: return "ERR";
    }
    return "UNKNOWN";
}
