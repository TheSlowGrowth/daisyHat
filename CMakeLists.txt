project(libDaisyHaT)
cmake_minimum_required(VERSION 3.19)

set(TARGET daisyHat)

add_library(${TARGET} 
    src/daisyHat.cpp
    src/daisyHat.h
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

include(cmake/add_daisyhat_test.cmake)