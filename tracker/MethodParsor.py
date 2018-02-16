import re

class MethodParsor:
    def __init__(self):
        return

    def DivideMethod(self, classBuffer):
        self.tempBuffer = ''
        self.divideType = []
        self.divideBuffer = []
        count = 0
        lineByline = classBuffer.split("\n")
        while (count < len(lineByline)):
            line = lineByline[count]
            p1 = re.findall(".method", line)
            if len(p1) != 0:
                self.divideType.append("NoneType")
                self.divideBuffer.append(self.tempBuffer)
                self.tempBuffer = ''                        ## Re-Initialization tempBuffer (Re-Cycle)

                count = count + 1
                if ".method" not in lineByline[count]:
                    count = count - 1

                p2 = re.findall(".method public abstract", lineByline[count])
                count = count + self.methodBody(count, lineByline)
                if len(p2) != 0:
                    self.divideType.append("AbstractType")
                    self.divideBuffer.append(self.tempBuffer)
                    self.tempBuffer = ''
                else:
                    self.divideType.append("MethodType")
                    self.divideBuffer.append(self.tempBuffer)
                    self.tempBuffer = ''

            else:
                count = count + 1
                self.tempBuffer += "\n" + line

        if len(self.divideType) == 0:
            self.divideType.append("NoneType")
            self.divideBuffer.append(self.tempBuffer)
    
    def methodBody(self, count, lineBuffer):
        idx = 0
        currentBuff = lineBuffer[count:]
        for line in currentBuff:
            idx = idx + 1
            p1 = re.findall(".end method", line)
            if len(p1) != 0:
                self.tempBuffer += "\n" + line
                return idx

            self.tempBuffer += "\n" + line

    def InjectLocals(self, localCount, bodys):
        codelist = []
        code = "    .locals %d" % localCount
        for line in bodys:
            if len(re.findall(",method", line)) != 0:
                codelist.append(line + "\n" + code)
            else:
                codelist.append(line + "\n")
        return codelist

    def ExpandLocals(self, localCount, bodys):
        codelist = []
        code = "    .locals %d" % localCount
        for line in bodys:
            if len(re.findall(".locals", line)) != 0:
                sizeVariable = int(re.findall("\d+", line)[0])
                if sizeVariable >= 13:
                    return False
                if sizeVariable < localCount:
                    codelist.append(code + "\n")
                else:
                    codelist.append(line + "\n")
            else:
                codelist.append(line + "\n")
        return codelist

    def InjectCodes(self, type_, logcode, methodbody):
        codelist = []
        for line in methodbody:
            if type_ in line:
                codelist.append(line + "\n" + logcode)
            else:
                codelist.append(line + "\n")
        return codelist

    def InjectCodesAfterParams(self, logcode, methodbody):
        codelist = []
        lastidx = self.getLastParamPosition(methodbody)
        for idx in range(len(methodbody)):
            line = methodbody[idx]
            if (lastidx == idx) and (".end param" in line):
                codelist.append(line + "\n" + logcode)
            else:
                codelist.append(line + "\n")
        return codelist

    def getLastParamPosition(self, methodBody):
        lastidx = 0
        for idx in range(len(methodBody)):
            line = methodBody[idx]
            if ".end param" in line:
                lastidx = idx
        return lastidx

    def printCurrentStatus(self):
        print self.divideType
        print self.divideBuffer
