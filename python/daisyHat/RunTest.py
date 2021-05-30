import re
import serial
import time

import Tools

def runTest(serialDevice):

    sanitizedDevice = re.sub(r'[^A-Za-z0-9\\\/]', '', serialDevice)

    Tools.printSmallHeadline("Running test on device '" + sanitizedDevice + "' ...")

    maxNumAttempts = 30
    numAttemps = 0
    device = None
    while not device:
        try:
            device = serial.Serial(sanitizedDevice, timeout=10)
        except serial.SerialException as e:
            numAttemps = numAttemps + 1
            if numAttemps < maxNumAttempts:
                time.sleep(1)
            else:
                print("ERROR: Failed to connect to serial port after " + str(numAttemps) + " attempts")
                return False
        except Exception as e:
            print("ERROR: Exception while opening serial port:")
            print(e)
            return False

    device.flushInput()

    # read lines from the serial connection until the test result
    # is received
    line = device.readline()
    if not line:
        print("ERROR: Timeout")
        return False
    print(">>> " + line.decode("UTF-8").rstrip())

    while not line.decode("UTF-8").startswith("> testResult = "):
        line = device.readline()
        if not line:
            print("ERROR: Timeout")
            return False
        print(">>> " + line.decode("UTF-8").rstrip())
    
    # extract result
    if line.decode("UTF-8").startswith("> testResult = SUCCESS"):
        return True
    else:
        return False

