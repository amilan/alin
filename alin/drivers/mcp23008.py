## @package PExp_drv.py 
#    File containing the I2C driver for the Port Expander MCP23008
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


_CONFIG_MASK = "PEXPDRV_"

_DEFAULT_I2C_ADDRESS = 0x20
_DEFAULT_I2C_BUS = 8

_REG_ADDRESS = {'INIT_ADD':0x00,
				'CTRL_ADD':0x09
				}

# reg_name = (address, mask, pos)
_REGISTERS = {'INIT':('INIT_ADD',0xff,0),
			  'CTRL_ISO': ('CTRL_ADD', 0x01, 0x00),
			  'CTRL_VCC': ('CTRL_ADD', 0x01, 0x01),
			  'CTRL_VS':  ('CTRL_ADD', 0x01, 0x02),
			  'CTRL_VAUX': ('CTRL_ADD', 0x01, 0x03),
			}

class MCP23008(AlinLog):
	def __init__(self, debug=False):
		AlinLog.__init__(self, debug=False, loggerName='MCP23008')
		
		# Get default configuration from config file
		self._debug = debug
		self.configure()
	
		self._regValues = {}
		for reg in _REG_ADDRESS.keys():
			self._regValues[_REG_ADDRESS[reg]] = 0
		
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
		
		# Initialize PExp ports as output
		self.writeRegister('INIT', 0x0)
		
		self.writeRegister('CTRL_ISO', 0x1)
		self.writeRegister('CTRL_VCC', 0x1)
		self.writeRegister('CTRL_VS', 0x1)
		
	def status(self):
		try:
			self.i2c.read_byte(self._i2c_address)
			return True
		except:
			return False

	def writeRegister(self, register, value):
		try:
			self.logMessage("writeRegister() Register %s "%str(register), self.DEBUG)
			
			address = _REG_ADDRESS[_REGISTERS[register][0]]
			mask = _REGISTERS[register][1]
			bit_pos = _REGISTERS[register][2]
			aux_value = self._regValues[address]
			
			aux_value = aux_value & (0xFF-(mask<<bit_pos))
			aux_value = aux_value | ((value & mask)<<bit_pos)
			
			self.i2c.write_byte_data(self._i2c_address, address, aux_value)
			self._regValues[address] = aux_value
			
			self.logMessage("writeRegister() address %s value %s"%(hex(address), hex(aux_value)), self.DEBUG)
		except Exception, e:
			self.logMessage("writeRegister() Error!! Not possible to access I2C due to %s"%str(e), self.ERROR)
			
	def readRegister(self, register):
		aux_value = None
		try:
			self.logMessage("readRegister() Register %s "%str(register), self.DEBUG)
			
			address = _REG_ADDRESS[_REGISTERS[register][0]]
			mask = _REGISTERS[register][1]
			bit_pos = _REGISTERS[register][2]
			
			aux_value = self.i2c.read_byte_data(self._i2c_address, address)
			self._regValues[address] = aux_value
			
			aux_value = (aux_value & (mask<<bit_pos))
			aux_value = (aux_value >>bit_pos) & mask
			self.logMessage("readRegister() address %s value %s"%(hex(address), hex(aux_value)), self.DEBUG)
		except Exception, e:
			self.logMessage("readRegister() Error!! Not possible to access I2C due to %s"%str(e), self.ERROR)
			
		return aux_value
