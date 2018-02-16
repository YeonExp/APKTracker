import re
import sys
import string
import traceback
import os as command
import Utils
from MethodParsor import *

class Tracker(MethodParsor):
    def __init__(self, message="Tracking!!"):
        self.author = "@Yeon"
        self.log = ""
        self.message = message
        self.lastBuffer = ''
        self.currentBuf = None
        self.classFileList = []
        self.currentClass = []
        self.finalBuffer = []
        self.currentPath = command.getcwd()
        self.base = self.currentPath + "/base"
        self.temp = self.currentPath + "/temp"
        self.target = self.temp + "/smali"
        self.blacklist = ["/smali/com/google","/smali_classes2/android", "/smali/android", "/smali_classes2/com/google",
                          "/smali_classes2/org"]
    def makeTemp(self):
        command.system("rm -rf %s" % (self.temp))
        command.system("cp -a %s %s" % (self.base, self.temp))

    def checkBlackList(self, search):
        for black in self.blacklist:
            if black in search:
                return True
        return False

    def getAllClassFiles(self, ends):
        for path, subdirs, files in command.walk(self.target):
            for name in files:
                absolute = command.path.join(path, name)
                if absolute.endswith(ends) == True:
                     if self.checkBlackList(absolute) == True:
                         continue
                     self.classFileList.append(absolute)
                     self.currentClass.append(Utils.reverse_strchr(absolute))

    def existHeader(self, formData, search):
        if len(re.findall(search, formData)) != 0:
            return True
        else:
            return False

    def expandPrologue(self, methodData):
        methodSplit = methodData.split("\n")

        local_flag = self.existHeader(methodData, ".locals")
        prologue_flag = self.existHeader(methodData, ".prologue")
        param_flag = self.existHeader(methodData, ".end param")
        # local_flag = True

        if local_flag == False:
            methodSplit = MethodParsor.InjectLocals(self, 2, methodSplit)
        else:
            methodSplit = MethodParsor.ExpandLocals(self, 2, methodSplit)
            if methodSplit == False:
                return False
        
        # Insert Tracking Code
        if prologue_flag == True:
            methodSplit = MethodParsor.InjectCodes(self, ".prologue", self.log, methodSplit)
        elif param_flag == True:
            methodSplit = MethodParsor.InjectCodesAfterParams(self, self.log, methodSplit)
        elif local_flag == True:
            methodSplit = MethodParsor.InjectCodes(self, ".locals", self.log, methodSplit)
        
        return ''.join(x for x in methodSplit)

    ## Custom Smali Code's Area
    def generateLogCode(self, className, methodBody):
        name = Utils.reverse_strchr(className)
        for data in methodBody:
            if ".method" in data:
                functionName = Utils.getParseFunction(data)

        ## User can control and change contents in this code.
        logs =  "    const-string v0, \"Break: %s\"\n" % name
        logs += "    const-string v1, \"%s\"\n" % functionName
        logs += "    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I\n"
        self.log = logs

    def build(self):
        for path_c in range(len(self.classFileList)):
            self.finalBuffer = []
            currentClass = self.classFileList[path_c]
            print "[*] Patched : %s" % currentClass
            self.currentBuf = Utils.read_all_contents(currentClass)
            MethodParsor.DivideMethod(self, self.currentBuf)                    # Parse the Class File, (NoneType or MethodType)
            
            # MethodParsor.printCurrentStatus(self)
            # print self.divideBuffer
            # print self.divideType
            for types in range(len(self.divideType)):
                if self.divideType[types] == "NoneType":
                    self.finalBuffer.append(self.divideBuffer[types])
                elif self.divideType[types] == "MethodType":
                    self.generateLogCode(currentClass, self.divideBuffer[types].split("\n"))    # Generate Log Code
                    expandBuf = self.expandPrologue(self.divideBuffer[types])
                    if expandBuf == False:
                        self.finalBuffer.append(self.divideBuffer[types])
                        print "[*] Except : %s (Too big local registers)" % currentClass
                    else:
                        self.finalBuffer.append(expandBuf)
                elif self.divideType[types] == "AbstractType":
                    self.finalBuffer.append(self.divideBuffer[types])
            Utils.new_write(currentClass, self.finalBuffer)

    def run(self):
        self.makeTemp()
        self.getAllClassFiles("smali")
        self.build()
        print "[*] Complete"
