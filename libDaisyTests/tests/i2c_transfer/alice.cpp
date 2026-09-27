#include <daisy_seed.h>
#include "stringConversions.hpp"
#include <daisyHat.h>
#include "sequence.hpp"

using namespace daisy;
using namespace seed;

DaisySeed hw;

// Bob's 7-bit slave address. It must be within the range accepted by
// I2CHandle::Impl::Init in slave mode (16..119); it must match
// kSlaveAddress in bob.cpp.
constexpr uint16_t kBobSlaveAddress = 0x10;

struct I2cConfig
{
    I2CHandle::Config::Speed speed;
};

// I2CHandle initialises the SCL/SDA pins as open-drain with *no* pull
// (I2CHandle::Impl::InitPins hardcodes GPIO_NOPULL). This fixture has no
// external pull-up resistors, so after every Init we re-configure both
// pins with the internal pull-ups enabled (same open-drain AF mode).
static void EnableInternalPullUps(const I2CHandle::Config& conf)
{
    GPIO_InitTypeDef gpio;
    gpio.Mode  = GPIO_MODE_AF_OD;
    gpio.Pull  = GPIO_PULLUP;
    gpio.Speed = GPIO_SPEED_FREQ_LOW;
    for (size_t i = 0; i < 2; i++)
    {
        Pin pin = (i == 0) ? conf.pin_config.scl : conf.pin_config.sda;
        GPIO_TypeDef* port = GetHALPort(pin);
        gpio.Pin = GetHALPin(pin);
        if (conf.periph == I2CHandle::Config::Peripheral::I2C_1)
            gpio.Alternate = GPIO_AF4_I2C1;
        else if (conf.periph == I2CHandle::Config::Peripheral::I2C_2)
            gpio.Alternate = GPIO_AF4_I2C2;
        else if (conf.periph == I2CHandle::Config::Peripheral::I2C_3)
            gpio.Alternate = GPIO_AF4_I2C3;
        else if (conf.periph == I2CHandle::Config::Peripheral::I2C_4)
            gpio.Alternate = GPIO_AF6_I2C4;
        HAL_GPIO_Init(port, &gpio);
    }
}

static I2CHandle::Config makeConf(const I2cConfig& cfg)
{
    I2CHandle::Config conf;
    conf.mode = I2CHandle::Config::Mode::I2C_MASTER;
    conf.periph = I2CHandle::Config::Peripheral::I2C_1;
    conf.pin_config.scl = D11;
    conf.pin_config.sda = D12;
    conf.speed = cfg.speed;
    conf.address = kBobSlaveAddress;
    return conf;
}

// DMA transfer support: the buffers have to be in a memory section the DMA
// controller can access (DMA_BUFFER_MEM_SECTION, see daisy_core.h); completion
// is reported from an interrupt via the end callback.
static uint8_t DMA_BUFFER_MEM_SECTION txBuffer[i2c_transfer::kSequenceAliceToBob.size()];
static uint8_t DMA_BUFFER_MEM_SECTION rxBuffer[i2c_transfer::kSequenceBobToAlice.size()];
static volatile bool dmaComplete = false;
static volatile I2CHandle::Result dmaResult;

static void DmaEndCallback(void* context, I2CHandle::Result result)
{
    // called from an interrupt, keep it fast
    (void) context;
    dmaResult = result;
    dmaComplete = true;
}

static void waitDmaDoneOrTimeout()
{
    uint32_t deadline = System::GetNow() + 5000;
    while (!dmaComplete && System::GetNow() < deadline)
    {
        System::Delay(1);
    }
}

// Alice (master) pushes kSequenceAliceToBob to Bob.
void sendBytesForConfig(const I2cConfig& cfg)
{
    I2CHandle i2c;
    i2c.Init(makeConf(cfg));
    EnableInternalPullUps(i2c.GetConfig());
    I2CHandle::Result result = i2c.TransmitBlocking(kBobSlaveAddress,
                                                    const_cast<uint8_t*>(i2c_transfer::kSequenceAliceToBob.data()),
                                                    i2c_transfer::kSequenceAliceToBob.size(),
                                                    1000);
    EXPECT_EQ(result, I2CHandle::Result::OK);
}

