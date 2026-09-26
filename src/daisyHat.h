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

    /**
     * @brief Initializes the daisyHat test library.
     * @param seed the DaisySeed object
     * @param testName name of the test (printed in the test report)
     * @param deviceName name of this device; announced to the host via the
     *        start handshake (must match the seed identifier in the daisyHat
     *        config file, cf. DaisySeed.start_test_execution on the host)
     * @param port serial port used for the test communication
     */
    void Init(daisy::DaisySeed& seed,
              const char* testName,
              const char* deviceName,
              SerialPort port = SerialPort::usbInternal);

    void Print(const char* text);
    void PrintLine(const char* lineOfText);

    // Checkpoint for host-side synchronization of multi-device tests:
    // reports the checkpoint to the host and blocks until the host releases
    // this checkpoint (cf. DaisySeed.halt_at_checkpoint / .release on the host).
    void Checkpoint(const char* checkpointName);

    void FinishTest();

} // namespace daisyhat

#include "testFunctions.h"