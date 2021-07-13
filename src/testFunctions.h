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
        bool AssertTwoVarWithStringOutput(const A& a,
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
                Assert(result, failureMessageStart, detailMsg);
            }

            return result;
        }

        template <typename A, typename B, typename C>
        bool AssertThreeVarWithStringOutput(const A& a,
                                            const B& b,
                                            const C& c,
                                            bool result,
                                            const char* failureMessageStart,
                                            const char* aVarName,
                                            const char* bVarName,
                                            const char* cVarName)
        {
            if (!result)
            {
                daisy::FixedCapStr<128> detailMsg("Where\n");
                detailMsg.Append("     ");
                detailMsg.Append(aVarName);
                detailMsg.Append(" = '");
                detailMsg.Append(::ToString(a));
                detailMsg.Append("',\n     ");
                detailMsg.Append(bVarName);
                detailMsg.Append(" = '");
                detailMsg.Append(::ToString(b));
                detailMsg.Append("',\n     ");
                detailMsg.Append(cVarName);
                detailMsg.Append(" = '");
                detailMsg.Append(::ToString(c));
                detailMsg.Append("'");
                Assert(result, failureMessageStart, detailMsg);
            }

            return result;
        }
    } // namespace internal

#define STRINGIFY(x) #x
#define TOSTRING(x) STRINGIFY(x)

#define EXPECT_STREQ(a, b) \
    { \
        const auto a_ = a; \
        const auto b_ = b; \
        daisyhat::internal::AssertTwoVarWithStringOutput(a_, b_, strcmp(a_, b_) == 0, "FAILURE: Expected " #a " == " #b " at " __FILE__ ":" TOSTRING(__LINE__), #a, #b); \
    }
#define EXPECT_EQ(a, b) \
    { \
        const auto a_ = a; \
        const auto b_ = b; \
        daisyhat::internal::AssertTwoVarWithStringOutput(a_, b_, a_ == b_, "FAILURE: Expected " #a " == " #b " at " __FILE__ ":" TOSTRING(__LINE__), #a, #b); \
    }
#define EXPECT_GT(a, b) \
    { \
        const auto a_ = a; \
        const auto b_ = b; \
        daisyhat::internal::AssertTwoVarWithStringOutput(a_, b_, a_ > b_, "FAILURE: Expected " #a " > " #b " at " __FILE__ ":" TOSTRING(__LINE__), #a, #b); \
    }
#define EXPECT_GE(a, b) \
    { \
        const auto a_ = a; \
        const auto b_ = b; \
        daisyhat::internal::AssertTwoVarWithStringOutput(a_, b_, a_ >= b_, "FAILURE: Expected " #a " >= " #b " at " __FILE__ ":" TOSTRING(__LINE__), #a, #b); \
    }
#define EXPECT_LT(a, b) \
    { \
        const auto a_ = a; \
        const auto b_ = b; \
        daisyhat::internal::AssertTwoVarWithStringOutput(a_, b_, a_ < b_, "FAILURE: Expected " #a " < " #b " at " __FILE__ ":" TOSTRING(__LINE__), #a, #b); \
    }
#define EXPECT_LE(a, b) \
    { \
        const auto a_ = a; \
        const auto b_ = b; \
        daisyhat::internal::AssertTwoVarWithStringOutput(a_, b_, a_ <= b_, "FAILURE: Expected " #a " <= " #b " at " __FILE__ ":" TOSTRING(__LINE__), #a, #b); \
    }
#define EXPECT_NEAR(a, b, maxDelta) \
    { \
        const auto a_ = a; \
        const auto b_ = b; \
        const auto diff_ = (a_ - b_); \
        const auto maxDelta_ = maxDelta; \
        daisyhat::internal::AssertThreeVarWithStringOutput(a_, b_, maxDelta_, (diff_ > 0 ? diff_ : -diff_) <= maxDelta_, "FAILURE: Expected abs(" #a " - " #b ") <= " #maxDelta " at " __FILE__ ":" TOSTRING(__LINE__), #a, #b, #maxDelta); \
    }
#define EXPECT_TRUE(condition) daisyhat::internal::Assert(condition, "FAILURE: Expected " #condition " == true at " __FILE__ ":" TOSTRING(__LINE__))
#define EXPECT_FALSE(condition) daisyhat::internal::Assert(!condition, "FAILURE: Expected " #condition " == false at " __FILE__ ":" TOSTRING(__LINE__))
} // namespace daisyhat