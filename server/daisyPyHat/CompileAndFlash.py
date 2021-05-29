from server.Tools import checkCall
import Tools
import os

def compile(firmwareFolder):
    absPath = os.path.abspath(firmwareFolder)
    Tools.checkCall("cd " + absPath + " && make")

def upload(firmwareFolder):
    absPath = os.path.abspath(firmwareFolder)
    Tools.checkCall("cd " + absPath + " && make upload")

def compileAndUpload(firmwareFolder):
    absPath = os.path.abspath(firmwareFolder)
    Tools.printSmallHeadline("Compiling " + absPath)
    compile(absPath)
    Tools.printSmallHeadline("Uploading " + absPath)
    upload(absPath)