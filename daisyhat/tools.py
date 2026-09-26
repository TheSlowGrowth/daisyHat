from . import hostlog


def print_big_headline(text):
    hostlog.log("")
    hostlog.log("#######################################################################")
    hostlog.log(text)
    hostlog.log("#######################################################################")
    hostlog.log("")


def print_small_headline(text):
    hostlog.log("")
    hostlog.log("-----------------------------------------------------------------------")
    hostlog.log(text)
    hostlog.log("-----------------------------------------------------------------------")
    hostlog.log("")

def print_warning(text):
    hostlog.log("WARNING: " + str(text))

def print_info(text):
    hostlog.log("INFO: " + str(text))
