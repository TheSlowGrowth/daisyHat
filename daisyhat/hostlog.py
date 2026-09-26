"""Host-side logging for daisyHat.

Every line the host prints to the console (its own messages and lines
received from the devices) is prefixed with a host-side timestamp, so that
a captured log gives the real timeline of a test run, independent of how the
terminal interleaves output.
"""

import time


def timestamp():
    """ Returns the current host time as a string, local time with
    millisecond precision, e.g. '21:10:13.946' """
    t = time.time()
    return "{}.{:03d}".format(time.strftime("%H:%M:%S", time.localtime(t)),
                             int((t % 1) * 1000))


def log(message):
    """ Prints a host-side log line with a timestamp prefix """
    print("[{}] {}".format(timestamp(), message))
