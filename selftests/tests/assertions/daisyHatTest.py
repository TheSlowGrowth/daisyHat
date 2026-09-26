""" Self-test for the daisyHat C++ assertion macros.

The firmware (main.cpp) runs every assertion macro once with a passing and
once with a failing value. The failure prints are a stable API: this runner
checks that the captured serial output contains exactly the expected failure
messages (in order), no unexpected ones, and the expected total failure
count. The firmware therefore reports `testResult = FAILURE` by design.
"""
import re

# the failure message embeds the compile-time source location
# (`at <path>:<line>`); the path varies per machine, so only the
# file name and line number are matched
AT_SOURCE = r"at .*main\.cpp:\d+"

# expected failure prints, in the firmware's execution order.
# each entry: (message pattern, detail line patterns)
EXPECTED_FAILURES = [
    (rf"FAILURE: Expected a == c {AT_SOURCE}",
     [r"^Where$", r"^     a = '1',$", r"^     c = '2'$"]),
    (rf"FAILURE: Expected a > c {AT_SOURCE}",
     [r"^Where$", r"^     a = '1',$", r"^     c = '2'$"]),
    (rf"FAILURE: Expected a >= c {AT_SOURCE}",
     [r"^Where$", r"^     a = '1',$", r"^     c = '2'$"]),
    (rf"FAILURE: Expected c < a {AT_SOURCE}",
     [r"^Where$", r"^     c = '2',$", r"^     a = '1'$"]),
    (rf"FAILURE: Expected c <= a {AT_SOURCE}",
     [r"^Where$", r"^     c = '2',$", r"^     a = '1'$"]),
    (rf"FAILURE: Expected abs\(f1 - f2\) <= delta {AT_SOURCE}",
     [r"^Where$", r"^     f1 = '1',$", r"^     f2 = '1\.5',$", r"^     delta = '0\.1'$"]),
    (rf"FAILURE: Expected sa == sb {AT_SOURCE}",
     [r"^Where$", r"^     sa = 'a',$", r"^     sb = 'b'$"]),
    (rf"FAILURE: Expected a == c == true {AT_SOURCE}", []),
    (rf"FAILURE: Expected a == b == false {AT_SOURCE}", []),
]


def verify_lines(lines):
    """ Verifies the captured serial lines against EXPECTED_FAILURES.

        :return: list of error strings (empty list = the self-test passed)
    """
    errors = []
    cursor = 0
    for i, (message, details) in enumerate(EXPECTED_FAILURES):
        position = None
        for j in range(cursor, len(lines)):
            if re.search(message, lines[j]):
                position = j
                break
        if position is None:
            errors.append(
                "expected failure message {}/{} not found: {}".format(
                    i + 1, len(EXPECTED_FAILURES), message))
            continue
        for k, detail in enumerate(details):
            index = position + 1 + k
            line = lines[index] if index < len(lines) else None
            if line is None or not re.search(detail, line):
                errors.append(
                    "failure {}: expected detail line {}, got {}".format(
                        i + 1, detail, line))
                break
        cursor = position + 1 + len(details)
    num_failure_lines = sum(1 for line in lines if line.startswith("FAILURE:"))
    if num_failure_lines != len(EXPECTED_FAILURES):
        errors.append(
            "expected {} failure messages, found {}".format(
                len(EXPECTED_FAILURES), num_failure_lines))
    counters = [
        int(m.group(1))
        for line in lines
        for m in [re.search(r"> numFailedAssertions = (\d+)", line)]
        if m]
    if counters != [len(EXPECTED_FAILURES)]:
        errors.append(
            "expected 'numFailedAssertions = {}', got {}".format(
                len(EXPECTED_FAILURES), counters))
    return errors


class Test:
    def setup(self, ctx):
        image_name = next(iter(ctx.images))
        if set(ctx.images) != {image_name}:
            raise ValueError("expected exactly one firmware image, got {}".format(
                sorted(ctx.images)))
        self.seed = ctx.flash(ctx.images[image_name], ctx.default_seed_id)

    def run(self, ctx):
        self.seed.start_test_execution()
        result = self.seed.await_test_result()
        if result is None:
            print("timeout waiting for the test result")
            return False
        if result:
            print("expected testResult = FAILURE (intentional assertion "
                  "failures), got SUCCESS")
            return False
        errors = verify_lines(self.seed.lines)
        if errors:
            for error in errors:
                print("SELFTEST ERROR: " + error)
            return False
        print("assertion self-test passed: {} expected failures verified".format(
            len(EXPECTED_FAILURES)))
        return True
