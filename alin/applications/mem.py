## @package psb.py 
#    File containing the driver module that controls the EEPROM devices
#
#    Author = "Manuel Broseta"
#    Copyright = "Copyright 2017, ALBA"
#    Version = "1.0"
#    Email = "mbroseta@cells.es"
#    Status = "Development"
#    History:
#              9/05/2016 - file created by Manolo Broseta


from alin.base import AlinLog
from alin.base import getConfigData

from alin.drivers.eeprom import EEPROM
from distutils.sysconfig import get_python_lib

import os
import pickle
import threading
import time

_CONFIG_MASK = "MEMORYMW_"

_NUM_CHANNELS = 4
_NUM_GPIO = 13

class MemoryMW(AlinLog):
    def __init__(self,debug=False):
        AlinLog.__init__(self, debug=False, loggerName='MEM_MW ')
        
        # Get default configuration from config file
        self._debug = debug
        self.configure()
        
        self._HRMY = None
        try:
            self._eepromdrv = EEPROM()
        except:
            self._eepromdrv = None
            
        self._eeprom_dict = {'ca1': None,
                             'ca2': None,
                             'ca3': None,
                             'ca4': None,
                             'cacb':None,
                             'feb': None,
                             'psb': self._eepromdrv,
                            }
        
        self._userData = {}
        self._userData_Dict = {}
        self._userData_Initialized = False
        
        #self.__device_folder = os.path.abspath(os.path.dirname(__file__))+"/deviceslib/"
        self._userData_folder = get_python_lib()+"/alin/config/"
        self._userData_file = self._userData_folder + "userdata"
        
        self.logMessage("__init__() Initialized ", self.DEBUG)
        
    def configure(self):
        # Get default configuration from config file
        configDict = getConfigData(_CONFIG_MASK)
        self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else self._debug
        self._debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 20
        
        # Logging
        self.logLevel(self._debuglevel)
        self.logEnable(self._debug)
        
        self.logMessage("configure() %s configured"%_CONFIG_MASK, self.INFO)
        

    def reconfigure(self):
        self.logMessage("reconfigure(): reconfiguring applications and associted devices", self.INFO)
                
        # reconfigure Applications
        self.configure()
        
        # reconfigure devices
        if self._eepromdrv is not None:
            self._eepromdrv.configure()
        
        self.logMessage("reconfigure(): Done!!", self.INFO)

    def start(self):
        self.logMessage("start() Start EEPROM control....",self.INFO)
        
        # Initialize EEPROM
        if self._eepromdrv is not None:
            self._eepromdrv.init()
        
    def stop(self):
        self.logMessage("stop() Stop EEPROM control....",self.INFO)
        pass
        
    def shareApplications(self, applications):
        self.logMessage("shareApplications(): Getting needed applications layers", self.INFO)

        self._HRMY = applications['HARMONY']['pointer']
        self._DIAGS = applications['DIAGNOSTICS']['pointer']
        self._PSB = applications['PSB']['pointer']

        for key in self._eeprom_dict.keys():
            if key.lower() != "psb":
                self._eeprom_dict[key] = self._HRMY._dSPI
                
        # Test function TBD in future.
        self.getAllManufacturers()
        
        self.initializeUserData()

    def initializeUserData(self):
        self._userData_Initialized = False
        
        self._userData = {'range': (self._HRMY.setRange, None),
                          'filter': (self._HRMY.setFilter, None),
                          'trigmode': (self._HRMY.setTrigMode, None),
                          'trigpol': (self._HRMY.setTrigPol, None),
                          'acqtime': (self._HRMY.setAcqTime, None),
                          'acqntriggers': (self._HRMY.setAcqNTriggers, None),
                          'trigdelay': (self._HRMY.setTrigDelay, None),
                          'triginput': (self._HRMY.setTrigInput, None),
                          'gpioconfig': (self._HRMY.setGPIOConfig, _NUM_GPIO),
                          'gpiovalue': (self._HRMY.setGPIOValue, _NUM_GPIO),
                          'supplyport': (self._HRMY.setSupplyPort, _NUM_CHANNELS),
                          'cafilter': (self._HRMY.caSetFilter, _NUM_CHANNELS),
                          'capostfilter': (self._HRMY.caSetPostFilter, _NUM_CHANNELS),
                          'caprefilter': (self._HRMY.caSetPreFilter, _NUM_CHANNELS),
                          'cainversion': (self._HRMY.caSetInversion, _NUM_CHANNELS),
                          'carange': (self._HRMY.caSetRange, _NUM_CHANNELS),
                          'cavgain': (self._HRMY.caSetVGain, _NUM_CHANNELS),
                          'catigain': (self._HRMY.caSetTIGain, _NUM_CHANNELS),
                          'caoffset': (self._HRMY.caSetOffset, _NUM_CHANNELS),
                          'casaturationmax': (self._HRMY.caSetSaturationMax, _NUM_CHANNELS),
                          'casaturationmin': (self._HRMY.caSetSaturationMin, _NUM_CHANNELS),
                          'vanalog': (self._HRMY.setVAnalog, _NUM_CHANNELS),
                          'dacgain': (self._HRMY.setDACGain, None),
                          'fvmaximumlimit': (self._DIAGS.setFVMaximumLimit, None),
                          'fvminimumlimit': (self._DIAGS.setFVMinimumLimit, None),
                          'resetfv': (self._DIAGS.resetFV, None),
                          'psbiso': (self._PSB.setISO , None),
                          'psbvcc': (self._PSB.setVCC , None),
                          'psbvs': (self._PSB.setVS , None),
                          'psbvaux': (self._PSB.setVAUX , None),
                         }
        
        if not os.path.isfile(self._userData_file):
            self._userData_Dict = {}
            self.logMessage("initializeUserArray:: user data file NOT found!!", self.WARNING)
        else:
            self.logMessage("initializeUserArray:: user data file found!!", self.INFO)
        
            with open(self._userData_file) as output:
                self._userData_Dict = pickle.load(output)
                
            for key in self._userData_Dict.keys():
                if key in self._userData.keys():
                    callback_func = self._userData[key][0]
                    num_channels = self._userData[key][1]
                    if num_channels is not None:
                        for channel in self._userData_Dict[key].keys():
                            callback_func(channel, self._userData_Dict[key][channel])
                    else:
                        callback_func(self._userData_Dict[key])
                    
        self._userData_Initialized = True
        
    def saveUserData(self, item=None, idx=None, data=None):
        if self._userData_Initialized and item is not None:
            self.logMessage("saveUserData:: saving user %s data"%item, self.DEBUG)
            
            if item in self._userData.keys():
                callback_func = self._userData[item][0]
                num_channels = self._userData[item][1]
                if num_channels is not None:
                    if item not in self._userData_Dict.keys():
                        self._userData_Dict[item] = {}
                    self._userData_Dict[item][idx] = data
                else:
                    self._userData_Dict[item] = data
            
                # Write output to file
                try:
                    with open(self._userData_file,"w") as f:
                        pickle.dump(self._userData_Dict, f)
                except Exception, e:
                    self.logMessage("saveUserData:: Error saving user data file due to %s"%str(e), self.ERROR)
                    return None

                self.logMessage("saveUserData:: Data %s saved succesfulley"%str(item).upper(), self.INFO)
            else:
                self.logMessage("saveUserData:: invalid key %s "%str(item), self.ERROR)
                
        
    
    def write(self, device='', address=0, data=[]):
        self.logMessage("write(): Writting data to %s"%device, self.INFO)
        try: 
            if device.lower() in self._eeprom_dict.keys() and self._eeprom_dict[device.lower()] is not None:
                if len(data) > 0:
                    if device.lower() != 'psb':
                        self._eeprom_dict[device.lower()].eempromWrite(device.lower(), address, data)
                    else:
                        self._eeprom_dict[device.lower()].writeAddress(address, data)
                else:
                    self.logMessage("write(): Incorrect data size", self.ERROR)            
            else:
                self.logMessage("write(): Incorrect device name %s"%(device), self.ERROR)
        except Exception, e:
            self.logMessage("write(): Unexpected error due to %s"%str(e), self.ERROR)
        
    def read(self, device='', address=0, num_bytes=0):
        self.logMessage("read(): Reading data from %s"%device, self.DEBUG)
        ret_value = False
        try:
            if device.lower() in self._eeprom_dict.keys() and self._eeprom_dict[device.lower()] is not None:
                if num_bytes > 0:
                    if device.lower() != 'psb':
                        ret_value = self._eeprom_dict[device.lower()].eempromRead(device.lower(), address, num_bytes)
                    else:
                        ret_value = self._eeprom_dict[device.lower()].readAddress(address, num_bytes)
                        
                    self.logMessage("read(): Read value=%s"%str(', '.join(map(hex, ret_value))), self.DEBUG)
                else:
                    self.logMessage("read(): Incorrect data size", self.ERROR)            
            else:
                self.logMessage("read(): Incorrect device name %s"%(device), self.ERROR)        
        except Exception, e:
            self.logMessage("read(): Unexpected error due to %s"%str(e), self.ERROR)
            
        return ret_value
    
    def factoryReset(self):
        try:
            os.remove(self._userData_file)
        except:
            self.logMessage("factoryReset(): User data file doesn't exits.", self.WARNING)
    
    # This is a test function. ToBeDeleted
    def getAllManufacturers(self):
        for key in self._eeprom_dict.keys():
            address = 0xFA
            num_bytes = 6
            self.read(key, address, num_bytes)
        