## @package idgen.py 
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

from distutils.sysconfig import get_python_lib

__CONFIG_FILE__ = "Config"
__CONFIG_MASK__ = "IDGEN_"

class IDGen(AlinLog):
	
	# Supported data types
	CHANNEL_1_TYPE = 0
	CHANNEL_2_TYPE = 1
	CHANNEL_3_TYPE = 2
	CHANNEL_4_TYPE = 3
	N_TYPES_SUPPORTED = 4 # last +1

	# Defualt ID for supported data types	
	DEFAULT_CHANNEL_1_ID = 0x01
	DEFAULT_CHANNEL_2_ID = 0x02
	DEFAULT_CHANNEL_3_ID = 0x03
	DEFAULT_CHANNEL_4_ID = 0x04
	
	def __init__(self, dev='WB-HRMY-ID-GEN', debug=False):
		AlinLog.__init__(self, debug=False, loggerName='IDGen')		

		self._debug = debug
		self._debuglevel = 40
		self._device = dev
		
		self._ch1ID = self.DEFAULT_CHANNEL_1_ID
		self._ch2ID = self.DEFAULT_CHANNEL_2_ID
		self._ch3ID = self.DEFAULT_CHANNEL_3_ID
		self._ch4ID = self.DEFAULT_CHANNEL_4_ID
		
		self._idgen_mngthread = [None for x in range(0,4)]
		
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
						"CHANNEL_1_ID_":[self._ch1ID,"int"],
						"CHANNEL_2_ID_":[self._ch2ID,"int"],
						"CHANNEL_3_ID_":[self._ch3ID,"int"],
						"CHANNEL_4_ID_":[self._ch4ID,"int"],
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
		
		#self._alindev.setLogLevel(self._debuglevel)

	def configureIDGen(self):
		#Configuration of memory block
		self.logMessage("configureIDGen(): Configuration of memory block", self.INFO)
		
		try:
			# Each time this ID is received a message is generated in Harmony BUS
			self._alindev.writeAttribute('ID_gen_ctl_TriggerID',0x51)
			# Sends the Data Message when it is set.
			self._alindev.writeAttribute('ID_gen_ctl_mTrig',0)
			# If it is set to 1, the data mesage is send in Harmony bus each time
			# a Trigger ID is received.
			self._alindev.writeAttribute('ID_gen_ctl_ETI',0)
			# If it is set to 1, the mesage's timestamp is internally generated.
			self._alindev.writeAttribute('ID_gen_ctl_CLKE',0)
			# This bit indicates that data is still not send to the Harmony Bus
			# and an error can be generated if a new data request is generated.
			self._alindev.readAttribute('ID_gen_ctl_RDY')
		except Exception, e:
			self.logMessage("configureIDGen() Not possible due to: %s"%str(e),self.ERROR)
			
		
	def generateIDGenData(self, datatype=None, data=0, ts=0):
		self.logMessage("generateIDGenData():Generating datatype=%s with data=%s and timestamp=%s"%(str(datatype), str(data), str(ts)), self.INFO)
		try:
			iddata = self.getID(datatype)
			if iddata is not None:
				self._alindev.writeAttribute('TS_ID_ID_OUT',iddata)
				self._alindev.writeAttribute('TS_ID_TimeStamp',ts)
				self._alindev.writeAttribute('DATA_GEN_DATA',data)
				self._alindev.writeAttribute('ID_gen_ctl_mTrig', 1)
			else:
				self.logMessage("generateIDGenData() Unsupported data type %s"%str(datatype),self.ERROR)
				return False
		except Exception, e:
			self.logMessage("generateIDGenData() Not possible due to: %s"%str(e),self.ERROR)
			return False
		
		return True
	
	def getID(self, datatype):
		if datatype is not None and datatype < self.N_TYPES_SUPPORTED:
			if datatype == self.CHANNEL_1_TYPE:
				return self._ch1ID
			elif datatype == self.CHANNEL_2_TYPE:
				return self._ch2ID
			elif datatype == self.CHANNEL_3_TYPE:
				return self._ch3ID
			elif datatype == self.CHANNEL_4_TYPE:
				return self._ch4ID
			else:
				return None
		return None

	def startIDGenManagement(self, channel, range=100, time=1):
		self.logMessage("startIDGenManagement() Starting ID Gen thread %s channel...."%str(channel),self.INFO)
		
		if self._idgen_mngthread[channel] is not None:
			self.stopIDGenManagement(channel)

		try:
			self._idgen_mngthread[channel] = IDGenManagementThread(self,channel=channel, points=range, time=time)
			self._idgen_mngthread[channel].start()
			self.logMessage("startIDGenManagement() Thread started every %s secs with a range of %s samples"%(str(time),str(range)),self.INFO)
		except Exception, e:
			self.logMessage("startIDGenManagement() Not possible to start thread due to: %s"%str(e),self.ERROR)
		
	def stopIDGenManagement(self, channel):
		self.logMessage("stopIDGenManagement() Stopping thread....",self.INFO)
		if self._idgen_mngthread[channel] is not None:
			self._idgen_mngthread[channel].end()
			
			while not self._idgen_mngthread[channel].getProcessEnded():
				print "Waiting to finish process"
				time.sleep(0.5)
				
			self._idgen_mngthread[channel] = None
		
		self.logMessage("stopIDGenManagement() Thread stop", self.INFO)

	def getIDGenManagement(self, channel):
		self.logMessage("getIDGenManagement() Channel %s "%str(channel),self.INFO)
		if self._idgen_mngthread[channel] is not None and self._idgen_mngthread[channel].getProcessEnded() == False:
			retval = True
		else:
			retval = False
		self.logMessage("getIDGenManagement() Thread alive=%s"%str(retval), self.INFO)
		return retval


class IDGenManagementThread(threading.Thread):
	def __init__(self, parent=None, time=1, channel=None, points=1):
		threading.Thread.__init__(self)
		self._parent = parent
		
		self._time = time
		self._channel = channel
		self._npoints = points
		
		self._endProcess = False
		self._processEnded = False
	
	def end(self):
		self._endProcess = True
		
	def getProcessEnded(self):
		return self._processEnded

	def run(self): 
		#while not (self._endProcess):
		if self._channel is not None:
			for i in range(0, self._npoints):
				ts = i*1024
				if self._channel == 0: # Channel 1
					tmp = uniform(-1,1)
				if self._channel == 1: # Channel 2
					tmp = uniform(-5,5)
				if self._channel == 2: # Channel 3
					tmp = uniform(-10,10)
				if self._channel == 3: # Channel 4
					tmp = uniform(-100,100)
				if tmp<0:
					value = (0x100000000-int((round(tmp,6)*131072)/10))
				else:
					value = int((round(tmp,6)*131072)/10)
				self._parent.generateIDGenData(self._channel, value, ts)
		#	time.sleep(self._time)
		self._processEnded = True
