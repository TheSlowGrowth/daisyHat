#pragma once
#include <daisy.h>
#include "stringConversions.h"

namespace daisyhat
{
    namespace internal
    {
        bool Assert(bool result, const char* failureMessage);

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
                daisy::FixedCapStr<512> message(failureMessageStart);
                message.Append("\nWhere\n     ");
                message.Append(aVarName);
                message.Append(" = '");
                message.Append(::ToString(a));
                message.Append("', \n     ");
                message.Append(bVarName);
                message.Append(" = '");
                message.Append(::ToString(b));
                message.Append("'");
                Assert(result, message);
            }

            return result;
        }
    } // namespace internal

#define EXPECT_EQ(a, b) daisyhat::internal::AssertWithStringOutput(a, b, a == b, "FAILURE: Expected " #a " == " #b, #a, #b)
#define EXPECT_GT(a, b) daisyhat::i::AssertWithStringOutput(a, b, a > b, "FAILURE: Expected " #a " > " #b, #a, #b)
#define EXPECT_GE(a, b) daisyhat::i::AssertWithStringOutput(a, b, a >= b, "FAILURE: Expected " #a " >= " #b, #a, #b)
#define EXPECT_LT(a, b) daisyhat::iinternal::AssertWithStringOutput(a, b, a < b, "FAILURE: Expected " #a " < " #b, #a, #b)
#define EXPECT_LE(a, b) daisyhat::iinternal::AssertWithStringOutput(a, b, a <= b, "FAILURE: Expected " #a " <= " #b, #a, #b)
#define EXPECT_TRUE(condition) daisyhat::iinternal::Assert(condition, "FAILURE: Expected " #condition " == true")
#define EXPECT_FALSE(condition) daisyhat::iinternal::Assert(!condition, "FAILURE: Expected " #condition " == false")
} // namespace daisyhat