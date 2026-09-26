cmake_minimum_required(VERSION 3.20)
project(assertions)

# Firmware target via libDaisy's default build
set(FIRMWARE_NAME assertions)
set(FIRMWARE_SOURCES main.cpp)
include(${LIBDAISY_DIR}/cmake/DaisyDefaultBuild.cmake)

# daisyHat library
add_subdirectory(${DAISYHAT_DIR} daisyhat)
target_link_libraries(assertions PRIVATE daisyHat)
