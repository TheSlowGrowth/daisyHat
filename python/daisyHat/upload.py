import os
import subprocess
import Tools


def uploadFirmware(firmwareElfFile,
                   progDevice,
                   scriptsFolder=""):
    Tools.printSmallHeadline("Uploading firmware image ...")

    command = ["openocd"]
    if scriptsFolder:
        scriptsFolderAbsPath = os.path.abspath(scriptsFolder)
        command = command + ["-s", scriptsFolderAbsPath]
    else:
        command = command + ["-s", "/usr/local/share/openocd/scripts"]

    command = command + ["-f", progDevice,
                         "-f", "target/stm32h7x.cfg",
                         "-c", "program \"" + firmwareElfFile + "\" verify reset exit"]
    print("command:")
    print(command)

    result = subprocess.run(command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            timeout=20,
                            check=True)
    print(result.stdout.decode("utf-8"))
