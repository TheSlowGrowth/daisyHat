project (daisyHatExamples)
cmake_minimum_required(VERSION 3.19)

# include libDaisy and daisyHat
add_subdirectory(${LIBDAISY_DIR} libdaisy)
add_subdirectory(../ daisyhat)

# include the tests
add_subdirectory(test1)