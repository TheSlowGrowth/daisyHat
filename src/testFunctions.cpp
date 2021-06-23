#include "testFunctions.h"
#include "logOut.h"

namespace daisyhat
{
    extern int numFailedAssertions;
}

namespace daisyhat::internal
{
    bool Assert(bool result, const char* failureMessage, const char* failureMessageDetails)
    {
        if (!result)
        {
            daisyhat::numFailedAssertions++;
            PrintLine(failureMessage);
            if (failureMessageDetails)
                PrintLine(failureMessageDetails);
        }
        return result;
    }
} // namespace daisyhat::internal