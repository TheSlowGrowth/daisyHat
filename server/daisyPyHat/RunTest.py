import Tools
import serial

def RunTest(serialDevice):
    Tools.printSmallHeadline("Running test on device...")
    device = serial.Serial(serialDevice, timeout=5000)
    device.flushInput()

    # read lines from the serial connection until the test result
    # is received
    line = device.readline()
    while not line.startswith("> testResult = "):
        print(">>> " + line)
        line = device.readline()
    
    # extract result
    if line.startswith("> testResult = SUCCESS"):
        return True
    else:
        return False

