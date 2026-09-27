cmake_minimum_required(VERSION 3.20)
project(uart_transfer)

# NOTE: optimized with -Os, but not through a CMake build type.
# The Release build type (-O3, -flto, NDEBUG) hangs early in DaisySeed::Init
# (the firmware stalls in HAL_Delay with USB interrupts active; SysTick never
# runs again) - a libDaisy issue to investigate separately. -Os compiles and
# runs like the unoptimized build, while keeping the image in flash.
add_compile_options(-Os)
add_compile_definitions(NDEBUG)


# Firmware 'alice' (UART4) -> flashed to seed 'Alice'
set(FIRMWARE_NAME alice)
set(FIRMWARE_SOURCES alice.cpp)
include(${LIBDAISY_DIR}/cmake/DaisyDefaultBuild.cmake)

# daisyHat test library
add_subdirectory(${DAISYHAT_DIR} daisyhat)
target_link_libraries(alice PRIVATE daisyHat)

# Firmware 'bob' (USART1) -> flashed to seed 'Bob'.
# DaisyDefaultBuild already added libdaisy to the build; DaisyProject sets up
# a single firmware target from FIRMWARE_NAME / FIRMWARE_SOURCES.
set(FIRMWARE_NAME bob)
set(FIRMWARE_SOURCES bob.cpp)
include(${LIBDAISY_DIR}/cmake/DaisyProject.cmake)
target_link_libraries(bob PRIVATE daisyHat)
