#include <cstdio>
#include <daisy_seed.h>
#include "stringConversions.hpp"
#include <daisyHat.h>
#include "sequence.hpp"

using namespace daisy;
using namespace seed;

DaisySeed hw;

struct SpiConfig
{
    SpiHandle::Config::BaudPrescaler baud_prescaler;
    SpiHandle::Config::ClockPolarity clock_polarity;
    SpiHandle::Config::ClockPhase clock_phase;
    SpiHandle::Config::Direction direction;
};

// DMA transfer support: the buffers have to be in a memory section the DMA
// controller can access (DMA_BUFFER_MEM_SECTION, see daisy_core.h); completion
// is reported from an interrupt via the end callback
static uint8_t DMA_BUFFER_MEM_SECTION txBuffer[spi_transfer::kSequenceAliceToBob.size()];
static uint8_t DMA_BUFFER_MEM_SECTION rxBuffer[spi_transfer::kSequenceAliceToBob.size()];
static volatile bool dmaComplete = false;
static volatile SpiHandle::Result dmaResult;

static void DmaEndCallback(void* context, SpiHandle::Result result)
{
    // called from an interrupt, keep it fast
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

// DIAG: print a buffer as hex so we can see what actually came in over MISO
static void printReceived(const char* label, const uint8_t* data, size_t n)
{
    return;
    char line[256];
    int off = snprintf(line, sizeof(line), "DIAG received %s:", label);
    for (size_t i = 0; i < n; i++)
    {
        off += snprintf(line + off, sizeof(line) - (size_t) off, " %02x", data[i]);
    }
    daisyhat::PrintLine(line);
}

static SpiHandle::Config makeConf(const SpiConfig& cfg)
{
    SpiHandle::Config conf;
    conf.mode = SpiHandle::Config::Mode::MASTER;
    conf.periph = SpiHandle::Config::Peripheral::SPI_1;
    conf.pin_config.nss = D7;
    conf.pin_config.sclk = D8;
    conf.pin_config.miso = D9;
    conf.pin_config.mosi = D10;
    conf.direction = cfg.direction;
    conf.nss = SpiHandle::Config::NSS::HARD_OUTPUT;
    conf.baud_prescaler = cfg.baud_prescaler;
    conf.clock_polarity = cfg.clock_polarity;
    conf.clock_phase = cfg.clock_phase;
    return conf;
}

void sendBytesForConfig(const SpiConfig& cfg)
{
    SpiHandle spi;
    spi.Init(makeConf(cfg));
    // parity with the DMA version (sendBytesDmaForConfig / DmaTransmit): a
    // pure transmit runs the peripheral in single-line SIMPLEX_TX mode, which
    // pairs with the peer's BlockingReceive (SIMPLEX_RX). A full-duplex
    // BlockingTransmitAndReceive would drive MOSI while the peer samples the
    // single-line pin, so the two ends would disagree on which wire carries
    // the data.
    SpiHandle::Result result = spi.BlockingTransmit(const_cast<uint8_t*>(spi_transfer::kSequenceAliceToBob.data()), spi_transfer::kSequenceAliceToBob.size(), 1000);
    EXPECT_EQ(result, SpiHandle::Result::OK);
}

void receiveBytesForConfig(const SpiConfig& cfg)
{
    SpiHandle spi;
    spi.Init(makeConf(cfg));
    // the master just provides the clock, the slave drives the data
    uint8_t buffer[spi_transfer::kSequenceAliceToBob.size()] = {};
    SpiHandle::Result result = spi.BlockingReceive(buffer, spi_transfer::kSequenceAliceToBob.size(), 1000);
    EXPECT_EQ(result, SpiHandle::Result::OK);
    if (result == SpiHandle::Result::OK)
    {
        printReceived("receiveBytesForConfig", buffer, sizeof(buffer));
        for (size_t i = 0; i < spi_transfer::kSequenceAliceToBob.size(); i++)
        {
            EXPECT_EQ(buffer[i], spi_transfer::kSequenceBobToAlice[i]);
        }
    }
}

void sendAndReceiveBytesForConfig(const SpiConfig& cfg)
{
    SpiHandle spi;
    spi.Init(makeConf(cfg));
    uint8_t rxBuffer[spi_transfer::kSequenceAliceToBob.size()] = {};
    SpiHandle::Result result = spi.BlockingTransmitAndReceive(const_cast<uint8_t*>(spi_transfer::kSequenceAliceToBob.data()), rxBuffer, spi_transfer::kSequenceAliceToBob.size(), 1000);
    EXPECT_EQ(result, SpiHandle::Result::OK);
    if (result == SpiHandle::Result::OK)
    {
        printReceived("sendAndReceiveBytesForConfig", rxBuffer, sizeof(rxBuffer));
        for (size_t i = 0; i < spi_transfer::kSequenceAliceToBob.size(); i++)
        {
            EXPECT_EQ(rxBuffer[i], spi_transfer::kSequenceBobToAlice[i]);
        }
    }
}

void sendBytesDmaForConfig(const SpiConfig& cfg)
{
    SpiHandle spi;
    spi.Init(makeConf(cfg));
    memcpy(txBuffer, spi_transfer::kSequenceAliceToBob.data(), sizeof(txBuffer));
    dmaComplete = false;
    SpiHandle::Result result = spi.DmaTransmit(txBuffer, sizeof(txBuffer), NULL, DmaEndCallback, NULL);
    EXPECT_EQ(result, SpiHandle::Result::OK);
    waitDmaDoneOrTimeout();
    EXPECT_TRUE(dmaComplete);
    EXPECT_EQ(dmaResult, SpiHandle::Result::OK);
}

void receiveBytesDmaForConfig(const SpiConfig& cfg)
{
    SpiHandle spi;
    spi.Init(makeConf(cfg));
    memset(rxBuffer, 0, sizeof(rxBuffer));
    dmaComplete = false;
    SpiHandle::Result result = spi.DmaReceive(rxBuffer, sizeof(rxBuffer), NULL, DmaEndCallback, NULL);
    EXPECT_EQ(result, SpiHandle::Result::OK);
    waitDmaDoneOrTimeout();
    EXPECT_TRUE(dmaComplete);
    EXPECT_EQ(dmaResult, SpiHandle::Result::OK);
    if (dmaComplete && dmaResult == SpiHandle::Result::OK)
    {
        printReceived("receiveBytesDmaForConfig", rxBuffer, sizeof(rxBuffer));
        for (size_t i = 0; i < spi_transfer::kSequenceAliceToBob.size(); i++)
        {
            EXPECT_EQ(rxBuffer[i], spi_transfer::kSequenceBobToAlice[i]);
        }
    }
}

void sendAndReceiveBytesDmaForConfig(const SpiConfig& cfg)
{
    SpiHandle spi;
    spi.Init(makeConf(cfg));
    memcpy(txBuffer, spi_transfer::kSequenceAliceToBob.data(), sizeof(txBuffer));
    memset(rxBuffer, 0, sizeof(rxBuffer));
    dmaComplete = false;
    SpiHandle::Result result = spi.DmaTransmitAndReceive(txBuffer, rxBuffer, sizeof(txBuffer), NULL, DmaEndCallback, NULL);
    EXPECT_EQ(result, SpiHandle::Result::OK);
    waitDmaDoneOrTimeout();
    EXPECT_TRUE(dmaComplete);
    EXPECT_EQ(dmaResult, SpiHandle::Result::OK);
    if (dmaComplete && dmaResult == SpiHandle::Result::OK)
    {
        printReceived("sendAndReceiveBytesDmaForConfig", rxBuffer, sizeof(rxBuffer));
        for (size_t i = 0; i < spi_transfer::kSequenceAliceToBob.size(); i++)
        {
            EXPECT_EQ(rxBuffer[i], spi_transfer::kSequenceBobToAlice[i]);
        }
    }
}

int main()
{
    hw.Configure();
    hw.Init();
    daisyhat::Init(hw, "spi_transfer", "Alice");

    // block 0:
    // - full duplex
    // - low speed
    // - clock polarity low
    // - clock phase one edge
    {
        SpiConfig cfg {
            SpiHandle::Config::BaudPrescaler::PS_256,
            SpiHandle::Config::ClockPolarity::LOW,
            SpiHandle::Config::ClockPhase::ONE_EDGE,
            SpiHandle::Config::Direction::TWO_LINES
        };

        // blocking
        daisyhat::Checkpoint("alice-wait-00");
        sendBytesForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-01");
        receiveBytesForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-02");
        sendAndReceiveBytesForConfig(cfg);

        // DMA
        daisyhat::Checkpoint("alice-wait-03");
        sendBytesDmaForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-04");
        receiveBytesDmaForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-05");
        sendAndReceiveBytesDmaForConfig(cfg);
    }

    // block 1:
    // - full duplex
    // - medium speed
    // - clock polarity high
    // - clock phase two edge
    {
        SpiConfig cfg {
            SpiHandle::Config::BaudPrescaler::PS_16,
            SpiHandle::Config::ClockPolarity::HIGH,
            SpiHandle::Config::ClockPhase::TWO_EDGE,
            SpiHandle::Config::Direction::TWO_LINES
        };

        // blocking
        daisyhat::Checkpoint("alice-wait-10");
        sendBytesForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-11");
        receiveBytesForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-12");
        sendAndReceiveBytesForConfig(cfg);

        // DMA
        daisyhat::Checkpoint("alice-wait-13");
        sendBytesDmaForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-14");
        receiveBytesDmaForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-15");
        sendAndReceiveBytesDmaForConfig(cfg);
    }

    // block 2:
    // - simplex Alice-to-Bob
    // - medium speed
    // - clock polarity low
    // - clock phase one edge
    {
        SpiConfig cfg {
            SpiHandle::Config::BaudPrescaler::PS_16,
            SpiHandle::Config::ClockPolarity::HIGH,
            SpiHandle::Config::ClockPhase::TWO_EDGE,
            SpiHandle::Config::Direction::TWO_LINES_TX_ONLY
        };

        // blocking
        daisyhat::Checkpoint("alice-wait-20");
        sendBytesForConfig(cfg);

        // DMA
        daisyhat::Checkpoint("alice-wait-21");
        sendBytesDmaForConfig(cfg);
    }

    // block 3:
    // - simplex Bob-to-Alice
    // - medium speed
    // - clock polarity high
    // - clock phase two edge
    {
        SpiConfig cfg {
            SpiHandle::Config::BaudPrescaler::PS_16,
            SpiHandle::Config::ClockPolarity::HIGH,
            SpiHandle::Config::ClockPhase::TWO_EDGE,
            SpiHandle::Config::Direction::TWO_LINES_RX_ONLY
        };

        // blocking
        daisyhat::Checkpoint("alice-wait-30");
        receiveBytesForConfig(cfg);

        // DMA
        daisyhat::Checkpoint("alice-wait-31");
        receiveBytesDmaForConfig(cfg);
    }

    // block 4:
    // - half duplex
    // - medium speed
    // - clock polarity low
    // - clock phase two edge
    // TODO: This requires a connection
    //      Master:MOSI <> Slave:MISO
    // which currently doesn't exist.
    // Add later with a better fixture.
    /*
    {
        SpiConfig cfg {
            SpiHandle::Config::BaudPrescaler::PS_16,
            SpiHandle::Config::ClockPolarity::HIGH,
            SpiHandle::Config::ClockPhase::TWO_EDGE,
            SpiHandle::Config::Direction::ONE_LINE
        };

        // blocking
        daisyhat::Checkpoint("alice-wait-40");
        sendBytesForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-41");
        receiveBytesForConfig(cfg);

        // DMA
        daisyhat::Checkpoint("alice-wait-42");
        sendBytesDmaForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-43");
        receiveBytesDmaForConfig(cfg);
    }
    */

    daisyhat::FinishTest();
    return 0; // not reached (FinishTest traps)
}
