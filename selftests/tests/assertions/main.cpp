#include <daisy_seed.h>
#include <daisyHat.h>

daisy::DaisySeed seed;

int main()
{
    seed.Configure();
    seed.Init();

    daisyhat::Init(seed, "assertions");

    int a = 1;
    int b = 1;
    int c = 2;
    float f1 = 1.0f;
    float f2 = 1.5f;
    float delta = 0.1f;
    const char* sa = "a";
    const char* sb = "b";

    // Every assertion macro is used once with a passing and once with a
    // failing value. The failing cases are intentional: the self-test is
    // verified on the host side, which expects exactly the corresponding
    // failure prints and failure count.
    EXPECT_EQ(a, b);
    EXPECT_EQ(a, c);
    EXPECT_GT(c, a);
    EXPECT_GT(a, c);
    EXPECT_GE(a, b);
    EXPECT_GE(a, c);
    EXPECT_LT(a, c);
    EXPECT_LT(c, a);
    EXPECT_LE(a, b);
    EXPECT_LE(c, a);
    EXPECT_NEAR(f1, f2, 0.6f);
    EXPECT_NEAR(f1, f2, delta);
    EXPECT_STREQ(sa, sa);
    EXPECT_STREQ(sa, sb);
    EXPECT_TRUE(a == b);
    EXPECT_TRUE(a == c);
    EXPECT_FALSE(a == c);
    EXPECT_FALSE(a == b);

    daisyhat::FinishTest();
    return 0; // not reached (FinishTest traps)
}
