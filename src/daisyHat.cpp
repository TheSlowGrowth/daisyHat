#include "daisyHat.h"

namespace daisyhat
{
    int numFailedAssertions = 0;
    uint32_t startTime = 0;

    void StartTest(const char* testName)
    {
        StartLog(true);
        PrintLine("=== Starting Test ===");
        Print("> Name: ");
        PrintLine(testName);
        PrintLine("===");

        startTime = daisy::System::GetNow();
        numFailedAssertions = 0;
    }

    void FinishTest()
    {
        const auto endTime = daisy::System::GetNow();
        const auto testDuration = endTime - startTime;

        PrintLine("=== Test Finished ===");
        PrintLine("> numFailedAssertions = %d", numFailedAssertions);
        PrintLine("> duration = %d ms", testDuration);
        if (numFailedAssertions > 0)
            PrintLine("> testResult = FAILURE");
        else
            PrintLine("> testResult = SUCCESS");
        PrintLine("===");

        // trap processor in endless loop.
        while(1) {};
    }
} // namespace daisyhat