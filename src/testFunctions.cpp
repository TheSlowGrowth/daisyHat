#include "testFunctions.h"
#include "logOut.h"

namespace daisyhat
{
    extern int numFailedAssertions;
}

namespace daisyhat::internal
{
    bool Assert(bool result, const char* failureMessage)
    {
        if (!result)
        {
            daisyhat::numFailedAssertions++;
            PrintLine(failureMessage);
        }
        return result;
    }
} // namespace daisyhat::internal