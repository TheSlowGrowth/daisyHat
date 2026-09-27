""" I2C transfer test: Alice (master, I2C1) and Bob (slave, I2C4) exchange
fixed byte sequences over a direct I2C connection, for a hardcoded set of
I2C speeds.

Each block in alice.cpp / bob.cpp covers one speed and exercises four
functions in order: Alice blocking send / Bob blocking receive, Bob blocking
send / Alice blocking receive, then the same two directions with the master
(Alice) side running on DMA. (Bob's I2C4 has no DMA support yet, so Bob is
always on the blocking APIs.) The firmwares contain CHECKPOINTs before each
function; for each step the host waits until both devices are held at the
step's checkpoint, and only then releases both — Bob first, because as the
I2C slave he only starts acting once the master (Alice) releases and
addresses him.

The checkpoint primitives (halt_at_checkpoint / release) are part of the
daisyHat host library (daisyhat/daisy_seed.py); the device side is
daisyhat::Checkpoint. The step structure below must stay in sync with the
hardcoded blocks in alice.cpp and bob.cpp.
"""

import time

from daisyhat.hostlog import log

STEPS = [
    # block 0: standard mode (100 kHz)
    ("alice-wait-00", "bob-wait-00", "100 kHz, Alice blocking send / Bob blocking receive"),
    ("alice-wait-01", "bob-wait-01", "100 kHz, Bob blocking send / Alice blocking receive"),
    ("alice-wait-02", "bob-wait-02", "100 kHz, Alice DMA send / Bob blocking receive"),
    ("alice-wait-03", "bob-wait-03", "100 kHz, Bob blocking send / Alice DMA receive"),
    # block 1: fast mode (400 kHz)
    ("alice-wait-10", "bob-wait-10", "400 kHz, Alice blocking send / Bob blocking receive"),
    ("alice-wait-11", "bob-wait-11", "400 kHz, Bob blocking send / Alice blocking receive"),
    ("alice-wait-12", "bob-wait-12", "400 kHz, Alice DMA send / Bob blocking receive"),
    ("alice-wait-13", "bob-wait-13", "400 kHz, Bob blocking send / Alice DMA receive"),
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
            # release Bob first: as the I2C slave he only starts acting once
            # the master (Alice) addresses him, so his transfer is running
            # as soon as Alice's is
            bob_hold.release()
            time.sleep(0.1)
            alice_hold.release()

        alice_result = self.alice.await_test_result()
        bob_result = self.bob.await_test_result()
        log(" ... 'Alice': {}".format("Passed" if alice_result else "Failed"))
        log(" ... 'Bob': {}".format("Passed" if bob_result else "Failed"))
        return alice_result is True and bob_result is True
