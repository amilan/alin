## @package ADC_drv.py 
#    File containing the I2C driver for the ADC driver ADS7828
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
import smbus

_CONFIG_MASK = "ADS7828_"

_DEFAULT_I2C_ADDRESS 	= 0x48
_DEFAULT_I2C_BUS 		= 8

_ACK_VALUE = 0x08
_NACK_VALUE = 0x15

_REGISTERS 	= {'VSENSE_I_ISO'	: 0x84,
				'VSENSE_I_VS'	: 0x94,
				'VSENSE_I_SPEC'	: 0xA4,
				'VSENSE_I_VCC'	: 0xC4,
				'VSENSE_I_AUX'	: 0xD4,
				}

class ADS7828(AlinLog):
	def __init__(self, debug=False):
		AlinLog.__init__(self, debug=False, loggerName='ADS7828')
		
		# Get default configuration from config file
		self._debug = debug
		self.configure()
		
		self.logMessage("__init__() Initialized ", self.DEBUG)
		

	def configure(self):
		# Get default configuration from config file
		configDict = getConfigData(_CONFIG_MASK)
		self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else debug
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

	def status(self):
		try:
			self.i2c.read_byte(self._i2c_address)
			return True
		except:
			return False
	
	def readAddress(self, address):
		self.logMessage("readAddress() address %s"%(hex(address)), self.DEBUG)
		ret_value = []
		try:
			#self.i2c.write_byte(self._i2c_address, address)
			ret_value = self.i2c.read_i2c_block_data(self._i2c_address,address,2)
			self.logMessage("readRegister() Returned value=%s"%str(ret_value), self.DEBUG)			
		except Exception, e:
			self.logMessage("readAddress() Error!! Not possible access I2C due to %s"%str(e), self.ERROR)
		
		return ret_value
	
	def getRegister(self, register):
		val = None
		try:
			self.logMessage("getRegister() Register %s "%str(register), self.DEBUG)
		
			#val = self.readAddress(_REGISTERS[register])
			ret_val = self.readAddress(_REGISTERS[register])
			val = ((ret_val[0]&0x0F)<<0x08) + (ret_val[1]&0xFF)
		except Exception, e:
			self.logMessage("getRegister() Error!! Not possible get register due to %s"%str(e), self.ERROR)
		
		return val
