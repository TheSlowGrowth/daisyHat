""" SPI transfer test: Alice (master) and Bob (slave) exchange fixed byte
sequences over a direct SPI connection, for a hardcoded set of SPI
configurations.

Each block in alice.cpp / bob.cpp covers one SPI config and exercises six
functions in order (blocking send / receive / send-and-receive, then the same
three via DMA). The firmwares contain CHECKPOINTs before each function; for
each step the host waits until both devices are held at the step's checkpoint,
and only then releases both — Bob first, because as the SPI slave he only
starts acting once the master releases and clocks.

The checkpoint primitives (halt_at_checkpoint / release) are part of the
daisyHat host library (daisyhat/daisy_seed.py); the device side is
daisyhat::Checkpoint. The step structure below must stay in sync with the
hardcoded blocks in alice.cpp and bob.cpp.
"""

import time

from daisyhat.hostlog import log

STEPS = [
    # block 0: full-duplex, low speed, CPOL=LOW, CPHA=ONE_EDGE (mode 0), full duplex
    ("alice-wait-00", "bob-wait-00", "full duplex 1, blocking send"),
    ("alice-wait-01", "bob-wait-01", "full duplex 1, blocking receive"),
    ("alice-wait-02", "bob-wait-02", "full duplex 1, blocking send and receive"),
    ("alice-wait-03", "bob-wait-03", "full duplex 1, DMA send"),
    ("alice-wait-04", "bob-wait-04", "full duplex 1, DMA receive"),
    ("alice-wait-05", "bob-wait-05", "full duplex 1, DMA send and receive"),
    # block 1: full-duplex, medium speed, CPOL=HIGH, CPHA=TWO_EDGE (mode 3), full duplex
    ("alice-wait-10", "bob-wait-10", "full duplex 2, blocking send"),
    ("alice-wait-11", "bob-wait-11", "full duplex 2, blocking receive"),
    ("alice-wait-12", "bob-wait-12", "full duplex 2, blocking send and receive"),
    ("alice-wait-13", "bob-wait-13", "full duplex 2, DMA send"),
    ("alice-wait-14", "bob-wait-14", "full duplex 2, DMA receive"),
    ("alice-wait-15", "bob-wait-15", "full duplex 2, DMA send and receive"),
    # block 2: simplex Alice-to-Bob
    ("alice-wait-20", "bob-wait-20", "simplex Alice>Bob, blocking send"),
    ("alice-wait-21", "bob-wait-21", "simplex Alice>Bob, DMA send"),
    # block 3: simplex Bob-to-Alice
    ("alice-wait-30", "bob-wait-30", "simplex Bob>Alice, blocking receive"),
    ("alice-wait-31", "bob-wait-31", "simplex Bob>Alice, DMA receive"),
    # block 4: half-duplex. TODO: This requires a connection Master:MOSI <> Slave:MISO which currently doesn't exist. Add later with a better fixture.
    # ("alice-wait-40", "bob-wait-40", "half-duplex, blocking send"),
    # ("alice-wait-41", "bob-wait-41", "half-duplex, blocking receive"),
    # ("alice-wait-42", "bob-wait-42", "half-duplex, DMA send"),
    # ("alice-wait-43", "bob-wait-43", "half-duplex, DMA receive"),
]


class Test:
    def setup(self, ctx):
        expected_images = {"alice", "bob"}
        if set(ctx.images) != expected_images:
            raise ValueError("expected firmware images {}, got {}".format(
                sorted(expected_images), sorted(ctx.images)))
        self.alice = ctx.flash(ctx.images["alice"], "Alice")
        self.bob = ctx.flash(ctx.images["bob"], "Bob")

    def run(self, ctx):
        self.alice.start_test_execution()
        self.bob.start_test_execution()

        for step, (alice_checkpoint, bob_checkpoint, description) in enumerate(STEPS):
            log(" ... step {}: {}".format(step, description))
            # CHECKPOINT: hold Alice before she starts this step's transfer
            alice_hold = self.alice.halt_at_checkpoint(alice_checkpoint)
            # CHECKPOINT: hold Bob before he starts this step's transfer
            bob_hold = self.bob.halt_at_checkpoint(bob_checkpoint)
            # release Bob first: as the SPI slave he only starts acting once
            # the master (Alice) starts clocking, so his transfer is running
            # as soon as Alice's is
            bob_hold.release()
            time.sleep(0.1)
            alice_hold.release()

        alice_result = self.alice.await_test_result()
        bob_result = self.bob.await_test_result()
        log(" ... 'Alice': {}".format("Passed" if alice_result else "Failed"))
        log(" ... 'Bob': {}".format("Passed" if bob_result else "Failed"))
        return alice_result is True and bob_result is True
