#include <daisy_seed.h>
#include "stringConversions.hpp"
#include <daisyHat.h>
#include "sequence.hpp"

using namespace daisy;
using namespace seed;

DaisySeed hw;

// Bob's own 7-bit slave address. It must be within the range accepted by
// I2CHandle::Impl::Init in slave mode (16..119); it must match
// kBobSlaveAddress in alice.cpp.
constexpr uint8_t kSlaveAddress = 0x10;

struct I2cConfig
{
    I2CHandle::Config::Speed speed;
};

static I2CHandle::Config makeConf(const I2cConfig& cfg)
{
    I2CHandle::Config conf;
    conf.mode = I2CHandle::Config::Mode::I2C_SLAVE;
    // I2C4 has no DMA support (yet), so all of Bob's transfers are blocking.
    conf.periph = I2CHandle::Config::Peripheral::I2C_4;
    conf.pin_config.scl = D13;
    conf.pin_config.sda = D14;
    conf.speed = cfg.speed;
    conf.address = kSlaveAddress;
    return conf;
}

// Bob (slave) waits for the master (Alice) to address him, then collects the
// kSequenceAliceToBob bytes into the buffer.
void receiveBytesForConfig(const I2cConfig& cfg)
{
    I2CHandle i2c;
    i2c.Init(makeConf(cfg));
    uint8_t buffer[i2c_transfer::kSequenceAliceToBob.size()] = {};
    I2CHandle::Result result = i2c.ReceiveBlocking(kSlaveAddress, buffer, sizeof(buffer), 10000);
    EXPECT_EQ(result, I2CHandle::Result::OK);
    if (result == I2CHandle::Result::OK)
    {
        for (size_t i = 0; i < i2c_transfer::kSequenceAliceToBob.size(); i++)
        {
            EXPECT_EQ(buffer[i], i2c_transfer::kSequenceAliceToBob[i]);
        }
    }
}

// Bob (slave) hands over kSequenceBobToAlice while the master reads.
void sendBytesForConfig(const I2cConfig& cfg)
{
    I2CHandle i2c;
    i2c.Init(makeConf(cfg));
    I2CHandle::Result result = i2c.TransmitBlocking(kSlaveAddress,
                                                    const_cast<uint8_t*>(i2c_transfer::kSequenceBobToAlice.data()),
                                                    i2c_transfer::kSequenceBobToAlice.size(),
                                                    10000);
    EXPECT_EQ(result, I2CHandle::Result::OK);
}

int main()
{
    hw.Configure();
    hw.Init();
    daisyhat::Init(hw, "i2c_transfer", "Bob");

    // block 0: standard mode (100 kHz)
    {
        I2cConfig cfg {
            I2CHandle::Config::Speed::I2C_100KHZ
        };

        daisyhat::Checkpoint("bob-wait-00");
        receiveBytesForConfig(cfg);

        daisyhat::Checkpoint("bob-wait-01");
        sendBytesForConfig(cfg);

        // I2C4 has no DMA on Bob's side; the "DMA" steps still exercise Bob's
        // blocking slave receive while Alice's I2C1 master side uses DMA.
        daisyhat::Checkpoint("bob-wait-02");
        receiveBytesForConfig(cfg);

        daisyhat::Checkpoint("bob-wait-03");
        sendBytesForConfig(cfg);
    }

    // block 1: fast mode (400 kHz)
    {
        I2cConfig cfg {
            I2CHandle::Config::Speed::I2C_400KHZ
        };

        daisyhat::Checkpoint("bob-wait-10");
        receiveBytesForConfig(cfg);

        daisyhat::Checkpoint("bob-wait-11");
        sendBytesForConfig(cfg);

        daisyhat::Checkpoint("bob-wait-12");
        receiveBytesForConfig(cfg);

        daisyhat::Checkpoint("bob-wait-13");
        sendBytesForConfig(cfg);
    }

    daisyhat::FinishTest();
    return 0; // not reached (FinishTest traps)
}
