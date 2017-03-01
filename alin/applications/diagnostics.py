## @package Diagnostics.py 
#	File containing the device class, to control the ADC
#
#	Author = "Manuel Broseta"
#	Copyright = "Copyright 2016, ALBA"
#	Version = "1.0"
#	Email = "mbroseta@cells.es"
#	Status = "Development"
#	History:
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

from alin.drivers.crossbar import CrossBar
from alin.drivers.ads7828 import ADS7828
from alin.drivers.fvctrl import FVCtrl

import os
import threading
import time

_CONFIG_MASK = "DIAGS_"

class Diagnostics(AlinLog):
	def __init__(self, debug=False):
		AlinLog.__init__(self, debug=False, loggerName='DIAGS  ')

		# Get default configuration from config file
		self._debug = debug
		self.configure()

		self._dHRMYCB_0 = CrossBar(number=0)
		self._dHRMYCB_1 = CrossBar(number=1)
		self._dHRMYCB_2 = CrossBar(number=2)
		self._dHRMYCD_devices = [self._dHRMYCB_0, self._dHRMYCB_1, self._dHRMYCB_2]
		try:
			self._dADC = ADS7828()
		except:
			self._dADC = None
			
		# Applications
		self._MEMMW = None			
		
		self._dFVCTRL = FVCtrl()
		
		self.logMessage("__init__() Initialized ", self.INFO)
	
	def configure(self):
		# Get default configuration from config file
		configDict = getConfigData(_CONFIG_MASK)
		self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else self._debug
		self._debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 40
		
		# Logging
		self.logLevel(self._debuglevel)
		self.logEnable(self._debug)
		
		self.logMessage("configure() %s configured"%_CONFIG_MASK, self.INFO)        

	def reconfigure(self):
		self.logMessage("reconfigure(): reconfiguring applications and associted devices", self.INFO)

		# reconfigure Applications
		self.configure()
		
		# reconfigure devices
		self._dHRMYCB_0.configure()
		self._dHRMYCB_1.configure()
		self._dHRMYCB_2.configure()
		if self._dADC is not None:
			self._dADC.configure() 
		self._dFVCTRL.configure() 
		
		self.logMessage("reconfigure(): Done!!", self.INFO)
			
	def start(self):
		self.logMessage("start()", self.INFO)
		
		#Configuration of CrossBar
		self.logMessage("init(): Configuration of crossbar block", self.INFO)
		self._dHRMYCB_0.init()
		self._dHRMYCB_1.init()
		self._dHRMYCB_2.init()
		self._dFVCTRL.init()
		
		self.logMessage("start(): Diagnostics module started", self.INFO)
		
	def stop(self):
		self.logMessage("stop(): End Diagnostics control module", self.INFO)
		# Nothing to do
		
	def shareApplications(self, applications):
		self.logMessage("shareApplications(): Getting needed applications layers", self.INFO)

		self._MEMMW = applications['MEMORY_APP']['pointer']
			
	def getMemoryMLen(self):
		retval = []
		for dev in self._dHRMYCD_devices:
			retval.append(dev.readAttribute('ID_DIAGNJD_MLEN'))
		self.logMessage("getMemoryMLen(): Number of messages send witout a free slot=[%s]"%(', '.join(map(hex, retval))), self.DEBUG)
		return retval

	def getMemoryActReq(self):
		retval = []
		for dev in self._dHRMYCD_devices:
			retval.append(dev.readAttribute('ID_DIAGNJDRD_MREQ'))
		self.logMessage("getMemoryMLen(): Number of request active=[%s]"%(', '.join(map(hex, retval))), self.DEBUG)
		return retval

	def getMemorySgnAct(self):
		retval = []
		for dev in self._dHRMYCD_devices:
			retval.append(dev.readAttribute('ID_DIAGNJDRDRD_MTREQ'))
		self.logMessage("getCrossSgnAct(): Maximum number of requests active simultaiusly=[%s]"%(', '.join(map(hex, retval))), self.DEBUG)
		return retval

	def getUploadMessages(self):
		retval = []
		for dev in self._dHRMYCD_devices:
			retval.append(dev.readAttribute('ID_DIAGN_UPLOADMSG'))
		self.logMessage("getCrossSgnAct(): Maximum number of requests active simultaiusly=[%s]"%(', '.join(map(hex, retval))), self.DEBUG)
		return retval

	def getDownloadMessages(self):
		retval = []
		for dev in self._dHRMYCD_devices:
			retval.append(dev.readAttribute('ID_DIAGN_DWLOADMSG'))
		self.logMessage("getCrossSgnAct(): Maximum number of requests active simultaiusly=[%s]"%(', '.join(map(hex, retval))), self.DEBUG)
		return retval

        
	def getDiagsCurrent(self):
		self.logMessage("getDiagsCurrent()", self.DEBUG)
		ret_dict = {}
		if self._dADC is not None:
			current_list = {'VSENSE_I_ISO'	: 1.7238,
							'VSENSE_I_VS'	: 7.4477,
							'VSENSE_I_SPEC'	: 0.44,
							'VSENSE_I_VCC'	: 1.503,
							'VSENSE_I_AUX'	: 2.305,
							}
			for currkey in current_list.keys():
				try:
					adc_val = self._dADC.getRegister(currkey)
					current = (adc_val * 3.3)/(4096.*current_list[currkey]) 
				except Exception, e:
					current = None
					self.logMessage("getDiagsCurrent() Error in reg %s due to %s"%(currkey,str(e)), self.ERROR)
				ret_dict[currkey] = current
				self.logMessage("getDiagsCurrent() %s=%s"%(currkey, str(current)), self.DEBUG)
				
		return ret_dict

	def getDiagsCurrentText(self):
		self.logMessage("getDiagsCurrentText()", self.DEBUG)
		ret_dict = self.getDiagsCurrent()
		ret_val = []
		for key, val in ret_dict.iteritems():
			ret_val.append([key,val])
			
		return '[%s]' % ', '.join(map(str, ret_val))

	def getFVInstantVoltage(self):
		val = round(self._dFVCTRL.getInstantVoltage(),2)
		self.logMessage("getFVInstantVoltage() Voltage=%s"%str(val), self.DEBUG)
		return val
		
	def getFVAverageVoltage(self):
		val = round(self._dFVCTRL.getAverageVoltage(),2)
		self.logMessage("getFVAverageVoltage() Voltage=%s"%str(val), self.DEBUG)
		return val

	def getFVMaximumVoltage(self):
		val = int(self._dFVCTRL.getMaximumVoltage())
		self.logMessage("getFVMaximumVoltage() Voltage=%s"%str(val), self.DEBUG)
		return val

	def getFVMinimumVoltage(self):
		val = int(self._dFVCTRL.getMinimumVoltage())
		self.logMessage("getFVMinimumVoltage() Voltage=%s"%str(val), self.DEBUG)
		return val

	def getFVLED(self):
		val = self._dFVCTRL.getLEDStatus()
		self.logMessage("getFVLED() LED=%s"%str(val), self.DEBUG)
		return val
    
	def getFVRelay(self):
		val = self._dFVCTRL.getRelay()
		self.logMessage("getFVRelay() Relay=%s"%str(val), self.DEBUG)
		return val

	def setFVRelay(self, value):
		try:
			self._dFVCTRL.setRelay(int(value))
			self.logMessage("setRelay(): Relay set to value=%s"%str(value), self.DEBUG)
		except Exception, e:
			self.logMessage("setRelay(): Error due to %s"%str(e), self.ERROR)    
			
	def getFVMaximumLimit(self):
		val = int(self._dFVCTRL.getMaximumLimit())
		self.logMessage("getFVMaximumLimit() Limit=%s"%str(val), self.DEBUG)
		return val

	def setFVMaximumLimit(self, value):
		try:
			self._dFVCTRL.setMaximumLimit(int(value))
			self.logMessage("setFVMaximumLimit(): Max Limit set to value=%s"%str(value), self.INFO)
			
			self.saveUserData(item='fvmaximumlimit', data=value)
		except Exception, e:
			self.logMessage("setFVMaximumLimit(): Error due to %s"%str(e), self.ERROR)        
        
	def getFVMinimumLimit(self):
		val = int(self._dFVCTRL.getMinimumLimit())
		self.logMessage("getFVMinimumLimit() Limit=%s"%str(val), self.DEBUG)
		return val

	def setFVMinimumLimit(self, value):
		try:
			self._dFVCTRL.setMinimumLimit(int(value))
			self.logMessage("setFVMinimumLimit(): Min Limit set to value=%s"%str(value), self.INFO)
			
			self.saveUserData(item='fvminimumlimit', data=value)        
		except Exception, e:
			self.logMessage("setFVMinimumLimit(): Error due to %s"%str(e), self.ERROR)        
            
	def getHVStatus(self):
		val = self._dFVCTRL.getHVState()
		self.logMessage("getHVStatus() HV=%s"%str(val), self.DEBUG)
		return val
    
	def resetFV(self, value):
		val = self._dFVCTRL.resetFV()
		self.logMessage("resetFV() REset dataq", self.INFO)
		
		self.saveUserData(item='resetfv', data=value)
		return val

	def saveUserData(self, item=None, idx=None, data=None):
		try:
			self._MEMMW.saveUserData(item, idx, data)             
		except:
			pass  