# daisyHat is included as a subdirectory of the test project
# (add_subdirectory(${DAISYHAT_DIR} daisyhat)) and provides the
# daisyHat library target. It intentionally does not call project()
# so it can be included without interfering with the parent project.

set(TARGET daisyHat)

add_library(${TARGET} STATIC
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
