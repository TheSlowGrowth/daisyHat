#include "Signals.h"
#include <cstring>

namespace daisyhat::signals
{
    static constexpr size_t kMaxNumSignals = 16;
    daisy::Stack<Identifier, kMaxNumSignals> signalRegistry;
    SerialComms* serialCommsInstance = nullptr;
    static const char* signalCommandStr = "!!>> Signal:";

    bool WasHostSignalReceived(const Identifier& signalToCheck)
    {
        // compiler barrier so the polling loop cannot hoist this read
        // out (the registry is written from the serial RX ISR)
        __asm__ __volatile__("" : : : "memory");
        return signalRegistry.Contains(signalToCheck);
    }

    void AwaitHostSignal(const Identifier& signalToAwait)
    {
        if (!WasHostSignalReceived(signalToAwait) && signalRegistry.IsFull())
        {
            serialCommsInstance->Transmit("ERROR: Signal registry full;"
                                          " getting stuck waiting for signal\n");
        }

        while (!WasHostSignalReceived(signalToAwait))
        {
        }
    }

    void AwaitHostSignalAndClear(const Identifier& signalToAwait)
    {
        if (!WasHostSignalReceived(signalToAwait) && signalRegistry.IsFull())
        {
            serialCommsInstance->Transmit("ERROR: Signal registry full;"
                                          " getting stuck waiting for signal\n");
        }

        while (!WasHostSignalReceived(signalToAwait))
        {
        }
        ResetHostSignal(signalToAwait);
    }

    void ResetHostSignal(const Identifier& signalToReset)
    {
        signalRegistry.RemoveAllEqualTo(signalToReset);
    }

    void SendSignal(const Identifier& signalToSend)
    {
        serialCommsInstance->Transmit(signalCommandStr);
        serialCommsInstance->Transmit(signalToSend);
        serialCommsInstance->Transmit("\n");
    }

    // ==============================================================

    // ==============================================================

    class SignalListener : public SerialComms::LineListener
    {
    public:
        void OnLineReceived(const char* line) override
        {
            // check if this line is a "signal" command
            const bool startsWithSignalCommand = strncmp(signalCommandStr, line, strlen(signalCommandStr)) == 0;
            if (!startsWithSignalCommand)
                return;

            // extract the signal id
            const auto lineWithoutCommand = line + strlen(signalCommandStr);
            Identifier id(lineWithoutCommand);
            if (id.EndsWith("\n"))
                id.RemoveSuffix(1);

            // add it to the registry
            if (!signalRegistry.Contains(id))
                signalRegistry.PushBack(id);
        }
    };
    SignalListener signalListener;

    // ==============================================================

    // ==============================================================

    void internal::Init(SerialComms& _serialCommsInstance)
    {
        signalRegistry.Clear();
        serialCommsInstance = &_serialCommsInstance;
        serialCommsInstance->AddListener(&signalListener);
    }
} // namespace daisyhat::signals