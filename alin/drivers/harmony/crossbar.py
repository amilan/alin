## @package crossbar.py 
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

from alin.base import AlinDevice
from alin.base import AlinLog

from distutils.sysconfig import get_python_lib

__CONFIG_FILE__ = "Config"
__CONFIG_MASK__ = "CROSSBAR_"


class CrossBar(AlinLog):
	def __init__(self, dev='WB-HRMY-CROSSBAR', debug=False):
		AlinLog.__init__(self, debug=False, loggerName='CrossBar')		

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
							self.logMessage("%s::getConfigData(): %s set to %s"%(__CONFIG_MASK__, key.upper(), self._debug),self.INFO)
						except Exception, e:
							self.logMessage("%s::getConfigData(): Can't get %s flag %s"%(__CONFIG_MASK__, key.upper(), self._debug, str(e)),self.ERROR)
		except Exception, e:
			self.logMessage("%s::getConfigData():: Not possible to get config file due to:"%__CONFIG_MASK__,self.ERROR)
			self.logMessage(str(e),self.ERROR)
			
	def setLogLevel(self, level):
		self._debuglevel = level 
		self.logLevel(self._debuglevel)
		
		self._alindev.setLogLevel(self._debuglevel)

	def configureCrossbar(self):
		#Configuration of memory block
		self.logMessage("configureCrossbar(): Nothing to do!!!!!!!", self.DEBUG)
		pass
		
	def getCrossMLen(self):
		retval = None
		try:
			# Maximum number of messages send without a free slot
			retval = self._alindev.readAttribute('ID_DIAGNJD_MLEN')
			self.logMessage("getCrossMLen(): Number of messages send witout a free slot=%s"%str(retval), self.DEBUG)
		except Exception, e:
			self.logMessage("getCrossMLen() Not possible due to: %s"%str(e),self.ERROR)
		
		return retval

	def getCrossActReq(self):
		retval = None
		try:
			# Maximum number of requests active simultaiusly
			retval = self._alindev.readAttribute('ID_DIAGNJDRD_MREQ')
			self.logMessage("getCrossActReq(): Number of request active=%s"%str(retval), self.DEBUG)
		except Exception, e:
			self.logMessage("getCrossActReq() Not possible due to: %s"%str(e),self.ERROR)
		
		return retval

	def getCrossSgnAct(self):
		retval = None
		try:
			# Maximum time device has request signal active.
			retval = self._alindev.readAttribute('ID_DIAGNJDRDRD_MTREQ')
			self.logMessage("getCrossSgnAct(): Maximum time device has request signal active=%s"%str(retval), self.DEBUG)
		except Exception, e:
			self.logMessage("getCrossSgnAct() Not possible due to: %s"%str(e),self.ERROR)
		
		return retval
		

