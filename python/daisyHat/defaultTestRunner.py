import argparse
import sys
import RunTest
import upload

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--elf", action="store", type=str,
                        help="The firmware *.elf file to upload")
    parser.add_argument("--dev", action="store", type=str,
                        help="The device configuration fileof the device to upload the firmware to")
    args = parser.parse_args()

    firmwareElfFile = args.elf
    # TODO: Read config from the --dev config file
    progDevice = "interface/stlink.cfg"
    serialDevice = "/dev/serial/by-id/usb-Electrosmith_Daisy_Seed_Built_In_346135793139-if00"
    upload.uploadFirmware(firmwareElfFile, progDevice)

    result = RunTest.runTest(serialDevice)
    sys.exit(0 if result == True else 1)
