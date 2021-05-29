function(add_daisyhat_test)
    set(oneValueArgs NAME)
    set(multiValueArgs SOURCES)
    cmake_parse_arguments(PARSED_ARGS "" "${oneValueArgs}"
                        "${multiValueArgs}" ${ARGN})

    get_filename_component(LIBDAISY_DIR_ABS "${LIBDAISY_DIR}"
                           REALPATH BASE_DIR "${CMAKE_SOURCE_DIR}")
    set(LINKER_SCRIPT ${LIBDAISY_DIR_ABS}/core/STM32H750IB_flash.lds)

    add_executable(${PARSED_ARGS_NAME} ${PARSED_ARGS_SOURCES})

    target_link_libraries(${PARSED_ARGS_NAME}
        PUBLIC
            daisyHat
            daisy
    )

    set_target_properties(${PARSED_ARGS_NAME} PROPERTIES
        CXX_STANDARD 14
        CXX_STANDARD_REQUIRED YES
        SUFFIX ".elf"
        LINK_DEPENDS ${LINKER_SCRIPT}
    )

    target_link_options(${PARSED_ARGS_NAME} PUBLIC
        -T ${LINKER_SCRIPT}
        -Wl,-Map=${PARSED_ARGS_NAME}.map,--cref
        -Wl,--check-sections
        -Wl,--unresolved-symbols=report-all
        -Wl,--warn-common
        -Wl,--warn-section-align
    )

    add_custom_command(TARGET ${PARSED_ARGS_NAME} POST_BUILD
        COMMAND ${CMAKE_OBJCOPY}
        ARGS -O ihex
        -S ${PARSED_ARGS_NAME}.elf
        ${PARSED_ARGS_NAME}.hex
        BYPRODUCTS
        ${PARSED_ARGS_NAME}.hex
        COMMENT "Generating HEX image"
    VERBATIM)

    add_custom_command(TARGET ${PARSED_ARGS_NAME} POST_BUILD
        COMMAND ${CMAKE_OBJCOPY}
        ARGS -O binary
        -S ${PARSED_ARGS_NAME}.elf
        ${PARSED_ARGS_NAME}.bin
        BYPRODUCTS
        ${PARSED_ARGS_NAME}.bin
        COMMENT "Generating binary image"
    VERBATIM)
endfunction()