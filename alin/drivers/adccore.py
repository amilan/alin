## @package alinspinctrl.py 
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

import os

from random import uniform

from alin.base import AlinDevice
from alin.base import getConfigData

_CONFIG_MASK = "ADCCORE_"

_OVERSAMPLING_RATES = [1, 2, 4, 8, 16, 32, 64, 0]

_5V_RANGE_VALUE = 5
_10V_RANGE_VALUE = 10

class AdcCore(AlinDevice):
    def __init__(self, dev='WB-FMC-ADC-CORE', debug=False):
        AlinDevice.__init__(self, device=dev, debug=debug, logger='ADC_CORE')        

        # Get default configuration from config file
        self._debug = debug
        self._device = dev
        self.configure()
        
        self.logMessage("__init__() Initialized ", self.DEBUG)

    def configure(self):
        # Get default configuration from config file
        configDict = getConfigData(_CONFIG_MASK)
        self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else self._debug
        self._debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 40
        self._device = configDict["DEVICE_"] if "DEVICE_" in configDict.keys() else self._device

        self.setDevice(devname=self._device)
        
        # Logging
        self.logLevel(self._debuglevel)
        self.logEnable(self._debug)
        
        self.logMessage("configure() %s configured"%_CONFIG_MASK, self.INFO)        

    def init(self):
        self.writeAttribute('CTL_ADQ_M', 0x00)
        self.writeAttribute('CTL_RANGE', 0x01)
        self.writeAttribute('CTL_ADC_OS',0x06)
        self.writeAttribute('CTL_DBL_RATE',0x00)
        self.writeAttribute('ID_CH1_ID',0x00)
        self.writeAttribute('ID_CH2_ID',0x00)
        self.writeAttribute('ID_CH3_ID',0x00)
        self.writeAttribute('ID_CH4_ID',0x00)
        self.logMessage("init()...", self.DEBUG)
        
        self._voltrange = None
        self._dblrate = None

    def stop(self):
        self.writeAttribute('CTL_ADQ_M',0x01)
        self.logMessage("stopAdc()...", self.DEBUG)

    def getAdcRunState(self):
        readch = self.readAttribute('CTL_ADQ_M')
        if readch != 0:
            val = True
        else:
            val = False
        self.logMessage("getAdcRunState(): ADC run=%s"%val, self.DEBUG)
        return val
    
    def setOversamplig(self, ovsamp=0):
        if ovsamp<len(self.oversampling_rate):
            
            attr = self.device.getAttributeInfo('CTL_ADC_OS')
            if attr is not None and attr != {}:
                range = (2**attr['size']-1)
                if ovsamp>range:
                    self.logMessage("setOversamplig(): Value out of range => %s."%ovsamp, self.DEBUG)
                    return
                
                self.device.writeAttribute('CTL_ADC_OS',ovsamp)
                self.logMessage("setOversamplig(): Oversampling set to %s."%str(ovsamp), self.DEBUG)
            else:
                self.logMessage("setOversamplig(): Failed to read attribute info...", self.ERROR)
        else:
            self.logMessage("setOversamplig(): OS value exceeds limit", self.ERROR)

    def getOversampling(self):
        readch = _OVERSAMPLING_RATES[self.readAttribute('CTL_ADC_OS')]
        self.logMessage("getOversampling(): Oversampling read=%s"%str(readch), self.DEBUG)
        return readch
    
    def getInstantVoltage(self, ch):
        readch = self.convertADCToVoltage(self.readAttribute(ch))
        self.logMessage("getInstantCurrent=%s value=%s"%(str(ch),str(readch)), self.DEBUG)
        return readch

    def writeRegister(self, register, value):
        self.logMessage("writeRegister(): Register %s value=%s"%(str(register),str(value)),self.DEBUG)
        if register == 'CTL_RANGE':
            self._voltrange = value
        elif register == 'CTL_DBL_RATE':
            self._dblrate = value
        self.writeAttribute(register,value)
    
    def readRegister(self, register):
        value = self.readAttribute(register)
        if register == 'CTL_RANGE':
            self._voltrange = value
        elif register == 'CTL_DBL_RATE':
            self._dblrate = value
        self.logMessage("readRegister(): Register %s read value=%s"%(str(register),str(value)),self.DEBUG)
        return value
    
    def getMinSampleAcqTime(self):
        # Time reference used in miliseconds
        ossval = self.getOversampling()
        value = ossval * 5e-3
        return value
    
    def convertADCToVoltage(self, value):
        try: 
            if self._voltrange is None:
                self._voltrange = self.readRegister('CTL_RANGE')
            adc_range = _10V_RANGE_VALUE if self._voltrange==True else _5V_RANGE_VALUE

            if value>0x7fffffff:
                value-=0x100000000
            value = value*adc_range/2**17.
                
        except Exception, e:
            self._parent.logMessage("convertADCToVoltage() Error calculating voltage due to %s"%str(e),self._parent.ERROR)
            value = 0
            
            
        return value

