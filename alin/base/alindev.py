## @package alindev.py 
#	File containing the device class, to access device registers
#
#	Author = "Manolo Broseta"
#	Copyright = "Copyright 2015, ALBA"
#	Version = "1.1"
#	Email = "mbroseta@cells.es"
#	Status = "Development"
#	History:
#   29/07/2015 - file created
#	20/10/2015 - Several modifications done
#	             Doxygen detailed info added

__author__ = "Manolo Broseta"
__copyright__ = "Copyright 2015, ALBA"
__license__ = "GPLv3 or later"
__version__ = "1.0"
__email__ = "mbroseta@cells.es"
__status__ = "Development"


from alin import *
from alinlog import AlinLog
from configdata import getConfigData
import os.path
import pickle


_CONFIG_MASK = "ALINDEV_"
_OFFSET = 0x00 #0x100

## alinDevice class
#
# Main class that links the device map pickel file created with the coresponding memory area defined in the SDB
# It provides functions to get device information and to read/write attributes of that device
class AlinDevice(AlinLog):
	## The constructor.
	#  @param device (not mandatory) Device to controls
	def __init__(self, device=None, number=0, debug=False, logger='AlinDev'):
		AlinLog.__init__(self, debug=False, loggerName=logger)
		
		# Get default configuration from config file
		configDict = getConfigData(_CONFIG_MASK)
		self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else debug
		self._debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 40
		
		self._devMap = {}

		self.sdbDrv = AlinSDB(_OFFSET, debug=self._debuglevel)
		self.sdbDrv.getData(_OFFSET)
		
		#self.__device_folder = os.path.abspath(os.path.dirname(__file__))+"/deviceslib/"
		self.__device_folder = get_python_lib()+"/alin/deviceslib/"
		
		# Logging
		self.setLogLevel(self._debuglevel)
		self.logEnable(self._debug)
		
		if device is not None:
			self.setDevice(device, number)
		
		self.logMessage("__init__() Initialized ", self.DEBUG)
		
	def setLogLevel(self, level):
		self._debuglevel = level
		self.logLevel(self._debuglevel)
		
		self.sdbDrv.setLogLevel(self._debuglevel)
		
	def getFWVersion(self):
		self.logMessage("getFWVersion()", self.DEBUG)
		return self.sdbDrv.getFWVersion()

	## setDevice(device)
	#  This function reads the memory, searching for the prodcutID ad vendroID specified. When it is found it stores the falue for the memory
	#  address location where the device is located. A pickle file, named as the device, should exits to complete the set fo the Device. The pickle file
	#  contains a dict with all the device registers mapping
	#  @param device Device to read the information. This is a string parametar that should have the following structure:  PorductID:VendorID
	def setDevice(self, devname, devnum=0):
		
		devname = devname.upper()
		dev_count = 0
		pickfile = self.__device_folder+devname
		self.logMessage("setDevice::Reading %s pickle file"%pickfile, self.DEBUG)

		if not os.path.isfile(pickfile):
			self.logMessage("setDevice::%s device register map not found!!"%devname, self.DEBUG)
                        return None
		else:
			self.logMessage("setDevice::%s device found!"%devname, self.DEBUG)
		
		self._devMap = {}
		try:
			with open(pickfile) as output:
				self._devMap = pickle.load(output)
		except Exception, e:
			self.logMessage("setDevice::Problem found while reading %s"%pickfile, self.ERROR)		
			print str(e)
			return None
				
		dev_found = False
		if self._devMap and "vendorid" in self._devMap.keys() and "product" in self._devMap.keys():
			self.vendorId = long(self._devMap["vendorid"],16)
			self.logMessage("setDevice::%s getting vendorID....: %s"%(devname,hex(self.vendorId)), self.DEBUG)
			self.product = long(self._devMap["product"],16)
			self.logMessage("setDevice::%s getting product....: %s"%(devname,hex(self.product)), self.DEBUG)
			self.dev_number = devnum
		
			temp = []
			temp = self.sdbDrv.readData()
			self.initAddress = None
			
			for el in temp:
				if (el['interconnect'] == self.sdbDrv.SDB_RECORD_BRIDGE) or\
					(el['interconnect'] == self.sdbDrv.SDB_RECORD_INTERCONNECT) or\
					(el['interconnect'] == self.sdbDrv.SDB_RECORD_DEVICE):
					vendor = ''.join(['%02x'%a for a in el['vendor']])
					device = ''.join(['%02x'%a for a in el['device']])		
					if  ((self.vendorId == int(vendor,16)) and  self.product == int(device,16)):
						if int(devnum) == int(dev_count): 
							self.initAddress = self.sdbDrv.getAddress(el['first_address'])+el['base_address']
							self.logMessage("setDevice::%s init address found...: %s"%(devname,hex(self.initAddress)), self.DEBUG)
							# Add initial and last address to the map info
							self._devMap['first_address'] = self.initAddress
							self._devMap['last_address'] = self.sdbDrv.getAddress(el['last_address'])+el['base_address']
							dev_found = True							
							break
						else:
							dev_count +=1
			
		if not dev_found:
			self._devMap = {}
			self.logMessage("setDevice::%s Problem found, vendoID or product or device number not found"%devname, self.ERROR)
			return None
		
		return self._devMap

				
	## getDeviceInfo()
	#  This function returns all mapping information for the corresponding device
	#  @return Dict that contains all device information and mapping
	def getDeviceInfo(self):
		self.logMessage("getDeviceInfo::", self.DEBUG)		
		return self._devMap
	
	## getDeviceName()
	#  This function returns the device name which is included in the pickle file
	#  @return String that contains the device name
	def getDeviceName(self):
		if self._devMap and "name" in self._devMap.keys():
			self.logMessage("getDeviceName::", self.DEBUG)		
			return self._devMap["name"]
		else:
			self.logMessage("getDeviceName::Name not availble", self.ERROR)		
		return None		
	
	## getDeviceDescription()
	#  This function returns the device description which is included in the pickle file
	#  @return String that contains the description of the device
	def getDeviceDescription(self):
		if self._devMap and "description" in self._devMap.keys():
			self.logMessage("getDeviceDescription::", self.DEBUG)		
			return self._devMap["description"]
		else:
			self.logMessage("getDeviceDescription::Description not availble", self.ERROR)		
		return None

	## getDeviceData()
	#  This function returns all device information included in the pickle file, including device name, description and register mapping
	#  @return List containing all device data
	def getDeviceData(self):
		devValues = {}
		rd_data = {}
		rd_data = self.sdbDrv.getDeviceMemory(vend=self.vendorId, prod=self.product, devnum=self.dev_number)
		if rd_data and self._devMap:
			for regname in self._devMap['regs'].keys():
				address = self._devMap['regs'][regname]['address']
				position = self._devMap['regs'][regname]['bit_position']
				size = self._devMap['regs'][regname]['size']
				
				if address == 14:
					continue
				
				mask = (2**size - 1) << position
				
				value = rd_data['data'][address]
				value = (value&mask)>>position
				
				devValues[regname.upper()] = value
			self.logMessage("getDeviceData::Read all device data list", self.DEBUG)
		else:
			if self._devMap:
				for regname in self._devMap['regs'].keys():
					value = None
					
					devValues[regname.upper()] = value
			self.logMessage("getDeviceData:Not possible to get the data from Memory!!", self.ERROR)
		
		return devValues

	## getAttributesList()
	#  This function returns the list of attributes defined in the pickle file
	#  @return List containing the list of attributes defined in the pickle file
	def getAttributesList(self):
		if self._devMap:
			valueList = [el for el in self._devMap['regs']]
			self.logMessage("getAttributesList::Attribute list read", self.DEBUG)
		else:
			self.logMessage("getAttributesList::No data found", self.ERROR)
		return valueList

	## writeAttribute(attrName,attrVal)
	#  This function uses the initial device address obtained from the SDB for the device and do the mask wiht the 
	#  information in the pickle file for the register selecter to calculate the proper masked value to write.
	#  Then it uses alinSDB write funciton to apply the corresponding value
	#  @param attrName String containing the attribute name to write
	#  @param attrVal Num with the value to write in the aatribute
	def writeAttribute(self,attrName,attrVal):
		if attrName is not None and self._devMap:
			try:
				attMap = self._devMap['regs'][attrName.upper()]

				address = attMap['address']
				sdb_address = self.initAddress+(address*4)
				position = attMap['bit_position']
				size = attMap['size']
				access = attMap['access'].split()[0]

				mask = (2**size - 1) << position
				
				value = self.sdbDrv.readAddress(sdb_address)

				if access == "WRITE_ONLY" or access == "READ_WRITE":
					inv_mask = 0xffffffff - mask
					value = value & inv_mask
					data = (attrVal&(2**size - 1)) << position
					value = (value | data)
					
					self.sdbDrv.writeAddress(sdb_address,value)
					
					self.logMessage("writeAttribute::Attribute %s address: %s value=%s"%(attrName, hex(sdb_address), hex(value)), self.DEBUG)
				else:
					self.logMessage("writeAttribute::Attribute %s is %s type"%(attrName, access), self.ERROR)
			except Exception, e:
				self.logMessage("writeAttribute::Cannot write %s attribute due to %s"%(attrName, str(e)), self.ERROR)
		else:
			self.logMessage("writeAttribute::Cannot write %s attribute"%attrName, self.ERROR)

	## readAttribute(attrName)
	#  This function uses the initial device address obtained from the SDB to read the value using the alinSDB read
	#  functions. Then it uses the information in the pickle file to apply the proper mask and return the masked value
	#  @param attrName String containing the attribute name to write
	#  @return Numeric value for te selected attribute
	def readAttribute(self,attrName, cache = False):
		value = None
		if attrName is not None and self._devMap:
			try:
				attMap = self._devMap['regs'][attrName.upper()]

				address = attMap['address']
				sdb_address = self.initAddress+(address*4)
				position = attMap['bit_position']
				size = attMap['size']
				access = attMap['access'].split()[0]

				mask = (2**size - 1) << position
				value = self.sdbDrv.readAddress(sdb_address, cache)
				value = (value&mask)>>position
				
				self.logMessage("readAttribute::Attribute %s address: %s value=%s"%(attrName, hex(sdb_address), hex(value)), self.DEBUG)
			except Exception, e:
				self.logMessage("readAttribute::Cannot read %s attribute due to %s"%(attrName, str(e)), self.ERROR)
		else:
			self.logMessage("readAttribute::Cannot read %s attribute"%attrName, self.ERROR)
		return value
	
	## readAttribute(attrName)
	#  This function uses the initial device address obtained from the SDB to read the value using the alinSDB read
	#  functions. It uses the information in the pickle file to apply the proper mask and return the masked value and 
	#  return the value and the rest of detailed regiser information.
	#  @param attrName String containing the attribute name to write
	#  @return Dict that contains the register detailed information, including its value
	def getAttributeInfo(self,attrName):
		valueDict = {}
		if attrName is not None and self._devMap:
			try:
				attMap = self._devMap['regs'][attrName.upper()]

				address = attMap['address']
				position = attMap['bit_position']
				size = attMap['size']
				access = attMap['access'].split()[0]
				desc = attMap['description']
				mask = (2**size - 1) << position
				
				if self.initAddress is not None:
					sdb_address = self.initAddress+(address*4)
					value = self.sdbDrv.readAddress(sdb_address)
					value = (value&mask)>>position
				else:
					sdb_address = None
					value = None
					
				valueDict['name'] = attrName
				valueDict['desc'] = desc 
				valueDict['address'] = sdb_address
				valueDict['regaddress'] = address
				valueDict['position'] = position
				valueDict['size'] = size
				valueDict['access'] = access
				valueDict['value'] = value
				self.logMessage("getAttributeInfo::Attribute info %s dict read"%attrName, self.DEBUG )
			except Exception, e:
				self.logMessage("getAttributeInfo::Cannot read %s attribute due to %s"%(attrName, str(e)), self.ERROR)
		else:
			self.logMessage("getAttributeInfo::Cannot get %s attribute info"%attrName, self.ERROR)
		return valueDict
