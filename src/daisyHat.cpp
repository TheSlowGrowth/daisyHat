#include "daisyHat.h"
#include <daisy_seed.h>

namespace daisyhat
{
    int numFailedAssertions = 0;
    uint32_t startTime = 0;
    daisy::DaisySeed* seed;

    void StartTest(daisy::DaisySeed& _seed, const char* testName)
    {
        startTime = daisy::System::GetNow();
        numFailedAssertions = 0;

        seed = &_seed;
        seed->SetLed(true);
        StartLog(true);
        daisy::System::Delay(3000);

        PrintLine("=== Starting Test ===");
        Print("> Name: ");
        PrintLine(testName);
        PrintLine("===");
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

        seed->SetLed(false);

        // trap processor in endless loop.
        while (1)
        {
        };
    }
} // namespace daisyhat