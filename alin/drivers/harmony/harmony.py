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

import os, time
import threading

from random import uniform

from alin.base import AlinDevice
from alin.base import AlinLog

from adccore import AdcCore
from crossbar import CrossBar
from idgen import IDGen
from memory import Memory 

from distutils.sysconfig import get_python_lib

__CONFIG_FILE__ = "Config"
__CONFIG_MASK__ = "HARMONY_"

class Harmony(AlinLog):
	def __init__(self, dev=None, debug=False):
		AlinLog.__init__(self, debug=False, loggerName='Harmony')

		self._debug = debug
		self._debuglevel = 40
		self._device = dev
		# Get default configuration from config file
		self.getConfigData()

		self._dMEM = Memory(debug=self._debug)
		self._dIDGEN = IDGen(debug=self._debug)
		self._dHRMYCB = CrossBar(debug=self._debug)
		self._dADCCORE = AdcCore(debug=self._debug)
		
		self._ch_readdata = [[] for x in range(0,4)]
		self._ch_range = [100 for x in range(0,4)]
		self._ch_trgtime = [1 for x in range(0,4)]
		
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

		self._dMEM.setLogLevel(self._debuglevel)
		self._dIDGEN.setLogLevel(self._debuglevel)
		self._dHRMYCB.setLogLevel(self._debuglevel)
		self._dADCCORE.setLogLevel(self._debuglevel)
			
	def start(self):
		self.logMessage("start():", self.INFO)
		
		# 1. configure ADC and set it to Run
		self.logMessage("configureHarmony(): Confure ADC", self.INFO)
		if not self._dADCCORE.getAdcRunState():
			self._dADCCORE.startAdc()
		
		#Configuration of memory block
		self.logMessage("configureHarmony(): Configuration of memory block", self.INFO)
		self._dMEM.configureMemory()
		
		#Configuration of IDGEN Block
		self.logMessage("configureHarmony(): Configuration of memory block", self.INFO)
		self._dIDGEN.configureIDGen()
		
		#Configuration of CrossBar
		self.logMessage("configureHarmony(): Configuration of crossbar block", self.INFO)
		self._dHRMYCB.configureCrossbar()
		
		# Creates Main Harmony thread
		self._dMEM.startMemoryManagement()
		for x in range(0,4):
			self.setRange(x, self._ch_range[x])
			
		self.logMessage("start(): Harmony module started", self.INFO)
		
	def stop(self):
		self.logMessage("stop(): End Harmony control module", self.INFO)
		
		# Stop HW triggers
		for i in range(0,4):
			self.stopSWTRigger(i)
				
		self._dMEM.stopMemoryManagement()
				
		self.logMessage("stop(): Harmony process dead!!", self.INFO)
			
	def getInstantCurrent(self, channel):
		curr = self._dADCCORE.getInstantCurrent(channel)
		self.logMessage("getInstantCurrent(): Channel=%s Current=%s"%(channel,str(curr)), self.INFO)
		return curr

	def getFWVersion(self):
		ver = self._dADCCORE.getFWVersion()
		self.logMessage("getFWVersion(): FW version %s"%ver, self.INFO)
		return ver
	
	def getCurrent(self, channel):
		def convertCurrent(readch):
			if readch>0x7fffffff:
				readch-=0x100000000
			readch = round((readch*10)/131072.,6)
			return readch
		
		self.logMessage("getCurrent(): Channel=%d reading form fast bus"%channel, self.INFO)

		chid = self._dIDGEN.getID(channel)
		retval = self._dMEM.getMemoryBuffer(chid)
		if len(retval) != self._ch_range[channel]:
			self.logMessage("getInstantCurrent(): Channel=%d Buffer not filled yet"%channel, self.INFO)
			return []
		else:
			#self._dMEM.clearMemoryBuffer(chid)
			self._ch_readdata[channel] = []
			for el in retval:
				self._ch_readdata[channel].append(convertCurrent(el[1]))
			self.logMessage("getInstantCurrent(): Channel=%d with ID=%s Done!"%(channel,hex(chid)), self.INFO)
			retval = self._ch_readdata[channel]

		return retval
	
	def setRange(self, channel, n_points):
		self.logMessage("setRange(): Channel=%d points set to %d"%(channel, n_points), self.INFO)
		self._ch_range[channel] = n_points

		chid = self._dIDGEN.getID(channel)
		self._dMEM.setBufferLenght(chid ,self._ch_range[channel])

	def getRange(self, channel):
		points = self._ch_range[channel]
		self.logMessage("getRange(): Channel=%d points set to %d"%(channel, points), self.INFO)
		return points
	
	def setTriggerTime(self, channel, time):
		self.logMessage("setTriggerTime(): Channel=%d time set to %d second"%(channel, time), self.INFO)
		self._ch_trgtime[channel] = time
	
	def getTriggerTime(self, channel):
		time = self._ch_trgtime[channel]
		self.logMessage("getTriggerTime(): Channel=%d time set to %d second"%(channel, time), self.INFO)
		return time	
	
	def getAverageCurrent(self, channel):
		self.logMessage("getAverageCurrent(): Channel=%d "%channel, self.INFO)
		# Read channel data fisrt
		self.getCurrent(channel)
		
		avg = 0
		datalen = len(self._ch_readdata[channel])
		if datalen != 0:
			for dt in self._ch_readdata[channel]:
				avg += dt
				
			avg = avg/datalen
		
		self.logMessage("getAverageCurrent(): Channel=%d AverageCurrent=%s"%(channel, str(avg)), self.INFO)
		return avg

	def startSWTrigger(self, channel):
		self.logMessage("startSWTrigger(): Channel=%d"%(channel), self.INFO)
		try:
			chid = self._dIDGEN.getID(channel)
			self._dMEM.clearMemoryBuffer(chid)
			self._dIDGEN.startIDGenManagement(channel, range=self._ch_range[channel], time=self._ch_trgtime[channel])
		except Exception, e:
			self.logMessage("startSWTrigger(): not started due to %s"%str(e), self.ERROR)
		
	def stopSWTrigger(self, channel):
		self.logMessage("stopSWTRigger(): Channel=%d"%(channel), self.INFO)		
		try:
			self._dIDGEN.stopIDGenManagement(channel)
		except Exception, e:
			self.logMessage("stopSWTRigger(): not started due to %s"%str(e), self.ERROR)
		
	def getSWTrigger(self, channel):
		self.logMessage("getSWTRigger(): Channel=%d"%(channel), self.INFO)
		retval = False
		try:
			retval = self._dIDGEN.getIDGenManagement(channel)
		except Exception, e:
			self.logMessage("getSWTRigger(): not started due to %s"%str(e), self.ERROR)
		
		return retval
	
	def getMemoryMLen(self):
		retval = self._dHRMYCB.getCrossMLen()
		self.logMessage("getMemoryMLen(): Number of messages send witout a free slot=%s"%str(retval), self.INFO)
		return retval

	def getMemoryActReq(self):
		retval = self._dHRMYCB.getCrossActReq()
		self.logMessage("getMemoryMLen(): Number of request active=%s"%str(retval), self.INFO)
		return retval

	def getMemorySgnAct(self):
		retval = self._dHRMYCB.getCrossSgnAct()
		self.logMessage("getCrossSgnAct(): Number of messages send witout a free slot=%s"%str(retval), self.INFO)
		return retval



