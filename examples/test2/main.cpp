#include <daisy_seed.h>
#include <daisyHat.h>

daisy::DaisySeed seed;

int main()
{
    seed.Configure();
    seed.Init();

    daisyhat::StartTest(seed, "test2");
    int a = 1;
    int b = 2;
    EXPECT_EQ(a, b);
    daisyhat::FinishTest();
}