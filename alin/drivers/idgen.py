## @package idgen.py 
#    File containing the device class, to control the ADC
#
#    Author = "Manuel Broseta"
#    Copyright = "Copyright 2016, ALBA"
#    Version = "1.0"
#    Email = "mbroseta@cells.es"
#    Status = "Development"
#    History:
#   27/01/2016 - file created by Manuel Broseta

__author__ = "Manuel Broseta"
__copyright__ = "Copyright 2016, ALBA"
__license__ = "GPLv3 or later"
__version__ = "1.0"
__email__ = "mbroseta@cells.es"
__status__ = "Development"


from alin.base import AlinDevice
from alin.base import AlinLog
from alin.base import getConfigData
import os
from random import uniform
import threading
import time

_CONFIG_MASK = "IDGEN_"

# Supported data types
_CHANNEL_1_TYPE = 0
_CHANNEL_2_TYPE = 1
_CHANNEL_3_TYPE = 2
_CHANNEL_4_TYPE = 3
_N_TYPES_SUPPORTED = 4 # last +1

# Defualt ID for supported data types    
_DEFAULT_CHANNEL_1_ID = 0x01
_DEFAULT_CHANNEL_2_ID = 0x02
_DEFAULT_CHANNEL_3_ID = 0x03
_DEFAULT_CHANNEL_4_ID = 0x04

