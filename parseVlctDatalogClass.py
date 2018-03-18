'''
Created on Jan 3, 2018

@author: andersco
'''
from bisect import bisect_right
from time import sleep     

LINE_NUM = 0
TEST_NAME = 1
PATTERN_NAME = 2
MEAS_NAME = 3
PIN_NAME = 3
NOT_FOUND = 99

class parseVlctDatalogClass(object):
        
 
#public functions
    def setDatalogFilename(self, datalogFileName):
        self.__datalogFileName = datalogFileName
    
    
    def getTestNames(self):
        if not self.__dataPulled:
            self.__pullData()
        return self.__testNames
        
    
    def getAnalogMeasNames(self):
        if not self.__dataPulled:
            self.__pullData()
        return self.__analogMeasNames
        
    
    def getContinuityTests(self):
        if not self.__dataPulled:
            self.__pullData()
        return self.__contiuityTests
        
    
    def getTestInstances(self):
        if not self.__dataPulled:
            self.__pullData()
        return self.__testInstances
        
    
    def getPatternNames(self):           
        if not self.__dataPulled:
            self.__pullData()
        return self.__patternNames
  
  
    def doNothing(self):
        sleep(0)
    
        
    '''Private Functions'''
    def __init__(self):
        self.__datalogFileName = "vlctDatalog.txt"
        self.__dataPulled = False
        self.__patternNames = set()
        self.__testNames = set()
        self.__analogMeasNames = set()
        self.__contiuityTests = set()
        self.__testInstances = []
        self.__testInstancesFound = []
        self.__testLineNums = set()
        self.__initSeqLineNums = set()
               
            
    def __pullData(self):
        if not self.__dataPulled:
            self.__getCofLines()
            self.__getTestNames()
            self.__getAnalogDigitalTests()
            self.__dataPulled = True
            
                          
    def __getTestNames(self):
        with open(self.__datalogFileName,"r") as datalogFile:
            for (lineNum,line) in enumerate(datalogFile):
                words = line.split()
                if len(words) > 0:
                    if "TestName:" in words[0]:
                        testName = words[1]
                        self.__storeTestName(testName, lineNum) 
                    elif "Test_Open"  in words[0]:
                        testName = words[1]
                        self.__storeTestName(testName, lineNum)                       
                    elif lineNum == 353895:
                        self.__storeTestName("MRET_2FF_BP_TC_1V_ST", lineNum)
                    elif "====TAG_START_INIT_SEQ====" in line:
                        self.__initSeqLineNums.add(lineNum)
        datalogFile.close()
        #self.__find_Open_Test_tests() #some VLCT test do not output "Testname:" but only output "Open_Test"
        self.__testLineNums = sorted(self.__testLineNums) #put them in order to make future searches easier 

    
    def __getCofLines(self):
        with open(self.__datalogFileName,"r") as datalogFile:
            for (lineNum,line) in enumerate(datalogFile):
                if "OMAP5_XI_OSC_FR" in line:
                    self.doNothing()
                words = line.split()
                if "COF "  == line[:4]:
                    subTest = words[3]
                    testGroup = words[5]
                    patName = words[2]
                    patName = self.__getPatName(line)
                    testName = subTest + "_" + testGroup + "_ST"
                    if "0M" in subTest:
                        testName = subTest[:-4] + "_" + testGroup + subTest[-4:] + "_ST"
                    elif "300K" in subTest:
                        testName = subTest[:-5] + "_" + testGroup + subTest[-5:] + "_ST"
                    elif "52" in subTest:
                        testName = subTest[:-3] + "_" + testGroup + subTest[-3:] + "_ST"
                    elif "104" in subTest:
                        testName = subTest[:-4] + "_" + testGroup + subTest[-4:] + "_ST"
                    elif "MP_DSS1" in subTest:
                        testName = "MP_RETDSS1" + "_" + testGroup[:7] + "_ST"
                    elif "MP_DSS2" in subTest:
                        testName = "MP_RETDSS2" + "_" + testGroup[:7] + "_ST"
                    elif "XS_TOP_MPU_TC_OPNO_CORE_ST" in testName:
                        testName = "XS_SDMA_HANG_TC_OPNO_ST"
                    elif "XS_TOP_MPUALLIP_TC_OPNO_CORE_ST" in testName:
                        testName = "XS_ALLIPPING_TC_OPNO_ST"
                    elif testName == "MP_IVA1_RET_TC_OPNO_ST":
                        testName =  "MP_RETIVA1_TC_OPNO_ST"
                    elif testName == "MP_IVA2_RET_TC_OPNO_ST":
                        testName =  "MP_RETIVA2_TC_OPNO_ST"
                    elif "MP_MPUE_GLGN_LOOSEVSRAMOPL_ST" in testName:
                        testName =  "MP_MPUE_GLGN_TC_VSRAMOPL_ST"
                    elif "MP_MPUE_BRGN_LOOSEVSRAMOPL_ST" in testName:
                        testName =  "MP_MPUS_BRG_TC_VSRAMOPL_ST"
                    elif "MP_GPHY1_RET_TC_OPNO_ST" in testName:
                        testName =  "MP_RETGPHY1_TC_OPNO_ST"
                    elif "MP_GPHY2_RET_TC_OPNO_ST" in testName:
                        testName =  "MP_RETGPHY2_TC_OPNO_ST"
                    elif testName == "TP_DSIA_HSTX_0_MO_ST":
                        testName =  "TG_DSIA_HSTX_EMUL_MO"
                    elif testName == "TP_DSIA_HSTX_1_MO_ST":
                        testName =  "TG_DSIA_HSTX_EMUL_MO"
                    elif testName == "OMAP5_XI_OSC_RMR_TC_VMAX_ST":
                        testName =  "OMAP5_XI_OSC_TC_VMAX_ST"
                    self.__storeTestName(testName, lineNum)                       
                    testInst = (testName,patName,"","","","","")
                    if testInst not in self.__testInstancesFound:
                        self.__storePatternTestInstance(testInst,lineNum)
        datalogFile.close()
            
        
    def __storeTestName(self,testName,lineNum):
        if not self.__skipTest(testName):
            self.__testNames.add(testName)
            self.__testLineNums.add(lineNum)
            testName = "<" + testName + ">"
            testInst = (testName,"","","","","","")
            #if testInst not in self.__testInstancesFound:
            self.__testInstancesFound.append(testInst)
            testInst = tuple([lineNum]) + testInst
            self.__testInstances.append(testInst)
   
    
    def __getAnalogDigitalTests(self):
        with open(self.__datalogFileName,"r") as datalogFile:
            for (lineNum,line) in enumerate(datalogFile):
                if lineNum in self.__initSeqLineNums:
                    testName = self.__getInitSeqTestName(lineNum)
                elif lineNum in self.__testLineNums:
                    testName = self.__getTestName(lineNum)
                elif self.__isPatternTests(line):
                    patName = self.__getPatName(line)
                    if patName != "SKIP_PATTERN":
                        testInst = (testName,patName,"","","","","")
                        if testInst not in self.__testInstancesFound:
                            self.__storePatternTestInstance(testInst,lineNum)
                elif self.__isAnalogTest(line):
                    testInst = self.__getAnalogTestInst(testName, line)
                    if testInst not in self.__testInstancesFound:
                        if self.__isContinuityTest(line):
                            self.__storeContinuityTestInstance(testInst, lineNum)
                        else:
                            self.__storeAnalogTestInstance(testInst, lineNum)
                elif self.__isEfuseTest(line):
                    testInst = self.__getEfuseTestInst(line)
                    if testInst not in self.__testInstancesFound:
                        self.__storeAnalogTestInstance(testInst, lineNum)
        datalogFile.close()
 
            
    def __isContinuityTest(self,line):
        #codeAndDebug
        self.doNothing()
    
    
    def __isPatternTests(self,line):
        isPatternTests = True if "Pat_Name" in line else False
        return isPatternTests
        
        
    
    def __getEfuseTestInst(self,line):
        line = line.upper()
        words = line.split()
        testName = words[0]
        minLimit = words[1]
        maxLimit = words[2]
        measRslt = words[3]
        testInst = (testName,"",testName,minLimit,measRslt,maxLimit,"")
        return testInst
    
    
    def __isEfuseTest(self,line):
        if (line[:3] == "FF_"):
            words = line.split()
            if words[1].isdigit():
                return True
            else:
                return False
        else:
            return False
   
    
    def __storePatternTestInstance(self,testInst,lineNum):
        self.__testInstancesFound.append(testInst)
        testInst = tuple([lineNum]) + testInst
        self.__testInstances.append(testInst)
        self.__patternNames.add(testInst[PATTERN_NAME])
   
    
    def __skipTest(self,testName):
        #if testName in self.__testNames: XBCRXAALPRX_4DL_PM1D
            #return True
        if testName == "C_PBIST_TOP_DSS_BZGS_CKR0_OPNO_ST":
            return True
        elif testName[:3] == "IP_":
            return True  
        elif "PTRIMHDMI_CHAR0" in testName:
            return True
        elif "POWERSUM_850_ST" in testName:
            return True
        elif "USB2_GPIORX_ST" in testName:
            return True
        else:
            return False     
    
    
    def __getInitSeqTestName(self,lineNum):
        #find the line number of the first test name after init sequence
        i = bisect_right(self.__testLineNums, lineNum)
        testLineNum = self.__testLineNums[i]
        #get the first instance that includes this line number
        foundInstance = next((inst for inst in self.__testInstances if inst[LINE_NUM] == testLineNum), None)
        try:
            testName = foundInstance[TEST_NAME]
        except:
            self.doNothing()
        testName = testName[1:-1] #remove "<>" from test name
        return testName
 
    
    def __getTestName(self,lineNum):
        #get the first instance that includes this line number
        foundInstance = next((inst for inst in self.__testInstances if inst[LINE_NUM] == lineNum), None)
        try:
            testName = foundInstance[TEST_NAME]
        except:
            self.doNothing()
        testName = testName[1:-1] #remove "<>" from test name
        if "DIEIDPINOPENSTEST_ST" == testName:
            testName = "EFUSE_STD_INITCHECK_1_ST"
        return testName
   
    
    def __storeContinuityTestInstance(self,testInst,lineNum):
        #codeAndDebug
        #self.__testInstancesFound.append(testInst)
        #testInst = tuple([lineNum]) + testInst
        #self.__testInstances.append(testInst)
        #contTestInst = (testInst[TEST_NAME],testInst[PIN_NAME])
        #self.__contiuityTests.add(contTestInst)
        self.doNothing()
   
    
    def __storeAnalogTestInstance(self,testInst,lineNum):
        self.__testInstancesFound.append(testInst)
        testInst = tuple([lineNum]) + testInst
        if "IQ_VIDEOPB" in testInst[MEAS_NAME]:
            testInstList = list(testInst)
            testInstList[1] = "IDDQ_VIDEOPLAYBACK"
            testInst = tuple(testInstList)
        self.__testInstances.append(testInst)
        self.__analogMeasNames.add(testInst[MEAS_NAME])
   
    
    def __getAnalogTestInst(self,testName,line):
        line = line.upper()
        pinName = line[:31]
        pinName = pinName.strip()
        minLimit = line[35:45]
        minLimit = minLimit.strip()
        maxLimit = line[46:56]
        maxLimit = maxLimit.strip()
        units = line[57:62]
        units = units.strip()
        measRslt = line[63:74]
        measRslt = measRslt.strip()
        testInst = (testName,"",pinName,minLimit,measRslt,maxLimit,units)
        return testInst
    
    
    def __getPatName(self,line):
        words = line.split()
        if words[2] == ",":
            patName = words[3]
        else:
            patName = words[2]
        patName = patName.upper()
        if "_4DL_PM" in patName:
            indx = patName.index("_4DL_PM") + 4
            patName = patName[:indx] 
        elif patName[-4:-1] == "_PM":
            patName = patName[:-4] #on uflex all PM stops in one patterns 
        elif patName[-5:-2] == "_PM":
            patName = patName[:-5] #on uflex all PM stops in one patterns 
        elif patName[-8:] == "_FSCAN30":
            patName = patName[:-8] #on uflex all PM stops in one patterns
        elif patName == "T_NAME":
            patName = "SKIP_PATTERN" 
        elif  "_MG1B" in patName:
            patName = "SKIP_PATTERN" 
        return patName


    def __isAnalogTest(self,line):
        line = line.upper()
        try:
            measUnit = line[57:63]
            measUnit = measUnit.upper()
            measUnits = [" V "," MV "," UV "," A "," MA "," UA "," NA ",
                         " Z ", " M "," U "," MHZ "]
            foundUnit = next((unit for unit in measUnits if unit in measUnit), NOT_FOUND)
            if foundUnit == NOT_FOUND:
                return False
            else:
                if self.__pbTestNoLimits(line):
                    return False
                return True
        except:
            return False


    def __pbTestNoLimits(self,line):
        if "IQ_VIDEOPB_" in line:
            maxLimit = line[46:56]
            maxLimit = maxLimit.strip()
            return True if maxLimit == "" else False
        else:
            return False
        

#used to test class using runs as 
if __name__ == '__main__':
    
    vlct = parseVlctDatalogClass()
    
    vlct.setDatalogFilename("vlctDatalog_FT1.txt")
    testInsts =  vlct.getTestInstances() #this will take 3-4 minutes to run
    testNames =  vlct.getTestNames()
    testMeas =  vlct.getAnalogMeasNames()
    contTests = vlct.getContinuityTests()
    testPats =  vlct.getPatternNames()          
    vlct.doNothing()