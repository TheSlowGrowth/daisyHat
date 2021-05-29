import sys
import subprocess

def printBigHeadline(text):
    print("")
    print("#######################################################################")
    print(text)
    print("#######################################################################")
    print("")

def printSmallHeadline(text):
    print("")
    print("-----------------------------------------------------------------------")
    print(text)
    print("-----------------------------------------------------------------------")
    print("")

def checkCall(command, timeoutInSeconds = None):
    if sys.platform.startswith('darwin'):
        subprocess.check_call(command, shell=True, timeout=timeoutInSeconds)
    else:
        subprocess.check_call(command, timeout=timeoutInSeconds)

def checkOutput(command, timeoutInSeconds = None):
    if sys.platform.startswith('darwin'):
        return subprocess.check_output(command, shell=True, timeout=timeoutInSeconds)
    else:
        return subprocess.check_output(command, timeout=timeoutInSeconds)