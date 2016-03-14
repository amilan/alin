 ## @package channel.py 
#    This module includes the list of common funcitons that are used in the EM 
#
#    Author = "Manolo Broseta"
#    Copyright = "Copyright 2016, ALBA"
#    Version = "1.0"
#    Email = "mbroseta@cells.es"
#    Status = "Development"
#    History:
#    27/01/2016 - file created

__author__ = "Manolo Broseta"
__copyright__ = "Copyright 2016, ALBA"
__license__ = "GPLv3 or later"
__version__ = "1.0"
__email__ = "mbroseta@cells.es"
__status__ = "Development"

from alin.drivers.spi import SpiCtrl
from alin.drivers.harmony import Harmony 
from alin.base import version
from alin.base import AlinLog

# To get mac address
from uuid import getnode as get_mac
from distutils.sysconfig import get_python_lib

__CONFIG_FILE__ = "Config"
__CONFIG_MASK__ = "MAIN_"

class GeneralClass():
    def __init__(self, parent=None):
        self._parent = parent
        
        self._hrmy_drv = None
        self._spi_drv = None
        self._display_drv = None 
        self._dev_list = self._parent.getDeviceList()

        if self._dev_list is not None and self._dev_list != []:
            for dev in self._dev_list:
                if dev['name'] == 'HARMONY': 
                    self._hrmy_drv = dev['pointer']
                elif dev['name'] == 'SPI':
                    self._spi_drv = dev['pointer']
                elif dev['name'] == 'DISPLAY':
                    self._display_drv = dev['pointer']
        
        self._log = self._parent.getLogDevice()
        
        
        self._display = self._parent.getDisplayUIClass()
        
        self._funct_list = [
                            {'command':'cbtemp',
                             'component':None,
                             'fread':self.caCBTemp,
                             'fwrite':None,
                             'default':False,
                             },
                            {'command':'fetemp',
                             'component':None,
                             'fread':self.caFETemp,
                             'fwrite':None,
                             'default':False,
                             },
                            {'command':'reset',
                             'component':'display',
                             'fread': None,
                             'fwrite': self.displayReset,
                             'default':False,
                             },
                            {'command':'state',
                             'component':'display',
                             'fread':self.displayState,
                             'fwrite':self.displaySetState,
                             'default':True,
                             },
                             {'command':'level',
                             'component':'debug',
                             'fread':self.getDebugLevel,
                             'fwrite':self.setDebugLevel,
                             'default':True,
                             },
                             {'command':'enable',
                             'component':'debug',
                             'fread':self.getDebugEnable,
                             'fwrite':self.setDebugEnable,
                             'default':True,
                             },
                            {'command':'Lenght',
                             'component':'Memory',
                             'fread':self._hrmy_drv.getMemoryMLen,
                             'fwrite':None,
                             'default':True,
                             },
                            {'command':'ActReq',
                             'component':'Memory',
                             'fread':self._hrmy_drv.getMemoryActReq,
                             'fwrite':None,
                             'default':True,
                             },
                            {'command':'SgnAct',
                             'component':'Memory',
                             'fread':self._hrmy_drv.getMemorySgnAct,
                             'fwrite':None,
                             'default':True,
                             },                            
                            ] 
        
        self._specials_list = [{'command':'idn', 
                                'fread':self.getIdetification},
                               {'command':'mac',
                                'fread':self.getMacAddress},
                               {'command':'fwver',
                                'fread':self.getFWVersion}
                               ]
                
    def getSCPIFunctionList(self):
        return self._funct_list
    
    def getSCPISpecialsList(self):
        return self._specials_list
        
    def caCBTemp(self):
        self._log.logMessage("SCPI::caFeTemp()", self._log.INFO)
        try:
            val = self._spi_drv.caCBReadTemp()
            self._log.logMessage("SCPI::caFeTemp() value=%f"%(val), self._log.INFO)
        except:
            self._log.logMessage("SCPI::caFeTemp() ERROR FOUND!!", self._log.ERROR)
            return 
        return val

    
    def caFETemp(self):
        self._log.logMessage("SCPI::caFeTemp()", self._log.INFO)
        try:
            val = self._spi_drv.feReadTemp()
            self._log.logMessage("SCPI::caFeTemp() value=%f"%(val), self._log.INFO)
        except:
            self._log.logMessage("SCPI::caFeTemp() ERROR FOUND!!", self._log.ERROR)
            return 
        return val
    
    def getFWVersion(self):
        vers = self._hrmy_drv.getFWVersion()
        self._log.logMessage("SCPI::getFWVersion() Version %s"%vers, self._log.INFO)
        return vers

    def getIdetification(self):
        # Get config File
        config_folder = get_python_lib()+"/alin/config/"
        config_file = config_folder+__CONFIG_FILE__
        
        txt = ''
        try:
            with open(config_file, 'r') as f:
                lines = f.readlines()
                f.close()
                
            comp = [ln.split(__CONFIG_MASK__)[1] for ln in lines if ln.startswith(__CONFIG_MASK__)]
            if comp != []:
                for cm in comp:
                    if cm.startswith("MANUFACTURER_") or cm.startswith("INSTRUMENT_") or cm.startswith("SERIAL_"):
                        txt += cm.split(" = ")[1] 
            
            txt = txt.replace("\n",",")
            txt += version.version()+"\n"
            #txt += "FW Version "+ self._adc_drv.getFWVersion()
        except Exception, e:
            self._log.logMessage("SCPI::getIdetification() ERROR FOUND %s"%str(e), self._log.ERROR)
            
        self._log.logMessage("SCPI::getIdetification() value=%s"%txt, self._log.INFO)
        return txt
    
    def getMacAddress(self):
        self._log.logMessage("SCPI::getMacAddress()", self._log.INFO)
        mac = format(get_mac(), 'x')
        mac_format = ':'.join([mac[i:i+2] for i,j in enumerate(mac) if not (i%2)])
        self._log.logMessage("SCPI::getMacAddress() value=%s"%mac_format, self._log.INFO)
        return mac_format
        
    def displaySetState(self, param):
        value = bool(int(param))
        self._log.logMessage("SCPI::displaySetState() to %s"%value, self._log.INFO)
        if value:
            self._display.startDisplay()
            self._log.logMessage("SCPI::displayStart() Started successfully", self._log.INFO)
        else:
            self._display.stopDisplay()
            self._log.logMessage("SCPI::displayStart() Stopped successfully", self._log.INFO)
    
    def displayReset(self, param):
        self._log.logMessage("SCPI::displayReset()", self._log.INFO)
        self._display.stopDisplay()
        self._log.logMessage("SCPI::displayStart() Stopped successfully", self._log.INFO)
        self._display.startDisplay()
        self._log.logMessage("SCPI::displayStart() Restarted successfully", self._log.INFO)
    
    def displayState(self):
        self._log.logMessage("SCPI::displayState()", self._log.INFO)
        st = self._display.getDisplayStarted()
        if st:
            msg = "Display Started"
        else:
            msg = "Display NOT Started"
        return msg
    
    def getDebugLevel(self):
        txt = ''
        
        # Get debug state for main
        txt += "MAIN = "+str(self._log.logGetLevel())+", "
        
        # Get debug level for devices
        for dev in self._dev_list:
            try:
                txt += dev['name']+" = "+str(dev['pointer'].logGetLevel())+", "
            except Exception, e:
                msg = "Error in %s due to %s"%(dev['name'],str(e))
                self._log.logMessage("SCPI::getDebugLevel() %s"%msg, self._log.ERROR)

        self._log.logMessage("SCPI::getDebugLevel() %s"%txt, self._log.INFO)
        return txt
    
    def setDebugLevel(self, param):
        el_list = param.split(",")
        if len(el_list) == 1 and "=" not in el_list[0]:
            # Apply to all
            value = int(param)
            
            # Set debug level for devices
            for dev in self._dev_list:
                try:
                    dev['pointer'].setLogLevel(value)
                except Exception, e:
                    msg = "Error in %s due to %s"%(dev['name'],str(e))
                    self._log.logMessage("SCPI::setDebugLevel() %s"%msg, self._log.ERROR)
                    
            # Set debug level for main
            self._log.logLevel(value)
        else:
            for el in range(0,len(el_list)):
                tgt_dev = el_list[el].split("=")[0]
                value = int(el_list[el].split("=")[1])
                if tgt_dev == "MAIN":
                    self._log.logLevel(value)
                else:
                    for dev in self._dev_list:
                        if tgt_dev == dev['name']:
                            try:
                                dev['pointer'].setLogLevel(value)
                            except Exception, e:
                                msg = "Error in %s due to %s"%(dev['name'],str(e))
                                self._log.logMessage("SCPI::setDebugLevel() %s"%msg, self._log.ERROR)
                        
        
        self._log.logMessage("SCPI::setDebugLevel() %s"%param, self._log.INFO)
        return self.getDebugLevel()
        
    def getDebugEnable(self):
        txt = ''

        # Get debug state for main
        aux = 'True' if self._log.logState() else 'False'
        txt += "MAIN = "+aux+", "
        
        # Get debug level for devices
        for dev in self._dev_list:
            try:
                aux = 'True' if dev['pointer'].logState() else 'False'
                txt += dev['name']+" = "+aux+", "
            except Exception, e:
                msg = "Error in %s due to %s"%(dev['name'],str(e))
                self._log.logMessage("SCPI::getDebugLevel() %s"%msg, self._log.ERROR)
                

            
        self._log.logMessage("SCPI::getDebugEnable() %s"%txt, self._log.INFO)
        return txt
    
    def setDebugEnable(self, param):
        el_list = param.split(",")
        if len(el_list)==1 and "=" not in el_list:
            value = True if param.lower() == "true" else False
            
            # Set debug state for devices
            for dev in self._dev_list:
                try:
                    dev['pointer'].setLogEnable(dbg=value)
                except Exception, e:
                    msg = "Error in %s due to %s"%(dev['name'],str(e))
                    self._log.logMessage("SCPI::setDebugEnable() %s"%msg, self._log.ERROR)
            
            # Set debug level for main
            self._log.logEnable(value)
        else:
            for el in range(0,len(el_list)):
                tgt_dev = el_list[el].split("=")[0]
                value = True if el_list[el].split("=")[1].lower() == "true" else False
                if tgt_dev == "MAIN":
                    self._log.logEnable(value)
                else:
                    for dev in self._dev_list:
                        if tgt_dev == dev['name']:
                            try:
                                dev['pointer'].setLogEnable(value)
                            except Exception, e:
                                msg = "Error in %s due to %s"%(dev['name'],str(e))
                                self._log.logMessage("SCPI::setDebugEnable() %s"%msg, self._log.ERROR)
        
        self._log.logMessage("SCPI::setDebugEnable() %s"%param, self._log.INFO)
        return self.getDebugEnable()

