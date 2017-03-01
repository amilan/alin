## @package average.py 
#    File containing the device class, to control the Average
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

_CONFIG_MASK = "AVERAGE_"

class Average(AlinDevice):
    def __init__(self, dev='WB-HRMY-AVERAGE', number=0, debug=False):
        AlinDevice.__init__(self, device=dev, number=number, debug=debug, logger='AVG_'+str(number)+'  ')

        # Get default configuration from config file
        self._debug = debug
        self._device = dev
        self._devnumber = number
        self.configure()        

        self.logMessage("__init__() Initialized ", self.DEBUG)
        
    def configure(self):
        # Get default configuration from config file
        configDict = getConfigData(_CONFIG_MASK)
        self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else self._debug
        self._debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 40
        self._device = configDict["DEVICE_"] if "DEVICE_" in configDict.keys() else self._device
        
        self.setDevice(devname=self._device, devnum=self._devnumber)
        
        # Logging
        self.logLevel(self._debuglevel)
        self.logEnable(self._debug)
        
        self.logMessage("configure() %s configured"%_CONFIG_MASK, self.INFO)

    def init(self):
        #Configuration of memory block
        self.logMessage("init(): Configuration of Average block", self.INFO)
        
        try:
            self.writeAttribute('AVG_CTL_ENA', 0x00)
            self.writeAttribute('AVG_CTL_PRE_DIV', 0x00)
            self.writeAttribute('ID_CFG_ID_IN', 0x00)
            self.writeAttribute('ID_CFG_ID_IP', 0x00)
            self.writeAttribute('ID_CFG_ID_OUT', 0x00)
            
        except Exception, e:
            self.logMessage("init() Not possible due to: %s"%str(e),self.ERROR) 
