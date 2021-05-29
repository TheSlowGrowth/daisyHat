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

daisy::FixedCapStr<128> ToString(int value)
{
    daisy::FixedCapStr<128> str;
    str.AppendInt(value);
    return str;
}

const char ToString(char value)
{
    return value; // FixedCapStr.Append() takes a char directly.
}

const char* ToString(const char* value)
{
    return value; // FixedCapStr.Append() takes a const char* directly.
}