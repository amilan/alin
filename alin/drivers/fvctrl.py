## @package memory.py 
#    File containing the device class, to control the Flying voltage
#
#    Author = "Manuel Broseta"
#    Copyright = "Copyright 2016, ALBA"
#    Version = "1.0"
#    Email = "mbroseta@cells.es"
#    Status = "Development"
#    History:
#   20/01/2017 - file created by Manuel Broseta

__author__ = "Manuel Broseta"
__copyright__ = "Copyright 2016, ALBA"
__license__ = "GPLv3 or later"
__version__ = "1.0"
__email__ = "mbroseta@cells.es"
__status__ = "Development"


from alin.base import AlinDevice
from alin.base import getConfigData
import os
import threading
import time

import csv

_CONFIG_MASK = "FVCTRL_"

_LOOP_TIME = 2
_HV_LED_STATUS = 1

class FVCtrl(AlinDevice):
    def __init__(self, dev='WB-FMC-FV-CONTROL', debug=False):
        AlinDevice.__init__(self, device=dev, debug=debug, logger='FV_CTRL')

        # Get default configuration from config file
        self._debug = debug
        self._device = dev
        self.configure()
        
        self._fvctrl_thread = None
        self._fvctrl_maximum = 0 
        self._fvctrl_minimum = 0 
        
        self.logMessage("__init__() Initialized ", self.DEBUG)
        

    def configure(self):
        # Get default configuration from config file
        configDict = getConfigData(_CONFIG_MASK)
        self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else self._debug
        self._debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 40
        self._device = configDict["DEVICE_"] if "DEVICE_" in configDict.keys() else self._device
        self._loop_time = int(configDict["LOOPTIME_"]) if "LOOPTIME_" in configDict.keys() else _LOOP_TIME          

        self.setDevice(devname=self._device)
        
        # Logging
        self.logLevel(self._debuglevel)
        self.logEnable(self._debug)
        
        self.logMessage("configure() %s configured"%_CONFIG_MASK, self.INFO)                

    def init(self):
        #Configuration of memory block
        self.logMessage("start(): Configuration of flying voltage block", self.INFO)
        
        # Initializes limits
        self.setMaximumLimit(100)
        self.setMinimumLimit(-100)
        self.resetFV()        

        try:
            self._fvctrl_thread = None
            self._fvctrl_thread = FlyingVoltageThread(self, debug=self._debug, wtime=self._loop_time)
            self._fvctrl_thread.setDaemon(True)
            
            self._fvctrl_thread.start()
            self.logMessage("start() Flying Voltage thread started",self.DEBUG)

        except Exception, e:
            self.logMessage("start() Not possible due to: %s"%str(e),self.ERROR)
            
    def stop(self):
        self.logMessage("stop() Stopping Flying Voltage thread....",self.DEBUG)
        if self._fvctrl_thread is not None:
            self._fvctrl_thread.end()
        
        while not self._fvctrl_thread.getProcessEnded():
            self.logMessage("stop(): Waiting process to die", self.DEBUG)
            time.sleep(0.5)
            pass  
        
        self.logMessage("stop() Flying Voltage Thread stopped", self.DEBUG)
            
    def resetFV(self):
        self._fvctrl_maximum = 0 
        self._fvctrl_minimum = 0 

    def getInstantVoltage(self):
        ret_value = None
        if self._fvctrl_thread is not None:
            ret_value = self.calculateVoltage(self._fvctrl_thread.getValue('FV_INSTANT'))
            self.logMessage("getInstantVoltage(): FV instant read=%s"%str(ret_value), self.DEBUG)
        return ret_value
    
    def getAverageVoltage(self):
        ret_value = None
        if self._fvctrl_thread is not None:
            ret_value = self.calculateVoltage(self._fvctrl_thread.getValue('FV_AVERAGE'))
            self.logMessage("getAverageVoltage(): FV average read=%s"%str(ret_value), self.DEBUG)
        return ret_value

    def getMaximumVoltage(self):
        ret_value = 0
        if self._fvctrl_thread is not None:
            ret_value = self.calculateVoltage(self._fvctrl_thread.getValue('FV_MAXIMUM'))
            self.logMessage("getMaximumVoltage(): FV maximum read=%s"%str(ret_value), self.INFO)
            
        if ret_value > self._fvctrl_maximum:
            self._fvctrl_maximum = int(ret_value)
        self.logMessage("getMaximumVoltage(): FV maximum returned=%s"%str(ret_value), self.INFO)
        return self._fvctrl_maximum

    def getMinimumVoltage(self):
        ret_value = 0
        if self._fvctrl_thread is not None:
            ret_value = self.calculateVoltage(self._fvctrl_thread.getValue('FV_MINIMUM'))
            self.logMessage("getMinimumVoltage(): FV minimum read=%s"%str(ret_value), self.DEBUG)
            
        if ret_value < self._fvctrl_minimum:
            self._fvctrl_minimum = int(ret_value)
        self.logMessage("getMinimumVoltage(): FV minimum returned=%s"%str(ret_value), self.DEBUG)
        return self._fvctrl_minimum    
    
    def getLEDStatus(self):
        ret_value = int(self.readAttribute('CTRL_STA_LED'))
        self.logMessage("getLEDStatus(): LED Value=%s"%str(ret_value), self.DEBUG)
        return ret_value
    
    def getHVState(self):
        ret_value = False
        if self.getLEDStatus() > _HV_LED_STATUS:
            ret_value = True        
        self.logMessage("getHVState(): HV State=%s"%str(ret_value), self.DEBUG)
        return ret_value
    
    def getRelay(self):
        ret_value = int(self.readAttribute('CTRL_STA_RELAY'))
        self.logMessage("getRelay(): Relay Value=%s"%str(ret_value), self.DEBUG)
        return ret_value

    def setRelay(self, value):
        value = value  & 0x01
        self.writeAttribute('CTRL_STA_RELAY', value)
        self.logMessage("setRelay(): Relay set to Value=%s"%str(value), self.DEBUG)
        
    def setMaximumLimit(self, value):
        try:
            max_value = int(self.calculateValue(value))
            self.writeAttribute('LIM_MAX', max_value)
            self.logMessage("setMaximumLimit(): Max Limit=%s"%str(max_value), self.DEBUG)
        except:
            self.logMessage("setMaximumLimit(): Error setting Maximum Limit!!!!!", self.ERROR)

    def getMaximumLimit(self):
        ret_value = None
        try:
            max_value = int(self.readAttribute('LIM_MAX'))
            ret_value = self.calculateVoltage(max_value)
            self.logMessage("getMaximumLimit(): Max Limit=%s"%str(max_value), self.DEBUG)
        except:
            self.logMessage("getMaximumLimit(): Error getting Maximum Limit!!!!!", self.ERROR)
        return ret_value

    def setMinimumLimit(self, value):
        try:
            min_value = int(self.calculateValue(value))
            self.writeAttribute('LIM_MIN', min_value)
            self.logMessage("setMinimumLimit(): Min Limit=%s"%str(min_value), self.DEBUG)
        except:
            self.logMessage("setMinimumLimit(): Error setting Minimum Limit!!!!!", self.ERROR)

    def getMinimumLimit(self):
        ret_value = None
        try:
            min_value = int(self.readAttribute('LIM_MIN'))
            ret_value = self.calculateVoltage(min_value)
            self.logMessage("getMinimumLimit(): Min Limit=%s"%str(min_value), self.DEBUG)
        except:
            self.logMessage("getMinimumLimit(): Error getting Minimum Limit!!!!!", self.ERROR)
        return ret_value

    def calculateVoltage(self,value):
        try:
            volt = 2.5*(1001*value/1024.-500)
        except:
            volt = 0
        return volt           
    
    def calculateValue(self, volt):
        try:
            value = (1024/1001.)*(volt/2.5+500)
        except:
            value = 0
        return value    

        
