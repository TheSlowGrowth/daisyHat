#pragma once
#include <daisy.h>
#include <string.h>
#include "stringConversions.h"

namespace daisyhat
{
    namespace internal
    {
        bool Assert(bool result, const char* failureMessage, const char* failureMessageDetails = nullptr);

        template <typename A, typename B>
        bool AssertWithStringOutput(const A& a,
                                    const B& b,
                                    bool result,
                                    const char* failureMessageStart,
                                    const char* aVarName,
                                    const char* bVarName)
        {
            if (!result)
            {
                daisy::FixedCapStr<128> detailMsg("Where\n");
                detailMsg.Append("     ");
                detailMsg.Append(aVarName);
                detailMsg.Append(" = '");
                detailMsg.Append(::ToString(a));
                detailMsg.Append("', \n     ");
                detailMsg.Append(bVarName);
                detailMsg.Append(" = '");
                detailMsg.Append(::ToString(b));
                detailMsg.Append("'");
                // print output as individual snippets to work around the 128 character TX buffer
                Assert(result, failureMessageStart, detailMsg);
            }

            return result;
        }
    } // namespace internal

#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)

#define EXPECT_STREQ(a, b) daisyhat::internal::AssertWithStringOutput(a, b, strcmp(a, b) == 0, "FAILURE: Expected " #a " == " #b " at " __FILE__ ":" TOSTRING(__LINE__), #a, #b)
#define EXPECT_EQ(a, b) daisyhat::internal::AssertWithStringOutput(a, b, a == b, "FAILURE: Expected " #a " == " #b " at " __FILE__ ":" TOSTRING(__LINE__), #a, #b)
#define EXPECT_GT(a, b) daisyhat::i::AssertWithStringOutput(a, b, a > b, "FAILURE: Expected " #a " > " #b " at " __FILE__ ":" TOSTRING(__LINE__), #a, #b)
#define EXPECT_GE(a, b) daisyhat::i::AssertWithStringOutput(a, b, a >= b, "FAILURE: Expected " #a " >= " #b " at " __FILE__ ":" TOSTRING(__LINE__), #a, #b)
#define EXPECT_LT(a, b) daisyhat::iinternal::AssertWithStringOutput(a, b, a < b, "FAILURE: Expected " #a " < " #b " at " __FILE__ ":" TOSTRING(__LINE__), #a, #b)
#define EXPECT_LE(a, b) daisyhat::iinternal::AssertWithStringOutput(a, b, a <= b, "FAILURE: Expected " #a " <= " #b " at " __FILE__ ":" TOSTRING(__LINE__), #a, #b)
#define EXPECT_TRUE(condition) daisyhat::iinternal::Assert(condition, "FAILURE: Expected " #condition " == true at " __FILE__ ":" TOSTRING(__LINE__))
#define EXPECT_FALSE(condition) daisyhat::iinternal::Assert(!condition, "FAILURE: Expected " #condition " == false at " __FILE__ ":" TOSTRING(__LINE__))
} // namespace daisyhat