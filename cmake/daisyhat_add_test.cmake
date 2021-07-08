# Adds a multiple firmwares image for Daisy Seeds that link to libDaisy and libDaisyHat.
# Registers a simple test runner that downloads the images to the specified Daisy Seeds
# and collects the results from all of them.
# A firmware is added by FIRST specifying the ID of the Seed to download to, then
# specifying the source files to include in the firmware.
# 
# Example: 
#   daisyhat_add_test(
#       NAME MyTestName
#       SEED SeedIdToDownloadTo
#       SOURCES
#           main.cpp
#           util.cpp
#       SEED AnotherSeedIdToDownloadTo
#       SOURCES
#           main.cpp
#           util.cpp
#   )
function(daisyhat_add_test)
    set(current_firmware_seed_id "")
    set(current_firmware_sources "")
    set(expecting_name 0)
    set(expecting_seed_id 0)
    set(expecting_sources 0)
    set(runner_aguments "${DAISYHAT_PYTHON_MODULE_DIR}/runners/daisyHatTestRunner.py")

    macro(daisyhat_internal_complete_firmware)
        # add the firmware
        daisyhat_add_firmware(
            NAME "${test_name}_firmware_${current_firmware_seed_id}"
            SOURCES ${current_firmware_sources}
        )
        # add the runner arguments
        list(APPEND runner_aguments 
            "--firmware" 
            "$<TARGET_FILE:${test_name}_firmware_${current_firmware_seed_id}>"
            "${current_firmware_seed_id}"
        )
    endmacro()

    foreach(arg IN LISTS ARGN)
        # check if the argument is a command
        if("${arg}" STREQUAL "NAME")
            set(expecting_name 1)
            set(expecting_seed_id 0)
            set(expecting_sources 0)
        elseif("${arg}" STREQUAL "SEED")
            set(expecting_name 0)
            set(expecting_seed_id 1)
            set(expecting_sources 0)
        elseif("${arg}" STREQUAL "SOURCES")
            set(expecting_name 0)
            set(expecting_seed_id 0)
            set(expecting_sources 1)
        else()
            # argument is not a command, must be a value
            if(${expecting_sources} EQUAL 1)
                list(APPEND current_firmware_sources "${arg}")
            elseif(${expecting_name} EQUAL 1)
                set(expecting_name 0)
                set(test_name "${arg}")
            elseif(${expecting_seed_id} EQUAL 1)
                set(expecting_seed_id 0)
                # check if this completes the current firmware
                if(NOT ${current_firmware_seed_id} STREQUAL "${arg}")
                    daisyhat_internal_complete_firmware()
                    # reset sources array for the next firmware
                    set(current_firmware_sources "")
                endif()
                # set seed it for the next firmware
                set(current_firmware_seed_id "${arg}")
            endif()
        endif()
    endforeach()

    # finish the current firmware
    if(NOT ${current_firmware_seed_id} STREQUAL "")
        daisyhat_internal_complete_firmware()
        # reset sources array for the next firmware
        set(current_firmware_sources "")
    endif()

    daisyhat_add_custom_test(
        NAME ${test_name}
        COMMAND 
            ${PYTHON_EXECUTABLE} ${runner_aguments}
    )
endfunction()