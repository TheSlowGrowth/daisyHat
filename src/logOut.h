#pragma once
#include <daisy.h>

namespace daisyhat
{
    /** Local shorthand for debug log destination
    */
    using Log = daisy::Logger<daisy::LOGGER_INTERNAL>;

    /** Print formatted debug log message
     */
    template <typename... VA>
    void Print(const char* format, VA... va)
    {
        Log::Print(format, va...);
    }

    /** Print formatted debug log message with automatic line termination
    */
    template <typename... VA>
    void PrintLine(const char* format, VA... va)
    {
        Log::PrintLine(format, va...);
    }

    /** Start the logging session. Optionally wait for terminal connection before proceeding.
    */
    inline void StartLog(bool wait_for_pc = false)
    {
        Log::StartLog(wait_for_pc);
    }

} // namespace daisyhat
