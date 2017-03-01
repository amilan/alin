## @package alinspinctrl.py 
#    File containing the device class, to control any device in the FPGA
#
#    Author = "Manuel Broseta"
#    Copyright = "Copyright 2016, ALBA"
#    Version = "1.0"
#    Email = "mbroseta@cells.es"
#    Status = "Development"
#    History:
#   07/10/2016 - file created by Manuel Broseta

__author__ = "Manuel Broseta"
__copyright__ = "Copyright 2016, ALBA"
__license__ = "GPLv3 or later"
__version__ = "1.0"
__email__ = "mbroseta@cells.es"
__status__ = "Development"

import os

from random import uniform

from alin.base import AlinDevice
from alin.base import AlinLog
from alin.base import getConfigData

_CONFIG_MASK = "FPGA_"

class FPGA(AlinLog):
    def __init__(self, debug=False, logger='FPGA   '):
        AlinLog.__init__(self, debug=False, loggerName=logger)        

        # Get default configuration from config file
        self._debug = debug
        self._logger = logger
        self._devicedict = {}
        self.configure()
        
        self.logMessage("__init__() Initialized ", self.DEBUG)

    def configure(self):
        # Get default configuration from config file
        configDict = getConfigData(_CONFIG_MASK)
        self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else self._debug
        self._debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 40

        # Logging
        self.logLevel(self._debuglevel)
        self.logEnable(self._debug)
        
        self.logMessage("configure() %s configured"%_CONFIG_MASK, self.INFO)        

    def init(self):
        devfolder = os.environ.get('ALINPATH', 'Not Set')
        if devfolder != 'Not Set':
            devfolder = devfolder +"/deviceslib"            

            onlyfiles = [ f for f in os.listdir(devfolder) if os.path.isfile(os.path.join(devfolder,f)) ]
            
            if onlyfiles != []:
                for f in onlyfiles:
                    self._devicedict[f] = {}
                self.logMessage("init() Device list set", self.INFO)        
            else:
                self.logMessage("init() No devices found on devicelib folder", self.ERROR)            
        else:
            self.logMessage("init() ALINPATH not set", self.ERROR)

    def stop(self):
        # Clear devicelist
        self._devicedict = {}
        
    def getDevices(self):
        ret_value = None
        if self._devicedict != {}:
            ret_value = self._devicedict.keys() 
        return ret_value

    def checkDevice(self, device=None, num=0):
        ret_value = None
        self.logMessage("checkDevice(): Check device %s number %s in list and return pointer"%(device,str(num)),self.DEBUG)
        try:
            if self._devicedict[device] == {} or num not in self._devicedict[device].keys():
                tmp_dev = AlinDevice(device, num, self._debug, self._logger)
                self._devicedict[device][num] = tmp_dev
                ret_value = tmp_dev
            else:
                ret_value = self._devicedict[device][num]
        except Exception, e:
            self.logMessage("checkDevice() not possible to get device info due to %s"%str(e), self.ERROR)
                
        return ret_value


    def writeFPGARegister(self, device, num, register, value):
        self.logMessage("writeFPGARegister(): Device:%s number:%s Register:%s value=%s"%(device, str(num), str(register),str(value)),self.INFO)
        try:
            alindev = self.checkDevice(device, num)
            alindev.writeAttribute(register,int(value))
            self.logMessage("writeFPGARegister(): Write OK",self.INFO)
        except Exception, e:
            self.logMessage("writeFPGARegister() Failed due to %s"%str(e), self.ERROR)
    
    def readFPGARegister(self, device, num, register):
        value = None
        try:
            alindev = self.checkDevice(device, num)
            value = alindev.readAttribute(register)
            self.logMessage("readRegister():  Device:%s number:%s Register:%s read value=%s"%(device, str(num), str(register),str(value)),self.DEBUG)
        except Exception, e:
            self.logMessage("readRegister() Failed due to %s"%str(e), self.ERROR)
        return value
    
    def getFWVersion(self):
        # Use ADCCore device to get the FW version, but any other device could be used
        fwversion = None
        try:
            alindev = self.checkDevice('WB-FMC-ADC-CORE')
            fwversion = alindev.sdbDrv.getFWVersion()
            self.logMessage("getFWVersion(): Version=%s"%fwversion,self.INFO)
        except Exception, e:
            self.logMessage("getFWVersion() Failed due to %s"%str(e), self.ERROR)
        return fwversion

    def getFWVersionDate(self):
        # Use ADCCore device to get the FW version, but any other device could be used
        fwversiondate = None
        try:
            alindev = self.checkDevice('WB-FMC-ADC-CORE')
            fwversiondate = alindev.sdbDrv.getFWVersionDate()
            self.logMessage("getFWVersionDate(): Date=%s"%fwversiondate,self.INFO)
        except Exception, e:
            self.logMessage("getFWVersionDate() Failed due to %s"%str(e), self.ERROR)
        return fwversiondate
