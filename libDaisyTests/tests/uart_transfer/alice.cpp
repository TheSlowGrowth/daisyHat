#include <daisy_seed.h>
#include "stringConversions.hpp"
#include <daisyHat.h>
#include "sequence.hpp"

using namespace daisy;
using namespace seed;

DaisySeed hw;

// UART is point-to-point and has no flow control: once the sender starts
// clocking bits, the receiver must already have its peripheral armed
// (Init'd, RX enabled) or the bytes are lost. The host therefore always
// releases the receiver before the sender (see daisyHatTest.py).
struct UartConfig
{
    uint32_t baudrate;
};

static UartHandler::Config makeConf(const UartConfig& cfg)
{
    UartHandler::Config conf;
    // UART4 lives on the same two wires the I2C test uses (D11/D12):
    //   UART4 TX = D12 (PB9, AF8)  -> Bob's UART1 RX
    //   UART4 RX = D11 (PB8, AF8)  <- Bob's UART1 TX
    conf.periph = UartHandler::Config::Peripheral::UART_4;
    conf.pin_config.tx = D12;
    conf.pin_config.rx = D11;
    // full duplex so both pins are always configured, regardless of the
    // direction this step runs in.
    conf.mode = UartHandler::Config::Mode::TX_RX;
    conf.baudrate = cfg.baudrate;
    return conf;
}

// DMA transfer support: the buffers have to be in a memory section the DMA
// controller can access (DMA_BUFFER_MEM_SECTION, see daisy_core.h); completion
// is reported from an interrupt via the end callback.
static uint8_t DMA_BUFFER_MEM_SECTION txBuffer[uart_transfer::kSequenceAliceToBob.size()];
static uint8_t DMA_BUFFER_MEM_SECTION rxBuffer[uart_transfer::kSequenceBobToAlice.size()];
static volatile bool dmaComplete = false;
static volatile UartHandler::Result dmaResult;

static void DmaEndCallback(void* context, UartHandler::Result result)
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

// Alice pushes kSequenceAliceToBob to Bob (blocking).
void sendBytesForConfig(const UartConfig& cfg)
{
    UartHandler uart;
    uart.Init(makeConf(cfg));
    UartHandler::Result result = uart.BlockingTransmit(
        const_cast<uint8_t*>(uart_transfer::kSequenceAliceToBob.data()),
        uart_transfer::kSequenceAliceToBob.size(),
        10000);
    EXPECT_EQ(result, UartHandler::Result::OK);
}

// Alice pulls kSequenceBobToAlice out of Bob (blocking).
void receiveBytesForConfig(const UartConfig& cfg)
{
    UartHandler uart;
    uart.Init(makeConf(cfg));
    uint8_t buffer[uart_transfer::kSequenceBobToAlice.size()] = {};
    UartHandler::Result result = uart.BlockingReceive(buffer, sizeof(buffer), 10000);
    EXPECT_EQ(result, UartHandler::Result::OK);
    if (result == UartHandler::Result::OK)
    {
        for (size_t i = 0; i < uart_transfer::kSequenceBobToAlice.size(); i++)
        {
            EXPECT_EQ(buffer[i], uart_transfer::kSequenceBobToAlice[i]);
        }
    }
}

void sendBytesDmaForConfig(const UartConfig& cfg)
{
    UartHandler uart;
    uart.Init(makeConf(cfg));
    memcpy(txBuffer, uart_transfer::kSequenceAliceToBob.data(), sizeof(txBuffer));
    dmaComplete = false;
    UartHandler::Result result = uart.DmaTransmit(txBuffer, sizeof(txBuffer), NULL, DmaEndCallback, NULL);
    EXPECT_EQ(result, UartHandler::Result::OK);
    waitDmaDoneOrTimeout();
    EXPECT_TRUE(dmaComplete);
    EXPECT_EQ(dmaResult, UartHandler::Result::OK);
}

void receiveBytesDmaForConfig(const UartConfig& cfg)
{
    UartHandler uart;
    uart.Init(makeConf(cfg));
    memset(rxBuffer, 0, sizeof(rxBuffer));
    dmaComplete = false;
    UartHandler::Result result = uart.DmaReceive(rxBuffer, sizeof(rxBuffer), NULL, DmaEndCallback, NULL);
    EXPECT_EQ(result, UartHandler::Result::OK);
    waitDmaDoneOrTimeout();
    EXPECT_TRUE(dmaComplete);
    EXPECT_EQ(dmaResult, UartHandler::Result::OK);
    if (dmaComplete && dmaResult == UartHandler::Result::OK)
    {
        for (size_t i = 0; i < uart_transfer::kSequenceBobToAlice.size(); i++)
        {
            EXPECT_EQ(rxBuffer[i], uart_transfer::kSequenceBobToAlice[i]);
        }
    }
}

int main()
{
    hw.Configure();
    hw.Init();
    daisyhat::Init(hw, "uart_transfer", "Alice");

    // Pre-configure the UART so its TX line idles high. Without this, on the
    // very first step the TX pin is still in DaisySeed's default (floating)
    // state, so Bob captures spurious bytes from the floating line and the
    // received stream comes out shifted. The baud rate here is irrelevant
    // - we only care about getting the pins into UART mode.
    {
        UartHandler warmup;
        warmup.Init(makeConf(UartConfig { 115200 }));
    }

    // block 0: 115200 baud
    {
        UartConfig cfg {
            115200
        };

        daisyhat::Checkpoint("alice-wait-00");
        sendBytesForConfig(cfg); // Alice send (blocking)  / Bob receive (blocking)

        daisyhat::Checkpoint("alice-wait-01");
        receiveBytesForConfig(cfg); // Bob send (blocking)    / Alice receive (blocking)

        daisyhat::Checkpoint("alice-wait-02");
        sendBytesDmaForConfig(cfg); // Alice send (DMA)       / Bob receive (blocking)

        daisyhat::Checkpoint("alice-wait-03");
        receiveBytesForConfig(cfg); // Bob send (DMA)         / Alice receive (blocking)

        daisyhat::Checkpoint("alice-wait-04");
        sendBytesForConfig(cfg); // Alice send (blocking)  / Bob receive (DMA)

        daisyhat::Checkpoint("alice-wait-05");
        receiveBytesDmaForConfig(cfg); // Bob send (blocking)   / Alice receive (DMA)
    }

    // block 1: 921600 baud
    {
        UartConfig cfg {
            921600
        };

        daisyhat::Checkpoint("alice-wait-10");
        sendBytesForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-11");
        receiveBytesForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-12");
        sendBytesDmaForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-13");
        receiveBytesForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-14");
        sendBytesForConfig(cfg);

        daisyhat::Checkpoint("alice-wait-15");
        receiveBytesDmaForConfig(cfg);
    }

    daisyhat::FinishTest();
    return 0; // not reached (FinishTest traps)
}
