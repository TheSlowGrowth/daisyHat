from inspect import getframeinfo, stack

num_failed_assertions = 0

def _get_caller_line_and_file():
    caller = getframeinfo(stack()[2][0])
    return ("%s:%d" % (caller.filename, caller.lineno))

def EXPECT_EQ(a, b):
    global num_failed_assertions
    if a != b:
        num_failed_assertions = num_failed_assertions + 1
        print(f"FAILURE: Expected {str(a)} == {str(b)} in {_get_caller_line_and_file()}")
        return False
    return True

def EXPECT_GT(a, b):
    global num_failed_assertions
    if not a > b:
        num_failed_assertions = num_failed_assertions + 1
        print(f"FAILURE: Expected {str(a)} > {str(b)} in {_get_caller_line_and_file()}")
        return False
    return True

def EXPECT_GE(a, b):
    global num_failed_assertions
    if not a >= b:
        num_failed_assertions = num_failed_assertions + 1
        print(f"FAILURE: Expected {str(a)} >= {str(b)} in {_get_caller_line_and_file()}")
        return False
    return True

def EXPECT_LT(a, b):
    global num_failed_assertions
    if not a < b:
        num_failed_assertions = num_failed_assertions + 1
        print(f"FAILURE: Expected {str(a)} < {str(b)} in {_get_caller_line_and_file()}")
        return False
    return True

def EXPECT_LE(a, b):
    global num_failed_assertions
    if not a <= b:
        num_failed_assertions = num_failed_assertions + 1
        print(f"FAILURE: Expected {str(a)} <= {str(b)} in {_get_caller_line_and_file()}")
        return False
    return True

def EXPECT_NEAR(a, b, max_diff):
    global num_failed_assertions
    if not abs(a - b) < max_diff:
        num_failed_assertions = num_failed_assertions + 1
        print(f"FAILURE: Expected abs({str(a)} - {str(b)}) <= {str(max_diff)} in {_get_caller_line_and_file()}")
        return False
    return True

def EXPECT_TRUE(condition):
    global num_failed_assertions
    if not condition:
        num_failed_assertions = num_failed_assertions + 1
        print(f"FAILURE: Expected {str(condition)} == True in {_get_caller_line_and_file()}")
        return False
    return True

def EXPECT_FALSE(condition):
    global num_failed_assertions
    if condition:
        num_failed_assertions = num_failed_assertions + 1
        print(f"FAILURE: Expected {str(condition)} == False in {_get_caller_line_and_file()}")
        return False
    return True