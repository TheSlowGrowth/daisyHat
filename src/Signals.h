#pragma once
#include "SerialComms.h"
#include <daisy.h>

namespace daisyhat::signals
{
    /** A zero terminated string, used as an identifier. */
    using Identifier = daisy::FixedCapStr<32>;

    /** Returns true if a host signal was received. */
    bool WasHostSignalReceived(const Identifier& signalToCheck);

    /** Blocks until a host signal was received. If WasHostSignalReceived() 
     *  returns true, this will return immediately. */
    void AwaitHostSignal(const Identifier& signalToAwait);

    /** Resets the state of a host signal so that WasHostSignalReceived() will now return false */
    void ResetHostSignal(const Identifier& signalToReset);

    /** Sends a signal to the host. */
    void SendSignal(const Identifier& signalToSend);

    namespace ids::host_signals
    {
        /** A signal sent from the host to start running the test. */
        static constexpr Identifier startTest = "start_test";
    }

    namespace internal 
    {
        /** INTERNAL. Called to initialize the signalling code. */
        void Init(SerialComms& serialCommsInstance);
    }
}