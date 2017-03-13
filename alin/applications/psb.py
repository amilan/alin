## @package psb.py 
#    File containing the driver module that controls the Power Supply board
#
#    Author = "Manuel Broseta"
#    Copyright = "Copyright 2015, ALBA"
#    Version = "1.0"
#    Email = "mbroseta@cells.es"
#    Status = "Development"
#    History:
#              9/05/2016 - file created by Manolo Broseta


from alin.base import AlinLog
from alin.base import getConfigData

from alin.drivers.ads7828 import ADS7828
from alin.drivers.mcp23008 import MCP23008

import threading
import time

_CONFIG_MASK = "PSB_"

_DEFAULT_VIISO_LIMIT     = 3183
_DEFAULT_VIVCC_LIMIT     = 2818
_DEFAULT_VIVS_LIMIT      = 3148
_DEFAULT_VIAUX_LIMIT     = 2861
_DEFAULT_VISPEC_LIMIT    = 2731

_DEFAULT_SAMPLINGTIME = 0.5
_DEFAULT_REPETITIONS = 3

class Psb(AlinLog):
    def __init__(self,debug=False):
        AlinLog.__init__(self, debug=False, loggerName='Psb')
        
        # Get default configuration from config file
        self._debug = debug
        self.configure()
        
        try:
            self.pexdrv = MCP23008()
        except:
            self.pexdrv = None
        try:
            self.adcdrv = ADS7828()
        except:
            self.adcdrv = None
        
        self._psb_thread = None
        
        # Applications
        self._MEMMW = None        
        
        self.logMessage("__init__() Initialized ", self.DEBUG)
        
    def configure(self):
        # Get default configuration from config file
        configDict = getConfigData(_CONFIG_MASK)
        self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else self._debug
        self._debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 20
        self._viiso_limit = int(configDict["VSENSE_I_ISO_LIMIT_"]) if "VSENSE_I_ISO_LIMIT_" in configDict.keys() else _DEFAULT_VIISO_LIMIT
        self._vivcc_limit = int(configDict["VSENSE_I_VCC_LIMIT_"]) if "VSENSE_I_VCC_LIMIT_" in configDict.keys() else _DEFAULT_VIVCC_LIMIT
        self._vivs_limit = int(configDict["VSENSE_I_VS_LIMIT_"]) if "VSENSE_I_VS_LIMIT_" in configDict.keys() else _DEFAULT_VIVS_LIMIT
        self._viaux_limit = int(configDict["VSENSE_I_AUX_LIMIT_"]) if "VSENSE_I_AUX_LIMIT_" in configDict.keys() else _DEFAULT_VIAUX_LIMIT
        self._vispec_limit = int(configDict["VSENSE_I_SPEC_LIMIT_"]) if "VSENSE_I_SPEC_LIMIT_" in configDict.keys() else _DEFAULT_VISPEC_LIMIT
        self._looptime = float(configDict["LOOPTIME_"]) if "LOOPTIME_" in configDict.keys() else _DEFAULT_SAMPLINGTIME
        self._repetitions = int(configDict["REPETITIONS_"]) if "REPETITIONS_" in configDict.keys() else _DEFAULT_REPETITIONS
        
        # Logging
        self.logLevel(self._debuglevel)
        self.logEnable(self._debug)
        
        self.logMessage("configure() %s configured"%_CONFIG_MASK, self.INFO)
        

    def reconfigure(self):
        self.logMessage("reconfigure(): reconfiguring applications and associted devices", self.INFO)
                
        # reconfigure Applications
        self.configure()
        
        # reconfigure devices
        if self.pexdrv is not None:
            self.pexdrv.configure()
        if self.adcdrv is not None:
            self.adcdrv.configure()
        
        self.logMessage("reconfigure(): Done!!", self.INFO)

    def start(self):
        self.logMessage("start() Start PSB HW & control....",self.INFO)
        
        # Initialize ADC
        if self.adcdrv is not None:
            self.adcdrv.init()
        
        # Initialize PExp
        if self.pexdrv is not None:
            self.pexdrv.init()
        
        # Start PSB process control
        if self.adcdrv is not None:
            try:
                self._psb_thread = PSBControl(self, debug=self._debug, adc=self.adcdrv, pexp=self.pexdrv, loop=self._looptime, retries=self._repetitions)
                self._psb_thread.setDaemon(True)
                
                aux_limits = []
                aux_limits.append(self._viiso_limit)
                aux_limits.append(self._vivcc_limit)
                aux_limits.append(self._vivs_limit)
                aux_limits.append(self._viaux_limit)
                aux_limits.append(self._vispec_limit)
                self._psb_thread.setLimits(aux_limits)
                
                self._psb_thread.start()
                self.logMessage("start() Thread started",self.INFO)
            except Exception, e:
                self.logMessage("start() Not possible to start thread due to: %s"%str(e),self.ERROR)
                return 
        
    def stop(self):
        self.logMessage("stop() Stop PSB control....",self.INFO)
        if self._psb_thread is not None:
            self._psb_thread.end()
        
        while not self._psb_thread.getProcessEnded():
            self.logMessage("stop(): Waiting process to die", self.INFO)
            time.sleep(0.5)
            pass  
        
        self.logMessage("stop() Thread stop", self.INFO)
        
    def shareApplications(self, applications):
        self.logMessage("shareApplications(): Getting needed applications layers", self.INFO)

        self._MEMMW = applications['MEMORY_APP']['pointer']
    
    def setISO(self, value):
        if self.pexdrv is not None:
            try:
                self.logMessage("setISO() value %s"%value, self.INFO)
                self.pexdrv.writeRegister('CTRL_ISO',value)

                self.saveUserData(item='psbiso', data=value)                   
            except Exception, e:
                self.logMessage("setISO() Not possible to set CtrlISO due to %s"%str(e), self.ERROR)

    def getISO(self):
        ret_val = None
        if self.pexdrv is not None:
            try:
                ret_val = self.pexdrv.readRegister('CTRL_ISO')
                self.logMessage("getISO() value %s"%str(ret_val), self.DEBUG)
            except Exception, e:
                self.logMessage("getISO() Not possible to get CtrlISO due to %s"%str(e), self.ERROR)
        return ret_val
    
    def setVCC(self, value):
        if self.pexdrv is not None:
            try:
                self.logMessage("setVCC() value %s"%value, self.INFO)
                self.pexdrv.writeRegister('CTRL_VCC',value)
                
                self.saveUserData(item='psbvcc', data=value)                                   
            except Exception, e:
                self.logMessage("setVCC() Not possible to set CtrlVcc due to %s"%str(e), self.ERROR)
    
    def getVCC(self):
        ret_val = None
        if self.pexdrv is not None:
            try:
                ret_val = self.pexdrv.readRegister('CTRL_VCC')
                self.logMessage("getVCC() value %s"%str(ret_val), self.DEBUG)
            except Exception, e:
                self.logMessage("getVCC() Not possible to get CtrlVCC due to %s"%str(e), self.ERROR)
        return ret_val
    
    def setVS(self, value):
        if self.pexdrv is not None:
            try:
                self.logMessage("setVS() value %s"%value, self.INFO)
                self.pexdrv.writeRegister('CTRL_VS',value)
                
                self.saveUserData(item='psbvs', data=value)                                   
            except Exception, e:
                self.logMessage("setVS() Not possible to set CtrlVS due to %s"%str(e), self.ERROR)
    
    def getVS(self):
        ret_val = None
        if self.pexdrv is not None:
            try:
                ret_val = self.pexdrv.readRegister('CTRL_VS')
                self.logMessage("getVS() value %s"%str(ret_val), self.DEBUG)
            except Exception, e:
                self.logMessage("getVS() Not possible to get CtrlVS due to %s"%str(e), self.ERROR)
        return ret_val
    
    def setVAUX(self, value):
        if self.pexdrv is not None:
            try:
                self.logMessage("setVAUX() value %s"%value, self.INFO)
                self.pexdrv.writeRegister('CTRL_VAUX',value)
                
                self.saveUserData(item='psbvaux', data=value) 
            except Exception, e:
                self.logMessage("setVAUX() Not possible to set CtrlVAUX due to %s"%str(e), self.ERROR)
    
    def getVAUX(self):
        ret_val = None
        if self.pexdrv is not None:
            try:
                ret_val = self.pexdrv.readRegister('CTRL_VAUX')
                self.logMessage("getVAUX() value %s"%str(ret_val), self.DEBUG)
            except Exception, e:
                self.logMessage("getVAUX() Not possible to get CtrlVAUX due to %s"%str(e), self.ERROR)
        return ret_val
    
    def saveUserData(self, item=None, idx=None, data=None):
        try:
            self._MEMMW.saveUserData(item, idx, data)             
        except:
            pass    

