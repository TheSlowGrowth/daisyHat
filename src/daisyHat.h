#pragma once
#include <daisy_seed.h>
#include "logOut.h"
#include "testFunctions.h"

namespace daisyhat
{
    void StartTest(daisy::DaisySeed& seed, const char* testName);
    void FinishTest();
} // namespace daisyhat