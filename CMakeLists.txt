project(libDaisyHaT)
cmake_minimum_required(VERSION 3.19)

set(TARGET daisyHat)
set(DAISYHAT_PYTHON_MODULE_DIR ${CMAKE_CURRENT_LIST_DIR}/python CACHE STRING "Path to the daisyHat python module directory")

include(CTest)
find_package(PythonInterp 3.8.5 REQUIRED)

add_library(${TARGET} 
    src/daisyHat.h
    src/daisyHat.cpp
    src/SerialComms.h
    src/SerialComms.cpp
    src/Signals.h
    src/Signals.cpp
    src/testFunctions.cpp
    src/stringConversions.cpp
)

target_link_libraries(${TARGET}
  PRIVATE
    daisy
)

target_include_directories(${TARGET} PUBLIC 
    src
)

set_target_properties(${TARGET} 
  PROPERTIES
    CXX_STANDARD 14
    CXX_STANDARD_REQUIRED
    C_STANDARD 11
    C_STANDARD_REQUIRED
)

target_compile_options(${TARGET}
  PUBLIC
    -Wall
    -Wno-attributes
    -Wno-strict-aliasing
    -Wno-maybe-uninitialized
    -Wno-missing-attributes
    -Wno-stringop-overflow
    $<$<COMPILE_LANGUAGE:CXX>:-Wno-register>
)

include(cmake/daisyhat_add_test.cmake)