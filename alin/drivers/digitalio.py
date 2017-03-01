## @package average.py 
#    File containing the device class, to control the digital IO
#
#    Author = "Manuel Broseta"
#    Copyright = "Copyright 2016, ALBA"
#    Version = "1.0"
#    Email = "mbroseta@cells.es"
#    Status = "Development"
#    History:
#   25/05/2016 - file created by Manuel Broseta

__author__ = "Manuel Broseta"
__copyright__ = "Copyright 2016, ALBA"
__license__ = "GPLv3 or later"
__version__ = "1.0"
__email__ = "mbroseta@cells.es"
__status__ = "Development"

import os

from alin.base import AlinDevice
from alin.base import getConfigData

_CONFIG_MASK = "DIGITALIO_"

class DigitalIO(AlinDevice):
    def __init__(self, dev='WB-EM2-DIGITAL_IO', debug=False):
        AlinDevice.__init__(self, device=dev, debug=debug, logger='DIG_IO ')        

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
        #Configuration of memory block
        self.logMessage("init(): Configuration of Digital block", self.INFO)
        
        try:
            self.writeAttribute('CNT1_STP_OUT_ID', 0x00)
            self.writeAttribute('CNT1_STP_SRC_ID', 0x00)
            self.writeAttribute('CNT1_STP_SIG', 0x00)
            self.writeAttribute('CNT1_STP_TRIG', 0x00)
            self.writeAttribute('CNT1_STP_SRC', 0x00)
            self.writeAttribute('CNT1_V_CNT_V', 0x00)                
            self.writeAttribute('TRG1_V_CNT_V', 0x00)
            self.writeAttribute('DIS_STP_DIS1_ID', 0x00)
            self.writeAttribute('CNT1_STP_DIS', 0x00)
            self.writeAttribute('DIS_STP_DIS1_M', 0x00)
            self.writeAttribute('DIS_STP_WD1', 0x00)
            self.writeAttribute('CNT0_STP_OUT_ID', 0x00)
            self.writeAttribute('CNT0_STP_SRC_ID', 0x00)
            self.writeAttribute('CNT0_STP_SIG', 0x00)
            self.writeAttribute('CNT0_STP_DIS', 0x00)
            self.writeAttribute('CNT0_STP_TRIG', 0x00)
            self.writeAttribute('CNT0_STP_SRC', 0x00)
            self.writeAttribute('TRG0_V_CNT_V', 0x00)
            self.writeAttribute('CNT0_V_CNT_V', 0x00)
        except Exception, e:
            self.logMessage("init() Not possible due to: %s"%str(e),self.ERROR)            
    
