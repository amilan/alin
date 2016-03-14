## @package alinspinctrl.py 
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

import os

from random import uniform

from alin.base import AlinDevice
from alin.base import AlinLog

from distutils.sysconfig import get_python_lib

__CONFIG_FILE__ = "Config"
__CONFIG_MASK__ = "ADCCORE_"


class AdcCore(AlinLog):
	def __init__(self, dev='ADC_CORE', debug=False):
		AlinLog.__init__(self, debug=False, loggerName='AdcCore')		

		self._debug = debug
		self._debuglevel = 40
		self._device = dev
		# Get default configuration from config file
		self.getConfigData()

		self._alindev = AlinDevice(debug=self._debug, device=self._device)
		
		# Logging
		self.setLogLevel(self._debuglevel)
		self.logEnable(self._debug)
	
	def getConfigData(self):
		# Get config File
		config_folder = get_python_lib()+"/alin/config/"
		config_file = config_folder+__CONFIG_FILE__
		# Get config File
		config_folder = get_python_lib()+"/alin/config/"
		config_file = config_folder+__CONFIG_FILE__
		
		config_dict = {"DEBUG_":[self._debug, "bool"],
						"DEBUGLEVEL_": [self._debuglevel,"int"],
						"DEVICE_":[self._device,"string"],
						}
		
		try:
			with open(config_file, 'r') as f:
				lines = f.readlines()
				f.close()
				
			comp = [ln.split(__CONFIG_MASK__)[1].replace(" ","").replace("\t","").replace("\n","") for ln in lines if ln.startswith(__CONFIG_MASK__)]
			if comp != []:
				for cm in comp:
					key = cm.split("=")[0]
					value = cm.split("=")[1]
					if key in config_dict.keys():
						try:
							if config_dict[key][1] == "bool":
								config_dict[key][0] = True if value.lower() == "true" else False
							elif config_dict[key][1] == "int":
								config_dict[key][0] = int(value)
							#elif config_dict[key][1] == "string":
							else:
								config_dict[key][0] = cm.split("=")[1]
							self.logMessage("%s::getConfigData(): %s set to %s"%(__CONFIG_MASK__, key.upper(), self._debug),self.DEBUG)
						except Exception, e:
							self.logMessage("%s::getConfigData(): Can't get %s flag %s"%(__CONFIG_MASK__, key.upper(), self._debug, str(e)),self.ERROR)
		except Exception, e:
			self.logMessage("%s::getConfigData():: Not possible to get config file due to:"%__CONFIG_MASK__,self.ERROR)
			self.logMessage(str(e),self.ERROR)
			
	def setLogLevel(self, level):
		self._debuglevel = level
 
		self.logLevel(self._debuglevel)
		
		self._alindev.setLogLevel(self._debuglevel)

	def startAdc(self):
		self._alindev.writeAttribute('CTL_ADQ_M',0x01)
		self.logMessage("startAdc()...", self.DEBUG)

	def stopAdc(self):
		self._alindev.writeAttribute('CTL_ADQ_M',0x00)
		self.logMessage("stopAdc()...", self.DEBUG)

	def getAdcRunState(self):
		readch = self._alindev.readAttribute('CTL_ADQ_M')
		if readch != 0:
			val = True
		else:
			val = False
		self.logMessage("getAdcRunState(): ADC run=%s"%val, self.DEBUG)
		return val

	def getFWVersion(self):
		version = self._alindev.getFWVersion()
		self.logMessage("getFWVersion(): Version: %s"%version, self.DEBUG)
		return version

	def setVoltageRange(self, vrange=0):
		attr = self._alindev.getAttributeInfo('CTL_ADC_VOLT_RAGE')
		if attr is not None and attr != {}:
			range = (2**attr['size']-1)
			if vrange>range:
				self.logMessage("setVoltageRange(): Value out of range => %s."%str(vrange), self.ERROR)
				return
			
			self.device.writeAttribute('CTL_ADC_VOLT_RAGE',vrange)
			self.logMessage("setVoltageRange(): Voltage Range set to %s."%str(vrange), self.DEBUG)
		else:
			self.logMessage("setVoltageRange(): Failed to read attribute info...", self.ERROR)

	def getVoltageRange(self):
		readch = self._alindev.readAttribute('CTL_ADC_VOLT_RAGE')
		self.logMessage("getVoltageRange(): Range read=%s"%str(readch), self.DEBUG)
		return readch
	
	def setOversamplig(self, ovsamp=0):
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

	def getOversampling(self):
		readch = self._alindev.readAttribute('CTL_ADC_OS')
		self.logMessage("getOversampling(): Oversampling read=%s"%str(readch), self.DEBUG)
		return readch
	
	def getInstantCurrent(self, ch):
		readch = self._alindev.readAttribute(ch)
		if readch>0x7fffffff:
			readch-=0x100000000
		readch = round((readch*10)/131072.,6)
		self.logMessage("getInstantCurrent=%s value=%s"%(str(ch),str(readch)), self.DEBUG)

		return readch


