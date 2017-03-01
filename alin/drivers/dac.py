## @package alinspinctrl.py 
#    File containing the device class, to control the DAC
#
#    Author = "Manuel Broseta"
#    Copyright = "Copyright 2017, ALBA"
#    Version = "1.0"
#    Email = "mbroseta@cells.es"
#    Status = "Development"
#    History:
#   26/01/2017 - file created by Manuel Broseta

__author__ = "Manuel Broseta"
__copyright__ = "Copyright 2017, ALBA"
__license__ = "GPLv3 or later"
__version__ = "1.0"
__email__ = "mbroseta@cells.es"
__status__ = "Development"

import os

from random import uniform

from alin.base import AlinDevice
from alin.base import getConfigData

_CONFIG_MASK = "DAC_"

_NUM_OF_CHANNELS = 4

class Dac(AlinDevice):
    def __init__(self, dev='EM2_DAC', debug=False):
        AlinDevice.__init__(self, device=dev, debug=debug, logger='DAC     ')        

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
        self.writeAttribute('ID_1',0x00)
        self.writeAttribute('ID_2',0x00)
        self.writeAttribute('ID_3',0x00)
        self.writeAttribute('ID_4',0x00)
        self.writeAttribute('CFG_RST',0x01)
        self.logMessage("init()...", self.DEBUG)

    def stop(self):
        self.logMessage("stop()...", self.DEBUG)
        
    def getDAC(self, channel):
        ret_value = None
        if channel < _NUM_OF_CHANNELS:
            reg_list = ['RD12_V1','RD12_V2','RD34_V3','RD34_V4']
            
            ret_value = self.readAttribute(reg_list[channel])
            self.logMessage("getDAC(): Channel %s value=%s"%(str(channel),hex(ret_value)),self.DEBUG)
        else:
            self.logMessage("getDAC(): Incorrect channel number %s"%str(channel),self.ERROR)
        
        return ret_value
        
    def setDAC(self, channel, value):
        if channel < _NUM_OF_CHANNELS:
            try:
                id_list = ['ID_1','ID_2','ID_3','ID_4']
                aux = self.readAttribute(id_list[channel])
                if aux != 0:
                    self.logMessage("setDAC(): Channel %s %s is set to %s"%(str(channel),(id_list[channel]),hex(aux)),self.WARNING)
                
                # Set the channel to write
                self.writeAttribute('CFG_WCH', channel)
                # Set te output value
                value = value & 0xFFFF
                self.writeAttribute('CFG_WVALUE', value)
                # Sets the value to the output
                self.writeAttribute('CFG_WR', 1)
                if bool(self.readAttribute('CFG_OW')):
                    self.writeAttribute('CFG_RST',0x01)
                    self.logMessage("setDAC(): At least one DAC value is lost. Reset applied!",self.ERROR)
                    return
                self.logMessage("setDAC(): Channel %s value=%s"%(str(channel),hex(value)),self.DEBUG)
            except Exception, e:
                self.logMessage("setDAC(): Unexpected error due to %s"%str(e),self.ERROR)
        else:
            self.logMessage("setDAC(): Incorrect channel number %s"%str(channel),self.ERROR)

        
   