class FlyingVoltageThread(threading.Thread):
    def __init__(self, parent=None, debug=None, wtime=1):
        threading.Thread.__init__(self)
        self._parent = parent
        
        self._waittime = wtime
        
        self._endProcess = False
        self._processEnded = False
        
        self._acqdata_semaphore = False
        
        self._fv_data = {'FV_INSTANT':{'read_mode':0,'value':None},
                         'FV_AVERAGE':{'read_mode':3,'value':None},
                         'FV_MAXIMUM':{'read_mode':1,'value':None},
                         'FV_MINIMUM':{'read_mode':2,'value':None},
                        }
        
    def end(self):
        self._parent.logMessage("stopMemoryManagement() Stopping Acquisition thread....",self._parent.INFO)
        self._endProcess = True
        
    def getProcessEnded(self):
        return self._processEnded
    
        
    def setAcqSemaphore(self, value):
        self._acqdata_semaphore = value
        
    def getValue(self, reg=None):
        ret_value = None
        if reg is not None:
            ret_value = self._fv_data[reg]['value']
        return ret_value
            
    def run(self): 
        while not (self._endProcess):
            for key in self._fv_data.keys():
                self._parent.writeAttribute('CTRL_STA_READ_MODE', self._fv_data[key]['read_mode'])
                val = self._parent.readAttribute('CTRL_STA_FV')
                self._fv_data[key]['value'] = val
            time.sleep(self._waittime)

        self._processEnded = True        

