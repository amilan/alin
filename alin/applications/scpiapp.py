 ## @package main.py 
#    Main control module for the Electrometer
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


from alin.base import getConfigData
from alin.base import AlinLog
from alin.base import version

import os
import threading
import scpi
import sys
import time

# To get mac address
from uuid import getnode as get_mac

_CONFIG_MASK = "SCPI_"

_DEFAULT_SCPI_PORT = 5025
_DEFAULT_SCPI_AUTOOPEN = True
_DEFAULT_SCPI_LOCAL = False

_NUMBER_OF_CHANNELS  = 4
_NUMBER_OF_GPIO  = 13
_NUMBER_OF_SUPPLY  = 4

class ScpiApp():
    def __init__(self, debug=False, parent=None):
        # Logging
        self._log = AlinLog(debug=debug, loggerName='SCPI_APP')
        self._drvlog = AlinLog(debug=debug, loggerName='SCPI')
        
        # Get default configuration from config file
        self._debug = debug
        self.configure()
        
        self._scpiObj = None
        
        idn = self.getIdetification()
        mac = self.getMacAddress()
        self._log.logMessage("__init__(): MAC = %s"%mac, self._log.INFO)
        self._log.logMessage("__init__(): IDN = %s"%idn, self._log.INFO)
        
    def configure(self):
        # Get default configuration from config file
        configDict = getConfigData(_CONFIG_MASK)
        
        # Get default configuration from config file
        configDict = getConfigData(_CONFIG_MASK)
        self._scpiport = int(configDict["PORT_"]) if "PORT_" in configDict.keys() else _DEFAULT_SCPI_PORT
        self._scpiautoopen = bool(int(configDict["AUTOOPEN_"])) if "AUTOOPEN_" in configDict.keys() else _DEFAULT_SCPI_AUTOOPEN
        self._scpilocal = bool(int(configDict["LOCAL_"])) if "LOCAL_" in configDict.keys() else _DEFAULT_SCPI_LOCAL
        self._scpi_debug = bool(int(configDict["DEBUG_"])) if "DEBUG_" in configDict.keys() else False
        self._scpi_debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 40
        self._scpi_drvdebuglevel = int(configDict["DRV_DEBUGLEVEL_"]) if "DRV_DEBUGLEVEL_" in configDict.keys() else 40
        
        # Logging
        self._log.logLevel(self._scpi_debuglevel)
        self._log.logEnable(self._scpi_debug)

        self._drvlog.logLevel(self._scpi_drvdebuglevel)
        self._drvlog.logEnable(self._scpi_debug)
        
        self._log.logMessage("configure() %s configured"%_CONFIG_MASK, self._log.INFO)
        
    def reconfigure(self):
        self._log.logMessage("reconfigure(): reconfiguring applications and associted devices", self._log.INFO)
                
        # reconfigure Applications
        self.configure()
        
    def shareApplications(self, applications):
        self._log.logMessage("shareApplications(): Getting needed applications layers", self._log.INFO)
        
        self._DIAGS = applications['DIAGNOSTICS']['pointer']
        self._PSB = applications['PSB']['pointer']
        self._HARMONY = applications['HARMONY']['pointer']
        self._MEMMW = applications['MEMORY_APP']['pointer']
        
    def start(self):        
        self._log.logMessage("start()....",self._log.INFO)
        
        self._channel_funct_list = [
                                    # GENERAL COMMANDS
                                    {'command':'AVGCurrent',
                                     'component':None,
                                     'fread':self._HARMONY.getSCPIAverageCurrent,
                                     'fwrite':None,
                                     'default':False,
                                    },
                                    {'command':'CURRent',
                                     'component':None,
                                     'fread':self._HARMONY.getSCPICurrent,
                                     'fwrite':None,
                                     'default':False,
                                    },
                                    {'command':'INSCurrent',
                                     'component':None,
                                     'fread':self._HARMONY.getSCPIInstantCurrent,
                                     'fwrite':None,
                                     'default':True,
                                    },
                                    # CABOARD COMMANDS
                                    {'command':'FILTer',
                                     'component':'CABOard',
                                     'fread':self._HARMONY.caGetFilter,
                                     'fwrite':self._HARMONY.caSetFilter,
                                     'default':False,
                                    },
                                    {'command':'INIT',
                                     'component':'CABOard',
                                     'fread':self._HARMONY.caGetInit,
                                     'fwrite':self._HARMONY.caSetInit,
                                     'default':False,
                                    },
                                    {'command':'INVErsion',
                                     'component':'CABOard',
                                     'fread':self._HARMONY.caGetInversion,
                                     'fwrite':self._HARMONY.caSetInversion,
                                     'default':False,
                                    },
                                    {'command':'POSTfilter',
                                     'component':'CABOard',
                                     'fread':self._HARMONY.caGetPostFilter,
                                     'fwrite':self._HARMONY.caSetPostFilter,
                                     'default':False,
                                    },
                                    {'command':'PREFilter',
                                     'component':'CABOard',
                                     'fread':self._HARMONY.caGetPreFilter,
                                     'fwrite':self._HARMONY.caSetPreFilter,
                                     'default':False,
                                    },
                                    {'command':'RANGe',
                                     'component':'CABOard',
                                     'fread':self._HARMONY.caGetRange,
                                     'fwrite':self._HARMONY.caSetRange,
                                     'default':False,
                                    },
                                    {'command':'OFFSet',
                                     'component':'CABOard',
                                     'fread':self._HARMONY.caGetOffset,
                                     'fwrite':self._HARMONY.caSetOffset,
                                     'default':False,
                                    },                                    
                                    {'command':'TEMP',
                                     'component':'CABOard',
                                     'fread':self._HARMONY.caReadTemp,
                                     'fwrite':None,
                                     'default':False,
                                    },
                                    {'command':'TIGAin',
                                     'component':'CABOard',
                                     'fread':self._HARMONY.caGetTIGain,
                                     'fwrite':self._HARMONY.caSetTIGain,
                                     'default':False,
                                    },
                                    {'command':'VGAIn',
                                     'component':'CABOard',
                                     'fread':self._HARMONY.caGetVGain,
                                     'fwrite':self._HARMONY.caSetVGain,
                                     'default':False,
                                    },
                                    {'command':'SMAXimum',
                                     'component':'CABOard',
                                     'fread':self._HARMONY.caGetSaturationMax,
                                     'fwrite':self._HARMONY.caSetSaturationMax,
                                     'default':False,
                                    },                                    
                                    {'command':'SMINimum',
                                     'component':'CABOard',
                                     'fread':self._HARMONY.caGetSaturationMin,
                                     'fwrite':self._HARMONY.caSetSaturationMin,
                                     'default':False,
                                    },               
                                    {'command':'AOUT',
                                     'component':None,
                                     'fread':self._HARMONY.getVAnalog,
                                     'fwrite':self._HARMONY.setVAnalog,
                                     'default':False,
                                    },                                    
                                    ] 
    
        self._general_funct_list = [
                            # GENERAL COMMANDS
                            {'command':'RECOnfigure',
                             'component':None,
                             'fread':None,
                             'fwrite':self.reconfigure,
                             'default':False,
                             },
                            {'command':'FWVER',
                             'component':None,
                             'fread':self._HARMONY.getFWVersion,
                             'fwrite':None,
                             'default':False,
                            },
                            {'command':'FWDATE',
                             'component':None,
                             'fread':self._HARMONY.getFWVersionDate,
                             'fwrite':None,
                             'default':False,
                            },                            
                            # ACQUISITION COMMANDS
                            {'command':'FILTer',
                             'component':'ACQUisition',
                             'fread':self._HARMONY.getFilter,
                             'fwrite':self._HARMONY.setFilter,
                             'default':False,
                             },
                            {'command':'MEAS',
                             'component':'ACQUisition',
                             'fread':self._HARMONY.getMeas,
                             'fwrite':None,
                             'default':False,
                             },                            
                            {'command':'NDATa',
                             'component':'ACQUisition',
                             'fread':self._HARMONY.getNData,
                             'fwrite':None,
                             'default':False,
                             },
                            {'command':'RANGe',
                             'component':'ACQUisition',
                             'fread':self._HARMONY.getRange,
                             'fwrite':self._HARMONY.setRange,
                             'default':False,
                             },
                            {'command':'STARt',
                             'component':'ACQUisition',
                             'fread':None,
                             'fwrite':self._HARMONY.startAcq,
                             'default':False,
                             },
                            {'command':'STATe',
                             'component':'ACQUisition',
                             'fread':self._HARMONY.getState,
                             'fwrite':None,
                             'default':True,
                             }, 
                            {'command':'STOP',
                             'component':'ACQUisition',
                             'fread':None,
                             'fwrite':self._HARMONY.stopAcq,
                             'default':False,
                             },                                
                            {'command':'TIME',
                             'component':'ACQUisition',
                             'fread':self._HARMONY.getAcqTime,
                             'fwrite':self._HARMONY.setAcqTime,
                             'default':False,
                             },
                            # DIAGNOSTICS COMMANDS
                            {'command':'CBTEmp',
                             'component':'DIAGnostics',
                             'fread':self._HARMONY.caCBTemp,
                             'fwrite':None,
                             'default':False,
                             },
                            {'command':'FETEmp',
                             'component':'DIAGnostics',
                             'fread':self._HARMONY.caFETemp,
                             'fwrite':None,
                             'default':False,
                             },
                            {'command':'VSENse',
                             'component':'DIAGnostics',
                             'fread':self._DIAGS.getDiagsCurrentText,
                             'fwrite':None,
                             'default':True,
                            },
                            # TRIGGER COMMANDS
                            {'command':'DELAy',
                             'component':'TRIGger',
                             'fread':self._HARMONY.getTrigDelay,
                             'fwrite':self._HARMONY.setTrigDelay,
                             'default':False,
                             },
                            {'command':'INPUt',
                             'component':'TRIGger',
                             'fread':self._HARMONY.getTrigInput,
                             'fwrite':self._HARMONY.setTrigInput,
                             'default':False,
                             },
                            {'command':'MODE',
                             'component':'TRIGger',
                             'fread':self._HARMONY.getTrigMode,
                             'fwrite':self._HARMONY.setTrigMode,
                             'default':False,
                             },
                            {'command':'POLArity',
                             'component':'TRIGger',
                             'fread':self._HARMONY.getTrigPol,
                             'fwrite':self._HARMONY.setTrigPol,
                             'default':False,
                             },
                            {'command':'SWSEt',
                             'component':'TRIGger',
                             'fread':None,
                             'fwrite':self._HARMONY.setSWTrigger,
                             'default':False,
                             },                            
                            {'command':'STATe',
                             'component':'TRIGger',
                             'fread':self._HARMONY.getTriggerState,
                             'fwrite':None,
                             'default':True,
                             },
                            {'command':'RELAy',
                             'component':'FVCTrl',
                             'fread':self._DIAGS.getFVRelay,
                             'fwrite':self._DIAGS.setFVRelay,
                             'default':False,
                             },
                            {'command':'MAXLimit',
                             'component':'FVCTrl',
                             'fread':self._DIAGS.getFVMaximumLimit,
                             'fwrite':self._DIAGS.setFVMaximumLimit,
                             'default':False,
                             },
                            {'command':'MINLimit',
                             'component':'FVCTrl',
                             'fread':self._DIAGS.getFVMinimumLimit,
                             'fwrite':self._DIAGS.setFVMinimumLimit,
                             'default':False,
                             },
                            {'command':'RESEt',
                             'component':'FVCTrl',
                             'fread':None,
                             'fwrite':self._DIAGS.resetFV,
                             'default':False,
                             },
                            {'command':'STATe',
                             'component':'FVCTrl',
                             'fread':self._DIAGS.getFVLED,
                             'fwrite':None,
                             'default':True,
                             },       
                            {'command':'VOLTage',
                             'component':'FVCTrl',
                             'fread':self._DIAGS.getFVInstantVoltage,
                             'fwrite':None,
                             'default':False,
                             },
                            {'command':'AVERage',
                             'component':'FVCTrl',
                             'fread':self._DIAGS.getFVAverageVoltage,
                             'fwrite':None,
                             'default':False,
                             },                     
                            {'command':'MAXVoltage',
                             'component':'FVCTrl',
                             'fread':self._DIAGS.getFVMaximumVoltage,
                             'fwrite':None,
                             'default':False,
                             }, 
                            {'command':'MINVoltage',
                             'component':'FVCTrl',
                             'fread':self._DIAGS.getFVMinimumVoltage,
                             'fwrite':None,
                             'default':False,
                             },                             
                            {'command':'GAIN',
                             'component':'ODAC',
                             'fread':self._HARMONY.getDACGain,
                             'fwrite':self._HARMONY.setDACGain,
                             'default':True,
                             },                                                        
                            ] 
    
        self._specials_list = [{'command':'idn', 
                                'fread':self.getIdetification,
                                'fwrite':None},
                               {'command':'mac',
                                'fread':self.getMacAddress,
                                'fwrite':None},
                               {'command':'RST',
                                'fread':None,
                                'fwrite':self.resetCommand},
                               {'command':'HLP',
                                'fread':self.helpCommand,
                                'fwrite':None},
                               {'command':'SHT',
                                'fread':None,
                                'fwrite':self.shutdownCommand},
                               {'command':'FAC',
                                'fread':None,
                                'fwrite':self.factoryResetCommand},                               
                              ]
        
        self._gpio_funct_list = [
                            # GPIO COMMANDS
                            {'command':'NAME',
                             'component':None,
                             'fread':self._HARMONY.getGPIOName,
                             'fwrite':None,
                             'default':True,
                             },                            
                            {'command':'CONFig',
                             'component':None,
                             'fread':self._HARMONY.getGPIOConfig,
                             'fwrite':self._HARMONY.setGPIOConfig,
                             'default':False,
                             },
                            {'command':'VALUe',
                             'component':None,
                             'fread':self._HARMONY.getGPIOValue,
                             'fwrite':self._HARMONY.setGPIOValue,
                             'default':False,
                             },
                            ]
                            
        self._supply_funct_list = [
                            # GPIO COMMANDS
                            {'command':'VALUe',
                             'component':None,
                             'fread':self._HARMONY.getSupplyPort,
                             'fwrite':self._HARMONY.setSupplyPort,
                             'default':True,
                             },
                            ]                            

        self._log.logMessage("__init__() Initialized ", self._log.INFO)

        try:
            self._scpiObj = scpi.scpi(local=self._scpilocal, port=self._scpiport,\
                                      autoOpen=self._scpiautoopen, debug=self._scpi_debug, writeLock=True)
            self._log.logMessage("createSCPIObject() Object created %s"%self._scpiObj, self._log.INFO)
        
            handler_list = self._drvlog.getHandlers()
            for handler in handler_list:
                self._scpiObj._devlogger.addHandler(handler)
                
            self._scpiObj.log2File(True)
            self._scpiObj.logEnable(self._scpi_debug)   
        
            # Build scpi command list
            self._help_cmd_list = ''
            
            self.createSCPISpecialsList()
            self.createSCPIFunctionList()

        except Exception, e:
            self._log.logMessage("FAILED TO Create scpi Obj due to: %s"%str(e), self._log.CRITICAL)
            self._scpiObj = None
    
    def stop(self): 
        if self._scpiObj is not None:
            self._scpiObj = None
        self._log.logMessage("destroyedSCPIObject %s"%self._scpiObj, self._log.INFO)
    
    def createSCPISpecialsList(self):
        for spEl in self._specials_list:
            cmd = spEl['command']
            self._scpiObj.addSpecialCommand(cmd, readcb=spEl['fread'], writecb=spEl['fwrite'])

            self._help_cmd_list += cmd.upper()+"\n"
            self._log.logMessage("scpi special command ==> %s"%cmd.upper(), self._log.INFO)
    
    def createSCPIFunctionList(self):
        # Added general commans fisrt
        for spEl in self._general_funct_list:
            
            if spEl['component'] is not None:
                compName = spEl['component']
                attrName = spEl['command']
                cmd = '%s:%s'%(compName,attrName)
            else:
                attrName = spEl['command']
                cmd='%s'%attrName
                
            self._scpiObj.addCommand(cmd, readcb=spEl['fread'], writecb=spEl['fwrite'], default=spEl['default'])

            self._help_cmd_list += cmd.upper()+"\n"
            self._log.logMessage("scpi general command ==> %s"%cmd.upper(), self._log.INFO)
        
        # Added channel commands
        compList = {}
        spChannel = self._scpiObj.addChannel('CHANNEL', _NUMBER_OF_CHANNELS, self._scpiObj._commandTree)
        for spEl in self._channel_funct_list:
            cmd = spEl['command']
            if spEl['component'] is not None:
                compName = spEl['component']

                if compName not in compList.keys():
                    comp = self._scpiObj.addComponent(compName, spChannel)
                    compList[compName] = comp
                else: 
                    comp = compList[compName]
                
                txt = "CHANnelXX:"+compName.upper()+":"+cmd.upper()
                self._scpiObj.addAttribute(cmd, comp, readcb=spEl['fread'], writecb=spEl['fwrite'], default=spEl['default'])
            else:
                txt = "CHANnelXX:"+cmd.upper()
                self._scpiObj.addAttribute(cmd, spChannel, readcb=spEl['fread'], writecb=spEl['fwrite'], default=spEl['default'])
            
            
            self._help_cmd_list += txt+"\n"
            self._log.logMessage("scpi channel command ==> %s"%txt, self._log.INFO)

        # Added gpio commands
        compList = {}
        spChannel = self._scpiObj.addChannel('IOPORT', _NUMBER_OF_GPIO, self._scpiObj._commandTree)
        for spEl in self._gpio_funct_list:
            cmd = spEl['command']
            if spEl['component'] is not None:
                compName = spEl['component']

                if compName not in compList.keys():
                    comp = self._scpiObj.addComponent(compName, spChannel)
                    compList[compName] = comp
                else: 
                    comp = compList[compName]
                
                txt = "IOPOrtXX:"+compName.upper()+":"+cmd.upper()
                self._scpiObj.addAttribute(cmd, comp, readcb=spEl['fread'], writecb=spEl['fwrite'], default=spEl['default'])
            else:
                txt = "IOPOrtXX:"+cmd.upper()
                self._scpiObj.addAttribute(cmd, spChannel, readcb=spEl['fread'], writecb=spEl['fwrite'], default=spEl['default'])
            
            
            self._help_cmd_list += txt+"\n"
            self._log.logMessage("scpi channel command ==> %s"%txt, self._log.INFO)

        # Added supply commands
        compList = {}
        spChannel = self._scpiObj.addChannel('SUPP', _NUMBER_OF_SUPPLY, self._scpiObj._commandTree)
        for spEl in self._supply_funct_list:
            cmd = spEl['command']
            if spEl['component'] is not None:
                compName = spEl['component']

                if compName not in compList.keys():
                    comp = self._scpiObj.addComponent(compName, spChannel)
                    compList[compName] = comp
                else: 
                    comp = compList[compName]
                
                txt = "SUPPlyXX:"+compName.upper()+":"+cmd.upper()
                self._scpiObj.addAttribute(cmd, comp, readcb=spEl['fread'], writecb=spEl['fwrite'], default=spEl['default'])
            else:
                txt = "SUPPlyXX:"+cmd.upper()
                self._scpiObj.addAttribute(cmd, spChannel, readcb=spEl['fread'], writecb=spEl['fwrite'], default=spEl['default'])
            
            
            self._help_cmd_list += txt+"\n"
            self._log.logMessage("scpi channel command ==> %s"%txt, self._log.INFO)

                            
    def helpCommand(self):
        self._log.logMessage("SCPI - helpCommand()", self._log.INFO)
        # Only to test problems
        print self._scpiObj.commands        
        return self._help_cmd_list
    
    def resetCommand(self):
        self._log.logMessage("RESET_COMMAND ==> Rebooting System...............bye, bye!!", self._log.INFO)

        # restart system
        self._parent.end(type='REBOOT')
        
        
    def shutdownCommand(self):
        self._log.logMessage("SHUTDOWN_COMMAND ==> Shuting System...............bye, bye!!", self._log.INFO)

        # restart system
        self._parent.end(type='SHUTDOWN')
        
    def factoryResetCommand(self):
        # Reset Diagnostics
        self._DIAGS.resetFV(1)
        
        # Delete user settings file
        self._MEMMW.factoryReset()
        
        self._log.logMessage("RESET_COMMAND ==> Rebooting System...............bye, bye!!", self._log.INFO)

        # restart system
        self._parent.end(type='REBOOT')        
        
    def getIdetification(self):
        # Get config File
        configDict = getConfigData("MAIN_")
        identification_manufacturer = configDict["MANUFACTURER_"] if "MANUFACTURER_" in configDict.keys() else ""
        identification_instrument = configDict["INSTRUMENT_"] if "INSTRUMENT_" in configDict.keys() else ""
        identification_serial = configDict["SERIAL_"] if "SERIAL_" in configDict.keys() else ""
        
        identification = identification_manufacturer +","+ identification_instrument +","+ identification_serial
        identification.replace("\n",", ")
        self._log.logMessage("getIdetification() value=%s"%identification, self._log.DEBUG)
        return identification 
    
    def getMacAddress(self):
        self._log.logMessage("getMacAddress()", self._log.DEBUG)
        mac = format(get_mac(), 'x')
        mac_format = ':'.join([mac[i:i+2] for i,j in enumerate(mac) if not (i%2)])
        self._log.logMessage("getMacAddress() value=%s"%mac_format, self._log.DEBUG)
        return mac_format
    
    def reconfigure(self, attr):
        for key, el in self._parent._applicationss.iteritems():
            try:
                dev_pointer = el['pointer']
                dev_pointer.reconfigure()
            except Exception, e:
                self.setLogMessage("Failed to reconfigure %s due to: %s"%(key,str(e)), self._log.WARNING)
            
        self._log.logMessage("GeneralClass.reconfigure() Config data file reloaded", self._log.INFO)                
        
    def inputCommand(self, owner, command):
        try:
            self._log.logMessage("inputCommand():: owner=%s command=%s"%(str(owner),str(command)), self._log.INFO)                
            self._scpiObj.input(str(command))
        except Exception, e:
            self._log.logMessage("inputCommand():: failed to execute command %s due to %s"%(str(command),str(e)), self._log.WARNING)
    