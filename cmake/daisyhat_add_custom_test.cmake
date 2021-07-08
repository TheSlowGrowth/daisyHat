# Adds a custom test that executes a bash command.
# The projects daisyHat config file path will be provided to the command as an
# additional argument: "--config ${DAISYHAT_CONFIG_FILE}"
# 
# Example: 
#   daisyhat_add_custom_test(
#       NAME MyTestName
#       COMMAND MyTestCommand
#   )
function(daisyhat_add_custom_test)
    set(oneValueArgs NAME)
    set(multiValueArgs COMMAND)
    cmake_parse_arguments(PARSED_ARGS "" "${oneValueArgs}"
                        "${multiValueArgs}" ${ARGN})

    # custom config file path for the project ?
    if(NOT DEFINED DAISYHAT_CONFIG_FILE)
        set(DAISYHAT_CONFIG_FILE ${CMAKE_SOURCE_DIR}/daisyHat.config.json)
    endif()

    add_test(
        NAME ${PARSED_ARGS_NAME}
        COMMAND 
            ${PARSED_ARGS_COMMAND} --config ${DAISYHAT_CONFIG_FILE}
    )
endfunction()