#include "testFunctions.h"
#include "logOut.h"

extern int numFailedAssertions;

namespace daisyhat::internal
{
    bool Assert(bool result, const char* message)
    {
        if (!result)
            numFailedAssertions++;
        PrintLine(message);
        return result;
    }
} // namespace daisyhat::internal