class IDGen(AlinDevice):
    def __init__(self, dev='WB-HRMY-ID-GEN', debug=False):
        AlinDevice.__init__(self, device=dev, debug=debug, logger='IDGEN  ')
        
        # Get default configuration from config file
        self._debug = debug
        self._device = dev
        self.configure()               
        
        self._idgen_mngthread = [None for x in range(0,4)]
        
        # Logging
        self.setLogLevel(self._debuglevel)
        self.logEnable(self._debug)
        
        self.logMessage("__init__() Initialized ", self.DEBUG)

    def configure(self):
        # Get default configuration from config file
        configDict = getConfigData(_CONFIG_MASK)
        self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else self._debug
        self._debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 40
        self._device = configDict["DEVICE_"] if "DEVICE_" in configDict.keys() else self._device
        self._ch1ID = int(configDict["CHANNEL_1_ID_"]) if "CHANNEL_1_ID_" in configDict.keys() else _DEFAULT_CHANNEL_1_ID
        self._ch2ID = int(configDict["CHANNEL_2_ID_"]) if "CHANNEL_2_ID_" in configDict.keys() else _DEFAULT_CHANNEL_2_ID
        self._ch3ID = int(configDict["CHANNEL_3_ID_"]) if "CHANNEL_3_ID_" in configDict.keys() else _DEFAULT_CHANNEL_3_ID
        self._ch4ID = int(configDict["CHANNEL_4_ID_"]) if "CHANNEL_4_ID_" in configDict.keys() else _DEFAULT_CHANNEL_4_ID        

        self.setDevice(devname=self._device)
        
        # Logging
        self.logLevel(self._debuglevel)
        self.logEnable(self._debug)
        
        self.logMessage("configure() %s configured"%_CONFIG_MASK, self.INFO)                

    def init(self):
        #Configuration of memory block
        self.logMessage("init(): Configuration of ID Gen block", self.INFO)
        
        try:
            # Each time this ID is received a message is generated in Harmony BUS
            self.writeAttribute('ID_gen_ctl_TriggerID',0x51)
            # Sends the Data Message when it is set.
            self.writeAttribute('ID_gen_ctl_mTrig',0)
            # If it is set to 1, the data mesage is send in Harmony bus each time
            # a Trigger ID is received.
            self.writeAttribute('ID_gen_ctl_ETI',0)
            # If it is set to 1, the mesage's timestamp is internally generated.
            self.writeAttribute('ID_gen_ctl_CLKE',0)
            # This bit indicates that data is still not send to the Harmony Bus
            # and an error can be generated if a new data request is generated.
            self.readAttribute('ID_gen_ctl_RDY')
        except Exception, e:
            self.logMessage("init() Not possible due to: %s"%str(e),self.ERROR)
            
        
    def generateIDGenData(self, datatype=None, data=0, ts=0):
        self.logMessage("generateIDGenData():Generating datatype=%s with data=%s and timestamp=%s"%(str(datatype), str(data), str(ts)), self.INFO)
        try:
            iddata = self.getID(datatype)
            if iddata is not None:
                self.writeAttribute('TS_ID_ID_OUT',iddata)
                self.writeAttribute('TS_ID_TimeStamp',ts)
                self.writeAttribute('DATA_GEN_DATA',data)
                self.writeAttribute('ID_gen_ctl_mTrig', 1)
            else:
                self.logMessage("generateIDGenData() Unsupported data type %s"%str(datatype),self.ERROR)
                return False
        except Exception, e:
            self.logMessage("generateIDGenData() Not possible due to: %s"%str(e),self.ERROR)
            return False
        
        return True
    
    def getID(self, datatype):
        if datatype is not None and datatype < _N_TYPES_SUPPORTED:
            if datatype == _CHANNEL_1_TYPE:
                return self._ch1ID
            elif datatype == _CHANNEL_2_TYPE:
                return self._ch2ID
            elif datatype == _CHANNEL_3_TYPE:
                return self._ch3ID
            elif datatype == _CHANNEL_4_TYPE:
                return self._ch4ID
            else:
                return None
        return None

    def startIDGenManagement(self, channel, range=100, time=1):
        self.logMessage("startIDGenManagement() Starting ID Gen thread %s channel...."%str(channel),self.INFO)
        
        if self._idgen_mngthread[channel] is not None:
            self.stopIDGenManagement(channel)

        try:
            acq_time = (time/range)
            self._idgen_mngthread[channel] = IDGenManagementThread(self,channel=channel, points=range, time=acq_time)
            self._idgen_mngthread[channel].start()
            self.logMessage("startIDGenManagement() Thread started every %s secs with a range of %s samples"%(str(time),str(range)),self.INFO)
        except Exception, e:
            self.logMessage("startIDGenManagement() Not possible to start thread due to: %s"%str(e),self.ERROR)
        
    def stopIDGenManagement(self, channel):
        self.logMessage("stopIDGenManagement() Stopping thread....",self.INFO)
        if self._idgen_mngthread[channel] is not None:
            self._idgen_mngthread[channel].end()
            
            while not self._idgen_mngthread[channel].getProcessEnded():
                print "Waiting to finish process"
                time.sleep(0.5)
                
            self._idgen_mngthread[channel] = None
        
        self.logMessage("stopIDGenManagement() Thread stop", self.INFO)

    def getIDGenManagement(self, channel):
        self.logMessage("getIDGenManagement() Channel %s "%str(channel),self.INFO)
        if self._idgen_mngthread[channel] is not None and self._idgen_mngthread[channel].getProcessEnded() == False:
            retval = True
        else:
            retval = False
        self.logMessage("getIDGenManagement() Thread alive=%s"%str(retval), self.INFO)
        return retval

    def writeRegister(self, register, value):
        self.logMessage("writeRegister(): Register %s value=%s"%(str(register),str(value)),self.DEBUG)
        self.writeAttribute(register,value)
    
    def readRegister(self, register):
        value = self.readAttribute(register)
        self.logMessage("readRegister(): Register %s read value=%s"%(str(register),str(value)),self.DEBUG)
        return value        

class IDGenManagementThread(threading.Thread):
    def __init__(self, parent=None, time=1, channel=None, points=1):
        threading.Thread.__init__(self)
        self._parent = parent
        
        self._time = time
        self._channel = channel
        self._npoints = points
        
        self._endProcess = False
        self._processEnded = False
    
    def end(self):
        self._endProcess = True
        
    def getProcessEnded(self):
        return self._processEnded

    def run(self): 
        #while not (self._endProcess):
        if self._channel is not None:
            for i in range(0, self._npoints):
                ts = i*1024
                if self._channel == 0: # Channel 1
                    tmp = uniform(-1,1)
                if self._channel == 1: # Channel 2
                    tmp = uniform(-5,5)
                if self._channel == 2: # Channel 3
                    tmp = uniform(-10,10)
                if self._channel == 3: # Channel 4
                    tmp = uniform(-100,100)
                if tmp<0:
                    value = (0x100000000-int((round(tmp,6)*131072)/10))
                else:
                    value = int((round(tmp,6)*131072)/10)
                self._parent.generateIDGenData(self._channel, value, ts)
            time.sleep(self._time)
        self._processEnded = True
