cmake_minimum_required(VERSION 3.20)
project(external_memories)

# NOTE: optimized with -Os (as the other libDaisy tests), not via a build type.
add_compile_options(-Os)
add_compile_definitions(NDEBUG)

# Firmware target via libDaisy's default build
set(FIRMWARE_NAME alice)
set(FIRMWARE_SOURCES alice.cpp)
include(${LIBDAISY_DIR}/cmake/DaisyDefaultBuild.cmake)

# daisyHat library
add_subdirectory(${DAISYHAT_DIR} daisyhat)
target_link_libraries(alice PRIVATE daisyHat)
