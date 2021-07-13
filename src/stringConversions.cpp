#include "stringConversions.h"

const char* ToString(bool value)
{
    return value ? "true" : "false";
}

daisy::FixedCapStr<128> ToString(float value)
{
    daisy::FixedCapStr<128> str;
    str.AppendFloat(value, 9, true); // 10 digits, remove trailing zeros
    return str;
}

template <typename IntType>
daisy::FixedCapStr<128> ToStringImpl(IntType value)
{
    daisy::FixedCapStr<128> str;
    str.AppendInt(value);
    return str;
}

daisy::FixedCapStr<128> ToString(unsigned int value) { return ToStringImpl(value); }
daisy::FixedCapStr<128> ToString(int value) { return ToStringImpl(value); }
daisy::FixedCapStr<128> ToString(uint8_t value) { return ToStringImpl(value); }
daisy::FixedCapStr<128> ToString(int8_t value) { return ToStringImpl(value); }
daisy::FixedCapStr<128> ToString(uint16_t value) { return ToStringImpl(value); }
daisy::FixedCapStr<128> ToString(int16_t value) { return ToStringImpl(value); }
daisy::FixedCapStr<128> ToString(uint32_t value) { return ToStringImpl(value); }
daisy::FixedCapStr<128> ToString(int32_t value) { return ToStringImpl(value); }
daisy::FixedCapStr<128> ToString(uint64_t value) { return ToStringImpl(value); }
daisy::FixedCapStr<128> ToString(int64_t value) { return ToStringImpl(value); }

const char ToString(char value)
{
    return value; // FixedCapStr.Append() takes a char directly.
}

const char* ToString(const char* value)
{
    return value; // FixedCapStr.Append() takes a const char* directly.
}