class PSBControl(threading.Thread):
    def __init__(self, parent=None, debug=None, adc=None, pexp=None, loop=_DEFAULT_SAMPLINGTIME, retries=_DEFAULT_REPETITIONS):
        threading.Thread.__init__(self)
        self._parent = parent
        
        self._endProcess = False
        self._processEnded = False
        
        self._looptime = loop
        self._max_repetitions = retries
        
        self._adc = adc
        self._pexp = pexp
        
        self._vsenseiiso_limit = None
        self._vsenseivcc_limit = None
        self._vsenseivs_limit = None
        self._vsenseiaux_limit = None
        self._vsenseispec_limit = None
        
        self._vsenseiiso_counter = 0
        self._vsenseivcc_counter = 0
        self._vsenseivs_counter = 0
        self._vsenseiaux_counter = 0
        self._vsenseispec_counter = 0
        
        
    def end(self):
        self._parent.logMessage("PSBControl() Stopping control thread....",self._parent.INFO)
        self._endProcess = True
        
    def getProcessEnded(self):
        return self._processEnded
    
    def setLimits(self, limits):
        if limits != []:
            self._vsenseiiso_limit = limits[0]
            self._vsenseivcc_limit = limits[1]
            self._vsenseivs_limit = limits[2]
            self._vsenseiaux_limit = limits[3]
            self._vsenseispec_limit = limits[4]
    
    def run(self):
        display_msg = False 
        while not (self._endProcess):
            if self._adc.status() and self._pexp.status():
                display_msg = False 
                self._parent.logMessage("PSBControl() Power Supply board check...",self._parent.DEBUG)
                
                # Check Isolated PowerSupply
                try:
                    if self._pexp.readRegister('CTRL_ISO'):
                        aux_diags = self._adc.getRegister('VSENSE_I_ISO')
                        self._parent.logMessage("PSBControl() Checking ISO Power Supply..read %s....."%str(aux_diags),self._parent.DEBUG)
                        if aux_diags > self._vsenseiiso_limit:
                            self._vsenseiiso_counter += 1
                            if self._vsenseiiso_counter > self._max_repetitions:
                                # Switch Off Isolated Power Supply
                                self._parent.logMessage("PSBControl() Isolated Power Supply above load limit (%s). Switching of......"%str(aux_diags),self._parent.INFO)
                                self._pexp.writeRegister('CTRL_ISO',False)
                                self._vsenseiiso_counter = 0
                        else:
                            self._vsenseiiso_counter -= 1
                            if self._vsenseiiso_counter <= 0:
                                self._vsenseiiso_counter = 0
                except Exception, e:
                    self._parent.logMessage("PSBControl() Not possible to check Isolated Power Supply due to %s"%str(e),self._parent.CRITICAL)
                    
                # Check VCC Power Supply
                try:
                     if self._pexp.readRegister('CTRL_VCC'):
                        aux_diags = self._adc.getRegister('VSENSE_I_VCC')
                        self._parent.logMessage("PSBControl() Checking VCC Power Supply..read %s....."%str(aux_diags),self._parent.DEBUG)
                        if aux_diags > self._vsenseivcc_limit:
                            self._vsenseivcc_counter += 1
                            if self._vsenseivcc_counter > self._max_repetitions:
                                # Switch Off Isolated Power Supply
                                self._parent.logMessage("PSBControl() VCC Power Supply above load limit (%s). Switching of......"%str(aux_diags),self._parent.INFO)
                                self._pexp.writeRegister('CTRL_VCC',False)
                                self._vsenseivcc_counter = 0
                        else:
                            self._vsenseivcc_counter -= 1
                            if self._vsenseivcc_counter <= 0:
                                self._vsenseivcc_counter = 0
                except Exception, e:
                    self._parent.logMessage("PSBControl() Not possible to check VCC Power Supply due to %s"%str(e),self._parent.CRITICAL)
    
                # Check VS PowerSupply
                try:
                    if self._pexp.readRegister('CTRL_VS'):
                        aux_diags = self._adc.getRegister('VSENSE_I_VS')
                        self._parent.logMessage("PSBControl() Checking VS Power Supply..read %s....."%str(aux_diags),self._parent.DEBUG)
                        if aux_diags > self._vsenseivs_limit:
                            self._vsenseivs_counter += 1
                            if self._vsenseivs_counter > self._max_repetitions:
                                # Switch Off Isolated Power Supply
                                self._parent.logMessage("PSBControl() VS Power Supply above load limit (%s). Switching of......"%str(aux_diags),self._parent.INFO)
                                self._pexp.writeRegister('CTRL_VS',False)
                                self._vsenseivs_counter = 0
                        else:
                            self._vsenseivs_counter -= 1
                            if self._vsenseivs_counter <= 0:
                                self._vsenseivs_counter = 0   
                except Exception, e:
                    self._parent.logMessage("PSBControl() Not possible to check VS Power Supply due to %s"%str(e),self._parent.CRITICAL)
    
                # Check Auxiliary Power Supply
                try:
                    if self._pexp.readRegister('CTRL_VAUX'):
                        aux_diags = self._adc.getRegister('VSENSE_I_AUX')
                        self._parent.logMessage("PSBControl() Checking Auxiliary Power Supply..read %s....."%str(aux_diags),self._parent.DEBUG)
                        if aux_diags > self._vsenseiaux_limit:
                            self._vsenseiaux_counter += 1
                            if self._vsenseiaux_counter > self._max_repetitions:
                                # Switch Off Isolated Power Supply
                                self._parent.logMessage("PSBControl() Auxiliary Power Supply above load limit (%s). Switching of......"%str(aux_diags),self._parent.INFO)
                                self._pexp.writeRegister('CTRL_VAUX',False)
                                self._vsenseiaux_counter = 0
                        else:
                            self._vsenseiaux_counter -= 1
                            if self._vsenseiaux_counter <= 0:
                                self._vsenseiaux_counter = 0     
                except Exception, e:
                    self._parent.logMessage("PSBControl() Not possible to check Auxiliary Power Supply due to %s"%str(e),self._parent.CRITICAL)
    
                # Check 12V SPEC Power Supply
                try:
                    aux_diags = self._adc.getRegister('VSENSE_I_SPEC')
                    self._parent.logMessage("PSBControl() Checking 12V SPEC Power Supply..read %s....."%str(aux_diags),self._parent.DEBUG)
                    if aux_diags > self._vsenseispec_limit:
                        self._vsenseispec_counter += 1
                        if self._vsenseispec_counter > self._max_repetitions:
                            # Switch Off Isolated Power Supply
                            self._parent.logMessage("PSBControl() 12V SPEC Power Supply above load limit (%s). Switching of......"%str(aux_diags),self._parent.INFO)
                            self._vsenseispec_counter = 0
                    else:
                        self._vsenseispec_counter -= 1
                        if self._vsenseispec_counter <= 0:
                            self._vsenseispec_counter = 0         
                except Exception, e:
                    self._parent.logMessage("PSBControl() Not possible to check 12V SPEC Power Supply due to %s"%str(e),self._parent.CRITICAL)
            else:
                if not display_msg:
                    display_msg = True
                    self._parent.logMessage("PSBControl() Can't check Power Supply. No communication with devices..",self._parent.ERROR)
                    
            time.sleep(self._looptime)
            
        self._processEnded = True    

