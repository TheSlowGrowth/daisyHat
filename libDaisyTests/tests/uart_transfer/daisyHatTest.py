""" UART transfer test: Alice (UART4) and Bob (USART1) exchange fixed byte
sequences over a direct, cross-wired UART connection (Alice TX -> Bob RX,
Alice RX <- Bob TX), for a hardcoded set of baud rates.

The two seeds share the same two wires the i2c_transfer test uses:
Alice UART4 is on D11 (RX) / D12 (TX), Bob USART1 is on D13 (TX) / D14 (RX).

Each block in alice.cpp / bob.cpp covers one baud rate and exercises six
steps in order, alternating the blocking and DMA APIs on both sides:

    step 00  Alice blocking send   / Bob blocking receive
    step 01  Bob blocking send     / Alice blocking receive
    step 02  Alice DMA send        / Bob blocking receive
    step 03  Bob DMA send          / Alice blocking receive
    step 04  Alice blocking send   / Bob DMA receive
    step 05  Bob blocking send     / Alice DMA receive

Synchronization differs from the i2c/spi tests: UART has no master/slave
addressing or flow control, so once the sender starts clocking bits, any
byte the receiver is not yet sampling is simply lost. The firmwares contain
CHECKPOINTs before each function; for each step the host holds both devices
at the step's checkpoint, releases the *receiver* first (so its peripheral is
armed and polling), waits, and only then releases the *sender*. The
`receiver` field of each step selects that release order.

The checkpoint primitives (halt_at_checkpoint / release) are part of the
daisyHat host library (daisyhat/daisy_seed.py); the device side is
daisyhat::Checkpoint. The step structure below must stay in sync with the
hardcoded blocks in alice.cpp and bob.cpp.
"""

import time

from daisyhat.hostlog import log

# (receiver, alice_checkpoint, bob_checkpoint, description)
STEPS = [
    # block 0: 115200 baud
    ("bob",   "alice-wait-00", "bob-wait-00", "115200, Alice blocking send / Bob blocking receive"),
    ("alice", "alice-wait-01", "bob-wait-01", "115200, Bob blocking send / Alice blocking receive"),
    ("bob",   "alice-wait-02", "bob-wait-02", "115200, Alice DMA send / Bob blocking receive"),
    ("alice", "alice-wait-03", "bob-wait-03", "115200, Bob DMA send / Alice blocking receive"),
    ("bob",   "alice-wait-04", "bob-wait-04", "115200, Alice blocking send / Bob DMA receive"),
    ("alice", "alice-wait-05", "bob-wait-05", "115200, Bob blocking send / Alice DMA receive"),
    # block 1: 921600 baud
    ("bob",   "alice-wait-10", "bob-wait-10", "921600, Alice blocking send / Bob blocking receive"),
    ("alice", "alice-wait-11", "bob-wait-11", "921600, Bob blocking send / Alice blocking receive"),
    ("bob",   "alice-wait-12", "bob-wait-12", "921600, Alice DMA send / Bob blocking receive"),
    ("alice", "alice-wait-13", "bob-wait-13", "921600, Bob DMA send / Alice blocking receive"),
    ("bob",   "alice-wait-14", "bob-wait-14", "921600, Alice blocking send / Bob DMA receive"),
    ("alice", "alice-wait-15", "bob-wait-15", "921600, Bob blocking send / Alice DMA receive"),
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

        for step, (receiver, alice_checkpoint, bob_checkpoint, description) in enumerate(STEPS):
            log(" ... step {}: {}".format(step, description))
            # CHECKPOINT: hold Alice before she starts this step's transfer
            alice_hold = self.alice.halt_at_checkpoint(alice_checkpoint)
            # CHECKPOINT: hold Bob before he starts this step's transfer
            bob_hold = self.bob.halt_at_checkpoint(bob_checkpoint)
            # Release the receiver first: UART has no flow control, so the
            # receiver's peripheral must already be armed and polling before
            # the sender starts clocking bits, or the bytes are lost.
            if receiver == "bob":
                bob_hold.release()
                time.sleep(0.1)
                alice_hold.release()
            else:
                alice_hold.release()
                time.sleep(0.1)
                bob_hold.release()

        alice_result = self.alice.await_test_result()
        bob_result = self.bob.await_test_result()
        log(" ... 'Alice': {}".format("Passed" if alice_result else "Failed"))
        log(" ... 'Bob': {}".format("Passed" if bob_result else "Failed"))
        return alice_result is True and bob_result is True
