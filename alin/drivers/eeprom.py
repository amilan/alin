## @package ADC_drv.py 
#    File containing the I2C driver for the EEPROM driver 24AA02UIDT
#
#    Author = "Manuel Broseta"
#    Copyright = "Copyright 2017, ALBA"
#    Version = "1.0"
#    Email = "mbroseta@cells.es"
#    Status = "Development"
#    History:
#              9/05/2016 - file created by Manolo Broseta


from alin.base import AlinLog
from alin.base import getConfigData
import smbus

_CONFIG_MASK = "EEPROM_"

_DEFAULT_I2C_ADDRESS 	= 0x50
_DEFAULT_I2C_BUS 		= 8

_ACK_VALUE = 0x08
_NACK_VALUE = 0x15

class EEPROM(AlinLog):
	def __init__(self, debug=False):
		AlinLog.__init__(self, debug=False, loggerName='EEPROM ')
		
		# Get default configuration from config file
		self._debug = debug
		self.configure()
		
		self.logMessage("__init__() Initialized ", self.DEBUG)
		

	def configure(self):
		# Get default configuration from config file
		configDict = getConfigData(_CONFIG_MASK)
		self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else self._debug
		self._debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 40
		self._i2c_address = int(configDict["I2C_ADDRESS_"],16) if "I2C_ADDRESS_" in configDict.keys() else _DEFAULT_I2C_ADDRESS
		self._i2c_busnum = int(configDict["I2C_BUS_"]) if "I2C_BUS_" in configDict.keys() else _DEFAULT_I2C_BUS

		try:
			self.i2c = smbus.SMBus(self._i2c_busnum)
			self.i2c.read_byte(self._i2c_address)
			self.logMessage("configure() I2C device found at bus %s with address %s"%(str(self._i2c_busnum),hex(self._i2c_address)), self.INFO)
		except:
			# I2C device not found at specified bus number.
			# Search rotuine to find device
			self.i2c = None
		
			self.logMessage("configure() I2C device not found at bus %s. Starting I2C search..."%str(self._i2c_busnum), self.INFO)
			i2c_list = []
			for i in range(0,20):
				try:
					tmp = smbus.SMBus(i)
					i2c_list.append(tmp)
				except:
					break
			
			for i in range(len(i2c_list)-1,-1,-1):
				try:
					i2c_list[i].read_byte(self._i2c_address)
					self.i2c = i2c_list[i]
					self._i2c_busnum = i
					self.logMessage("configure() I2C device found in search at bus %s with address %s"%(str(self._i2c_busnum),hex(self._i2c_address)), self.INFO)
					break;
				except:
					pass
			if self.i2c is None:
				self.logMessage("configure() I2C device not found!!", self.ERROR)
		
		# Logging
		self.logLevel(self._debuglevel)
		self.logEnable(self._debug)
		
		self.logMessage("configure() %s configured"%_CONFIG_MASK, self.INFO)		
		
	def init(self):
		self.logMessage("init()", self.DEBUG)
		pass

	def readAddress(self, address=0, num_data=0):
		self.logMessage("readAddress() address %s"%(hex(address)), self.DEBUG)
		ret_value = []
		try:
			#self.i2c.write_byte(self._i2c_address, address)
			ret_value = self.i2c.read_i2c_block_data(self._i2c_address,address,num_data)
			self.logMessage("readAddress() Returned value=%s"%str(', '.join(map(hex, ret_value))), self.DEBUG)			
		except Exception, e:
			self.logMessage("readAddress() Error!! Not possible access I2C due to %s"%str(e), self.ERROR)
		
		return ret_value
	
	def writeAddress(self, address=0, data=[]):
		self.logMessage("writeAddress() address %s"%(hex(address)), self.DEBUG)
		try:
			self.i2c.write_i2c_block_data(self._i2c_address, address, data)
			self.logMessage("writeAddress() Write data=%s"%str(', '.join(map(hex, data))), self.DEBUG)         
		except Exception, e:
			self.logMessage("writeAddress() Error!! Not possible access I2C due to %s"%str(e), self.ERROR)


