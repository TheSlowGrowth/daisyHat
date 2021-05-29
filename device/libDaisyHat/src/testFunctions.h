#pragma once
#include <daisy.h>
#include "stringConversions.h"

namespace daisyhat
{
    namespace internal
    {
        bool Assert(bool result, const char* message);

        template <typename A, typename B>
        bool AssertWithStringOutput(const A& a,
                                    const B& b,
                                    bool result,
                                    const char* messageStart,
                                    const char* aVarName,
                                    const char* bVarName)
        {
            daisy::FixedCapStr<512> message(messageStart);
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
            return result;
        }
    } // namespace internal

#define EXPECT_EQ(a, b) internal::AssertWithStringOutput(a, b, a == b, "FAILURE: Expected " #a " == " #b, #a, #b)
#define EXPECT_GT(a, b) internal::AssertWithStringOutput(a, b, a > b, "FAILURE: Expected " #a " > " #b, #a, #b)
#define EXPECT_GE(a, b) internal::AssertWithStringOutput(a, b, a >= b, "FAILURE: Expected " #a " >= " #b, #a, #b)
#define EXPECT_LT(a, b) internal::AssertWithStringOutput(a, b, a < b, "FAILURE: Expected " #a " < " #b, #a, #b)
#define EXPECT_LE(a, b) internal::AssertWithStringOutput(a, b, a <= b, "FAILURE: Expected " #a " <= " #b, #a, #b)
#define EXPECT_TRUE(condition) internal::Assert(condition, "FAILURE: Expected " #condition " == true")
#define EXPECT_FALSE(condition) internal::Assert(!condition, "FAILURE: Expected " #condition " == false")
} // namespace daisyhat