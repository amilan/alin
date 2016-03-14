## @package memory.py 
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

from alin.base import AlinDevice
from alin.base import AlinLog

from distutils.sysconfig import get_python_lib

__CONFIG_FILE__ = "Config"
__CONFIG_MASK__ = "MEMORY_"

class Memory(AlinLog):
	def __init__(self, dev='WB-HRMY-MEMORY', debug=False):
		AlinLog.__init__(self, debug=False, loggerName='Memory')		

		self._debug = debug
		self._debuglevel = 40
		self._device = dev
		# Get default configuration from config file
		self.getConfigData()

		self._alindev = AlinDevice(debug=self._debug, device=self._device)
		
		self._memmng_thread = None
		
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
		
		#self._alindev.setLogLevel(self._debuglevel)

	def configureMemory(self):
		#Configuration of memory block
		self.logMessage("configureMemory(): Configuration of memory block", self.INFO)

		try:
			# Resets data in Memory
			self._alindev.writeAttribute('ctl_RST',1)
			# Save all the data after the trigger(0).
			self._alindev.writeAttribute('ctl_OnTrigger',0)
			#  When this bit is chnged from 0 to 1 all memory is deleted.
			self._alindev.writeAttribute('ctl_save',1)
			# When this Data ID is received Trigger is generated.
			self._alindev.writeAttribute('ctl_TRIGID',0x01)
			# Mask of ID, only the bits set at 1 will be checked to identify the data to save.
			# DATAID & IDMASK == ID & IDMASK
			self._alindev.writeAttribute('ctl_IDMask',0)
			self._alindev.writeAttribute('ctl_RST',0)
		except Exception, e:
			self.logMessage("configureMemory() Not possible due to: %s"%str(e),self.ERROR)
			
		
	def getMemoryLenData(self):
		#self.logMessage("getMemoryLenData(): Configuration of memory block", self.INFO)
		retval = None
		try:
			retval = self._alindev.readAttribute('Len_nDATA')
			self.logMessage("getMemoryLenData(): len data = %s"%str(retval), self.INFO)
		except Exception, e:
			self.logMessage("getMemoryLenData() Not possible due to: %s"%str(e),self.ERROR)
			
		return retval
	
	def getMemoryLastData(self, ndata=0):
		self.logMessage("getMemoryLastData(): Returns the last %d values in memory"%ndata, self.INFO)
		
		retval = []
		if ndata != 0:
			try:
				for i in range(0, ndata):
					if self._alindev.readAttribute('Len_nDATA') != 0:
						data = {}
						data['id'] = self._alindev.readAttribute('v_id')
						data['timestamp'] = self._alindev.readAttribute('v_T_stamp')
						data['data'] = self._alindev.readAttribute('v_data')
						retval.append(data)
					else:
						self.logMessage("getMemoryLenData() Buffer empty",self.INFO)
						break
			except Exception, e:
				self.logMessage("getMemoryLenData() Not possible due to: %s"%str(e),self.ERROR)
		
		return retval
	
	def startMemoryManagement(self):
		self.logMessage("startMemoryManagement() Starting thread....",self.INFO)
		self._memmng_thread = None
		try:
			self._memmng_thread = MemoryMangementThread(self, debug=self._debug)
			self._memmng_thread.start()
			self.logMessage("startMemoryManagement() Thread started",self.INFO)
		except Exception, e:
			self.logMessage("startMemoryManagement() Not possible to start thread due to: %s"%str(e),self.ERROR)
		
	def stopMemoryManagement(self):
		self.logMessage("stopMemoryManagement() Stopping thread....",self.INFO)
		if self._memmng_thread is not None:
			self._memmng_thread.end()
		
		while not self._memmng_thread.getProcessEnded():
			self.logMessage("stop(): Waiting harmony process to die", self.INFO)
			time.sleep(0.5)
			pass  
		
		self.logMessage("stopMemoryManagement() Thread stop", self.INFO)
		
	def getMemoryBuffer(self, id_mask):
		self.logMessage("getMemoryBuffer(): Id mask=%s"%str(id_mask),self.INFO)
		ret_val = []
		if self._memmng_thread is not None:
			ret_val = self._memmng_thread.getBuffer(id_mask)
			
		return ret_val
		
	def clearMemoryBuffer(self, id_mask):
		self.logMessage("clearMemoryBuffer(): clearing buffer %s"%str(id_mask),self.INFO)
		if self._memmng_thread is not None:
			ret_val = self._memmng_thread.clearBuffer(id_mask)
			
	def setBufferLenght(self, id_mask, length):
		self.logMessage("setBufferLenght(): setting buffer %s length %s"%(str(id_mask),str(length)),self.INFO)
		if self._memmng_thread is not None:
			self._memmng_thread.setBufferlenght(id_mask, length)
		
class MemoryMangementThread(threading.Thread):
	def __init__(self, parent=None, debug=None):
		threading.Thread.__init__(self)
		self._parent = parent
		
		self._endProcess = False
		self._processEnded = False
		
		self._thr_databuffer = [[] for x in range(0,256)] # Maximum number of possible ID
		self._thr_databuffer_maxlenght = [None for x in range(0,256)]
		
	def end(self):
		self._endProcess = True
		
	def getProcessEnded(self):
		return self._processEnded
	
	def setBufferlenght(self, id, lenght):
		self._thr_databuffer_maxlenght[id] = lenght
		
	def getBuffer(self, id):
		return  self._thr_databuffer[id]
	
	def clearBuffer(self, id):
		self._thr_databuffer[id] = []
	
	def run(self): 
		while not (self._endProcess):
			rdlen = self._parent.getMemoryLenData()
			if rdlen != 0 and rdlen is not None:				
				data = self._parent.getMemoryLastData(rdlen)

				for el in data:
					rd_id = el['id']
					rd_ts = el['timestamp']
					rd_data = el['data']
					maxlenght = self._thr_databuffer_maxlenght[rd_id] 
					
					if maxlenght is not None and len(self._thr_databuffer[rd_id])<maxlenght:
						self._thr_databuffer[rd_id].append([rd_ts,rd_data])
						self._parent.logMessage("MemoryMangementThread(): Data get Id=%s TimeStamp=%s Value=%s"%(str(rd_id),str(rd_ts),str(rd_data)),self._parent.DEBUG)
			
			time.sleep(0.1)
		self._processEnded = True

		
		

