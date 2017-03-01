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
from alin.base import getConfigData

_CONFIG_MASK = "CROSSBAR_"

class CrossBar(AlinDevice):
	def __init__(self, dev='WB-HRMY-CROSSBAR', number=0, debug=False):
		AlinDevice.__init__(self, device=dev, number=number, debug=debug, logger='CROSSBAR')		

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
		self.logMessage("init(): Nothing to do!!!!!!!", self.DEBUG)
		pass
		
	def getCrossMLen(self):
		retval = None
		try:
			# Maximum number of messages send without a free slot
			retval = self.readAttribute('ID_DIAGNJD_MLEN')
			self.logMessage("getCrossMLen(): Number of messages send witout a free slot=%s"%str(retval), self.DEBUG)
		except Exception, e:
			self.logMessage("getCrossMLen() Not possible due to: %s"%str(e),self.ERROR)
		
		return retval

	def getCrossActReq(self):
		retval = None
		try:
			# Maximum number of requests active simultaiusly
			retval = self.readAttribute('ID_DIAGNJDRD_MREQ')
			self.logMessage("getCrossActReq(): Number of request active=%s"%str(retval), self.DEBUG)
		except Exception, e:
			self.logMessage("getCrossActReq() Not possible due to: %s"%str(e),self.ERROR)
		
		return retval

	def getCrossSgnAct(self):
		retval = None
		try:
			# Maximum time device has request signal active.
			retval = self.readAttribute('ID_DIAGNJDRDRD_MTREQ')
			self.logMessage("getCrossSgnAct(): Maximum time device has request signal active=%s"%str(retval), self.DEBUG)
		except Exception, e:
			self.logMessage("getCrossSgnAct() Not possible due to: %s"%str(e),self.ERROR)
		
		return retval
		

