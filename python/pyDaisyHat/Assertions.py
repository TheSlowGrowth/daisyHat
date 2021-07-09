from inspect import getframeinfo, stack

numFailedAssertions = 0

def getCallerLineAndFile():
    caller = getframeinfo(stack()[2][0])
    return ("%s:%d" % (caller.filename, caller.lineno))

def EXPECT_EQ(a, b):
    global numFailedAssertions
    if a != b:
        numFailedAssertions = numFailedAssertions + 1
        print(f"FAILURE: Expected {str(a)} == {str(b)} in {getCallerLineAndFile()}")
        return False
    return True

def EXPECT_GT(a, b):
    global numFailedAssertions
    if not a > b:
        numFailedAssertions = numFailedAssertions + 1
        print(f"FAILURE: Expected {str(a)} > {str(b)} in {getCallerLineAndFile()}")
        return False
    return True

def EXPECT_GE(a, b):
    global numFailedAssertions
    if not a >= b:
        numFailedAssertions = numFailedAssertions + 1
        print(f"FAILURE: Expected {str(a)} >= {str(b)} in {getCallerLineAndFile()}")
        return False
    return True

def EXPECT_LT(a, b):
    global numFailedAssertions
    if not a < b:
        numFailedAssertions = numFailedAssertions + 1
        print(f"FAILURE: Expected {str(a)} < {str(b)} in {getCallerLineAndFile()}")
        return False
    return True

def EXPECT_LE(a, b):
    global numFailedAssertions
    if not a <= b:
        numFailedAssertions = numFailedAssertions + 1
        print(f"FAILURE: Expected {str(a)} <= {str(b)} in {getCallerLineAndFile()}")
        return False
    return True

def EXPECT_NEAR(a, b, maxDiff):
    global numFailedAssertions
    if not abs(a - b) < maxDiff:
        numFailedAssertions = numFailedAssertions + 1
        print(f"FAILURE: Expected abs({str(a)} - {str(b)}) <= {str(maxDiff)} in {getCallerLineAndFile()}")
        return False
    return True

def EXPECT_TRUE(condition):
    global numFailedAssertions
    if not condition:
        numFailedAssertions = numFailedAssertions + 1
        print(f"FAILURE: Expected {str(condition)} == True in {getCallerLineAndFile()}")
        return False
    return True

def EXPECT_FALSE(condition):
    global numFailedAssertions
    if condition:
        numFailedAssertions = numFailedAssertions + 1
        print(f"FAILURE: Expected {str(condition)} == False in {getCallerLineAndFile()}")
        return False
    return True