// Alice (master) pulls kSequenceBobToAlice out of Bob.
void receiveBytesForConfig(const I2cConfig& cfg)
{
    I2CHandle i2c;
    i2c.Init(makeConf(cfg));
    EnableInternalPullUps(i2c.GetConfig());
    uint8_t buffer[i2c_transfer::kSequenceBobToAlice.size()] = {};
    I2CHandle::Result result = i2c.ReceiveBlocking(kBobSlaveAddress, buffer, sizeof(buffer), 1000);
    EXPECT_EQ(result, I2CHandle::Result::OK);
    if (result == I2CHandle::Result::OK)
    {
        for (size_t i = 0; i < i2c_transfer::kSequenceBobToAlice.size(); i++)
        {
            EXPECT_EQ(buffer[i], i2c_transfer::kSequenceBobToAlice[i]);
        }
    }
}

void sendBytesDmaForConfig(const I2cConfig& cfg)
{
    I2CHandle i2c;
    i2c.Init(makeConf(cfg));
    EnableInternalPullUps(i2c.GetConfig());
    memcpy(txBuffer, i2c_transfer::kSequenceAliceToBob.data(), sizeof(txBuffer));
    dmaComplete = false;
    I2CHandle::Result result = i2c.TransmitDma(kBobSlaveAddress, txBuffer, sizeof(txBuffer), DmaEndCallback, NULL);
    EXPECT_EQ(result, I2CHandle::Result::OK);
    waitDmaDoneOrTimeout();
    EXPECT_TRUE(dmaComplete);
    EXPECT_EQ(dmaResult, I2CHandle::Result::OK);
}

void receiveBytesDmaForConfig(const I2cConfig& cfg)
{
    I2CHandle i2c;
    i2c.Init(makeConf(cfg));
    EnableInternalPullUps(i2c.GetConfig());
    memset(rxBuffer, 0, sizeof(rxBuffer));
    dmaComplete = false;
    I2CHandle::Result result = i2c.ReceiveDma(kBobSlaveAddress, rxBuffer, sizeof(rxBuffer), DmaEndCallback, NULL);
    EXPECT_EQ(result, I2CHandle::Result::OK);
    waitDmaDoneOrTimeout();
    EXPECT_TRUE(dmaComplete);
    EXPECT_EQ(dmaResult, I2CHandle::Result::OK);
    if (dmaComplete && dmaResult == I2CHandle::Result::OK)
    {
        for (size_t i = 0; i < i2c_transfer::kSequenceBobToAlice.size(); i++)
        {
            EXPECT_EQ(rxBuffer[i], i2c_transfer::kSequenceBobToAlice[i]);
        }
    }
}

int main()
{
    hw.Configure();
    hw.Init();
    daisyhat::Init(hw, "i2c_transfer", "Alice");

    // block 0: standard mode (100 kHz)
    {
        I2cConfig cfg {
            I2CHandle::Config::Speed::I2C_100KHZ
        };

        daisyhat::Checkpoint("alice-wait-00");
        sendBytesForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-01");
        receiveBytesForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-02");
        sendBytesDmaForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-03");
        receiveBytesDmaForConfig(cfg);
    }

    // block 1: fast mode (400 kHz)
    {
        I2cConfig cfg {
            I2CHandle::Config::Speed::I2C_400KHZ
        };

        daisyhat::Checkpoint("alice-wait-10");
        sendBytesForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-11");
        receiveBytesForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-12");
        sendBytesDmaForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-13");
        receiveBytesDmaForConfig(cfg);
    }

    daisyhat::FinishTest();
    return 0; // not reached (FinishTest traps)
}
