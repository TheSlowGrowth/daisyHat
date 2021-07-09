#pragma once
#include <daisy.h>

const char* ToString(bool value);
daisy::FixedCapStr<128> ToString(float value);
daisy::FixedCapStr<128> ToString(unsigned int value);
daisy::FixedCapStr<128> ToString(int value);
daisy::FixedCapStr<128> ToString(uint8_t value);
daisy::FixedCapStr<128> ToString(int8_t value);
daisy::FixedCapStr<128> ToString(uint16_t value);
daisy::FixedCapStr<128> ToString(int16_t value);
daisy::FixedCapStr<128> ToString(uint32_t value);
daisy::FixedCapStr<128> ToString(int32_t value);
daisy::FixedCapStr<128> ToString(uint64_t value);
daisy::FixedCapStr<128> ToString(int64_t value);
const char ToString(char value);
const char* ToString(const char* value);
