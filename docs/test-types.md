# Types of tests supported by daisyHat

A test is a subdirectory of `tests/` (inside a test root) that contains a
`CMakeLists.txt` making it a standalone CMake project. An optional
`daisyHatTest.py` file next to it provides host-side orchestration hooks.

The different kinds of tests are:

- Single Seed:
  The test's CMake project registers exactly one firmware image. The default
  flow (used when no `daisyHatTest.py` is present) flashes it to the suite's
  default seed (the `defaultSeed` in the `daisyHat.config.json` at the test
  root), starts the test execution there and collects the result.

  ```cpp
  // <test-root>/tests/mySeedTest/main.cpp
  #include <daisy_seed.h>
  #include <daisyHat.h>

  daisy::DaisySeed seed;

  int main() {
      seed.Configure();
      seed.Init();

      daisyhat::Init(seed, "mySeedTest");

      // <perform the test, using daisyhat::EXPECT_* macros>

      daisyhat::FinishTest();

      return 0;
  }
  ```

- Multi Seed:
  The test's CMake project registers one firmware image per seed. The
  association of images and seeds is provided by a `daisyHatTest.py` file
  (see below); with the default flow only one image is supported.

- Custom (non-firmware) host tests:
  A test directory whose CMake project registers no firmware image. Its
  `daisyHatTest.py` performs host-side steps instead.

## Tests with a custom test runner

When the test directory contains a `daisyHatTest.py`, the CLI imports it and
drives the `Test` class it defines, instead of using the default flow:

```python
# <test-root>/tests/mySeedTest/daisyHatTest.py

class Test:

    def setup(self, ctx):
        """Called before run(). Flash firmware here and set up fixtures."""
        self.seed_a = ctx.flash(ctx.images["appA"], "Alice")
        self.seed_b = ctx.flash(ctx.images["appB"], "Bob")

    def run(self, ctx):
        """Called after setup(). Return True if the test passed."""
        self.seed_a.start_test_execution()
        self.seed_b.start_test_execution()
        return self.seed_a.await_test_result() and self.seed_b.await_test_result()

    def teardown(self, ctx):
        """Called after run() in all cases (even on failure)."""
        pass
```

`setup` and `teardown` are optional, `run` is required. If `run` raises an
exception, the test fails. The context object `ctx` is provided by the CLI
and contains everything the test needs:

- `ctx.test_name` – the name of the test (its directory name)
- `ctx.test_dir`, `ctx.build_dir` – the test directory and its `.build`
  directory
- `ctx.images` – the built firmware images, as a dict of image name to `.elf`
  path (the image name is the filename without extension)
- `ctx.seed_ids` – the identifiers of the configured seeds
- `ctx.default_seed_id` – the suite's default seed (the `defaultSeed` from
  the config file, or the single seed if there is only one)
- `ctx.config` – the raw parsed `daisyHat.config.json` dict
- `ctx.flash(image, seed_id)` – flash the `.elf` image to the given seed and
  open its serial connection; returns the connected `DaisySeed`
- `ctx.connect(seed_id)` – open the serial connection to the given seed
  without flashing; returns the connected `DaisySeed`

All serial connections opened through the context are closed automatically
after the test, so `teardown` can use them but doesn't have to close them.

The returned `DaisySeed` objects support everything the default flow uses:
`start_test_execution()`, `await_test_result(timeout_ms)`,
`send_signal(signal)`, `send_integer(value)`, `send_string(string)`, and so
on (see `daisyhat.daisy_seed`).
