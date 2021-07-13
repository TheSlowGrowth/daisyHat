#pragma once
#include <daisy_seed.h>
#include "Signals.h"

namespace daisyhat
{
    enum class SerialPort
    {
        usbInternal,
        usbExternal,
        // add UART later
    };

    void Init(daisy::DaisySeed& seed,
              const char* testName,
              SerialPort port = SerialPort::usbInternal);

    void Print(const char* text);
    void PrintLine(const char* lineOfText);

    void FinishTest();

} // namespace daisyhat

#include "testFunctions.h"