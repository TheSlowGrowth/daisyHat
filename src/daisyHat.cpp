#include <memory>
#include "daisyHat.h"
#include <daisy_seed.h>
#include "SerialComms.h"
#include "Signals.h"

namespace daisyhat
{
    int numFailedAssertions = 0;
    uint32_t startTime = 0;
    daisy::DaisySeed* seed;

    // storage for a SerialComms object. Right now we only support UsbSerialComms,
    // but we can add more here, e.g. UartSerialComms
    std::aligned_union<0, UsbSerialComms /* add more types here ...*/>::type serialCommsStorage;
    SerialComms* serialComms = nullptr;

    void Init(daisy::DaisySeed& _seed, const char* testName, SerialPort serialPort)
    {
        startTime = daisy::System::GetNow();
        numFailedAssertions = 0;

        seed = &_seed;
        seed->SetLed(true);

        // create SerialComms object according to the specified port
        switch (serialPort)
        {
            case SerialPort::usbExternal:
                serialComms = new (std::addressof(serialCommsStorage)) UsbSerialComms(daisy::UsbHandle::FS_EXTERNAL);
                break;

            default:
            case SerialPort::usbInternal:
                serialComms = new (std::addressof(serialCommsStorage)) UsbSerialComms(daisy::UsbHandle::FS_INTERNAL);
                break;

                // we could also add UART communication if we need it.
        }

        // Init signals
        signals::internal::Init(*serialComms);
        // await test start
        signals::AwaitHostSignal(signals::ids::host_signals::startTest);

        PrintLine("=== Starting Test ===");
        Print("> Name: ");
        PrintLine(testName);
        PrintLine("===");
    }

    void Print(const char* text)
    {
        serialComms->Transmit(text);
    }

    void PrintLine(const char* lineOfText)
    {
        serialComms->Transmit(lineOfText);
        serialComms->Transmit("\n");
    }

    void FinishTest()
    {
        const auto endTime = daisy::System::GetNow();
        const int testDuration = endTime - startTime;

        PrintLine("=== Test Finished ===");
        Print("> numFailedAssertions = ");
        PrintLine(ToString(numFailedAssertions));
        Print("> duration = ");
        Print(ToString(testDuration));
        PrintLine(" ms");
        if (numFailedAssertions > 0)
            PrintLine("> testResult = FAILURE");
        else
            PrintLine("> testResult = SUCCESS");
        PrintLine("===");

        seed->SetLed(false);

        // trap processor in endless loop.
        while (1)
        {
        };
    }
} // namespace daisyhat