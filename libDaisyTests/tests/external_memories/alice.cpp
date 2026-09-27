/**
 * Hardware self-test: a single firmware that exercises the features of the
 * Daisy Seed that can only be validated on the physical board, i.e. the
 * external memory hardware that only exists on the real seed (not in any
 * simulator or on a bare MCU):
 *
 *   - SDRAM  : the external 32/64MB SDRAM (AS4C16M16SA), mapped at 0xC0000000
 *   - QSPI   : the external 8MB QSPI flash (IS25LP064A), mapped at 0x90000000
 *
 * Both peripherals are brought up by `DaisySeed::Init()` (which programs the
 * SDRAM controller and configures the QSPI flash in memory-mapped mode), so
 * this firmware can use them right after Init. Checks are added one per
 * peripheral below; add more hardware features (audio codec, ADC/DAC, ...)
 * as new `Check*` functions.
 *
 * NOTE: the QSPI check erases and writes to a single 4kB sector at the very
 * end of the flash. That one sector is DESTROYED by the test.
 */
#include <daisy_seed.h>
#include <daisyHat.h>
#include <string.h>
#include <cstdio>

using namespace daisy;
using namespace seed;

DaisySeed hw;

namespace
{
    // =========================================================================
    // SDRAM
    //
    // A buffer placed in the .sdram_bss linker section (via DSY_SDRAM_BSS)
    // lives in the external SDRAM at 0xC0000000, not in the MCU's internal
    // SRAM. SDRAM is volatile and nothing else is stored here, so these checks
    // are non-destructive: write a pattern, read it back, count mismatches.
    // Reads go through a volatile pointer so the compiler cannot elide them.
    // =========================================================================
    constexpr size_t kSdramSize = 2u * 1024u * 1024u; // 2 MB
    DSY_SDRAM_BSS static uint8_t sdramBuf[kSdramSize];

    void SdramFillVerify(uint8_t value, uint32_t* badCells)
    {
        memset(sdramBuf, value, kSdramSize);
        const volatile uint8_t* v = (const volatile uint8_t*)sdramBuf;
        for(size_t i = 0; i < kSdramSize; i++)
            if(v[i] != value)
                (*badCells)++;
    }

    void SdramFillVerifyIndexed(uint32_t* badCells)
    {
        for(size_t i = 0; i < kSdramSize; i++)
            sdramBuf[i] = (uint8_t)((i * 7u + 0x5Au) & 0xFFu);
        const volatile uint8_t* v = (const volatile uint8_t*)sdramBuf;
        for(size_t i = 0; i < kSdramSize; i++)
            if(v[i] != (uint8_t)((i * 7u + 0x5Au) & 0xFFu))
                (*badCells)++;
    }

    void CheckSdram()
    {
        daisyhat::PrintLine("== SDRAM ==");
        // sanity: the buffer must have been linked into the SDRAM region
        const uintptr_t p = (uintptr_t)sdramBuf;
        EXPECT_TRUE(p >= 0xC0000000u && p < 0xC4000000u);

        uint32_t bad = 0;
        SdramFillVerify(0x00, &bad);
        SdramFillVerify(0xFF, &bad);
        SdramFillVerify(0x55, &bad);
        SdramFillVerify(0xAA, &bad);
        SdramFillVerifyIndexed(&bad);
        EXPECT_TRUE(bad == 0);
        daisyhat::PrintLine("SDRAM: "
                            "0x00/0xFF/0x55/0xAA + indexed pattern verified");
    }

    // =========================================================================
    // QSPI flash
    //
    // hw.qspi is memory-mapped at 0x90000000 (read via plain loads after a
    // cache invalidate). Write/Erase switch the peripheral to indirect-polling
    // mode and back automatically, so they can be called from the default
    // state. Because writing requires a (destructive) erase, the write path is
    // confined to a single 4kB sector at the very end of the 8MB flash.
    // =========================================================================
    constexpr uint32_t kQspiBase   = 0x90000000u;
    constexpr uint32_t kQspiSector = 0x100000u; // a 4kB sector in the middle of the 8MB flash (scratch)
    constexpr size_t   kQspiSize   = 4096u;
    static uint8_t qspiBuf[kQspiSize];

    // per-index expected values for the two states of the sector
    uint8_t ExpectErased(size_t)
    {
        return 0xFFu;
    }
    uint8_t ExpectPattern(size_t i)
    {
        return (uint8_t)((i * 13u + 0xA5u) & 0xFFu);
    }

    // read the whole sector byte-by-byte from the memory-mapped QSPI (a plain
    // per-byte read, matching the libDaisy reference; the region's content
    // changes via the QSPI peripheral, so drop any cached lines first)
    void QspiReadSector()
    {
        dsy_dma_invalidate_cache_for_buffer((uint8_t*)(kQspiBase + kQspiSector), kQspiSize);
        const volatile uint8_t* p = (const volatile uint8_t*)(kQspiBase + kQspiSector);
        for(size_t i = 0; i < kQspiSize; i++)
            qspiBuf[i] = p[i];
    }

    // count mismatches vs expectedAt(i); on failure print how many and the
    // first (offset, got, want) so we can see what the sector actually holds
    void QspiVerify(const char* label, uint8_t (*expectedAt)(size_t))
    {
        uint32_t bad = 0;
        size_t firstOff = 0;
        for(size_t i = 0; i < kQspiSize; i++)
            if(qspiBuf[i] != expectedAt(i))
            {
                if(bad == 0)
                    firstOff = i;
                bad++;
            }
        if(bad != 0)
        {
            char msg[96];
            snprintf(msg, sizeof(msg),
                     "QSPI %s: %u/%u mismatch, first @%u got 0x%02X want 0x%02X",
                     label, (unsigned)bad, (unsigned)kQspiSize, (unsigned)firstOff,
                     (int)qspiBuf[firstOff], (int)expectedAt(firstOff));
            daisyhat::PrintLine(msg);
        }
        EXPECT_TRUE(bad == 0);
    }

    void CheckQspi()
    {
        daisyhat::PrintLine("== QSPI ==");

        // erase, then the sector must read back as 0xFF
        auto eraseRes = hw.qspi.Erase(kQspiSector, kQspiSector + kQspiSize);
        EXPECT_TRUE(eraseRes == QSPIHandle::Result::OK);
        QspiReadSector();
        QspiVerify("erase->0xFF", ExpectErased);

        // write a known pattern, read it back, verify
        for(size_t i = 0; i < kQspiSize; i++)
            qspiBuf[i] = ExpectPattern(i);
        auto writeRes = hw.qspi.Write(kQspiSector, kQspiSize, qspiBuf);
        EXPECT_TRUE(writeRes == QSPIHandle::Result::OK);
        QspiReadSector();
        QspiVerify("write->pattern", ExpectPattern);
        daisyhat::PrintLine("QSPI: erase/write/read verified (one 4kB sector)");
    }
} // namespace

int main()
{
    hw.Configure();
    hw.Init();

    daisyhat::Init(hw, "external_memories", "Alice");

    CheckSdram();
    CheckQspi();

    daisyhat::PrintLine("external_memories: all checks done");
    daisyhat::FinishTest();
    return 0; // not reached (FinishTest traps)
}
