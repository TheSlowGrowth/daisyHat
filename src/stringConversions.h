#pragma once
#include <daisy.h>

const char* ToString(bool value);
daisy::FixedCapStr<128> ToString(float value);
daisy::FixedCapStr<128> ToString(int value);
const char ToString(char value);
const char* ToString(const char* value);
