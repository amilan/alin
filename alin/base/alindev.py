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

import os.path, pickle

from distutils.sysconfig import get_python_lib

from alin import *
from alinlog import AlinLog

__OFFSET__ = 0x00 #0x100

__CONFIG_FILE__ = "Config"
__CONFIG_MASK__ = "ALINDEV_"

## alinDevice class
#
# Main class that links the device map pickel file created with the coresponding memory area defined in the SDB
# It provides functions to get device information and to read/write attributes of that device
class AlinDevice(AlinLog):
	## The constructor.
	#  @param device (not mandatory) Device to controls
	def __init__(self, device=None, number=0, debug=False):
		AlinLog.__init__(self, debug=False, loggerName='AlinDevice')
		
		self._debug = debug
		self._debuglevel = None
		# Get default configuration from config file
		self.getConfigData()
		
		self._devMap = {}
		self.sdbDrv = AlinSDB(__OFFSET__, debug=self._debuglevel)
		self.sdbDrv.getData(__OFFSET__)
		
		#self.__device_folder = os.path.abspath(os.path.dirname(__file__))+"/deviceslib/"
		self.__device_folder = get_python_lib()+"/alin/deviceslib/"
		
		# Logging
		self.setLogLevel(self._debuglevel)
		self.logEnable(self._debug)
		
		if device is not None:
			self.setDevice(device, number)
		
	def getConfigData(self):
		# Get config File
		config_folder = get_python_lib()+"/alin/config/"
		config_file = config_folder+__CONFIG_FILE__
		
		try:
			with open(config_file, 'r') as f:
				lines = f.readlines()
				f.close()
				
			comp = [ln.split(__CONFIG_MASK__)[1].replace(" ","").replace("\t","").replace("\n","") for ln in lines if ln.startswith(__CONFIG_MASK__)]
			if comp != []:
				for cm in comp:
					if cm.startswith("DEBUG_"):
						try:
							self._debug = True if cm.split("=")[1].lower() == "true" else False
							self.logMessage("%s::getConfigData(): DEBUG set to %s"%(__CONFIG_MASK__, self._debug),self.INFO)
						except Exception, e:
							self.logMessage("%s::getConfigData(): Can't get DEBUG flag %s"%(__CONFIG_MASK__, self._debug, str(e)),self.ERROR)
					elif cm.startswith("DEBUGLEVEL_"):
						try:
							self._debuglevel = int(cm.split("=")[1])
							self.logMessage("%s::getConfigData(): DEBUGLEVEL set to %d"%(__CONFIG_MASK__,self._debuglevel),self.INFO)
						except Exception, e:
							self.logMessage("%s::getConfigData(): Can't get DEBUGLEVEL  %s"%(__CONFIG_MASK__, self._debug, str(e)),self.ERROR)
					 
		except Exception, e:
			self.logMessage("%s::getConfigData():: Not possible to get config file due to:"%__CONFIG_MASK__,self.ERROR)
			self.logMessage(str(e),self.ERROR)
			
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
		valueList = []
		rd_data = {}
		rd_data = self.sdbDrv.getDeviceMemory(vend=self.vendorId, prod=self.product)
		if rd_data and self._devMap:
			for el in self._devMap['regs']:
				regname = el.keys()[0]
				address = el[el.keys()[0]]['address']
				position = el[el.keys()[0]]['bit_position']
				size = el[el.keys()[0]]['size']
				
				mask = (2**size - 1) << position
				
				value = rd_data['data'][address]
				value = (value&mask)>>position
				
				valueList.append((regname.upper(),hex(value)))
			self.logMessage("getDeviceData::Read all device data list", self.DEBUG)
		else:
			if self._devMap:
				for el in self._devMap['regs']:
					regname = el.keys()[0]
					value = None
					valueList.append((regname.upper(),value))
			self.logMessage("getDeviceData:Not possible to get the data from Memory!!", self.ERROR)
		
		return valueList

	## getAttributesList()
	#  This function returns the list of attributes defined in the pickle file
	#  @return List containing the list of attributes defined in the pickle file
	def getAttributesList(self):
		valueList = []
		if self._devMap:
			valueList = [el.keys()[0] for el in self._devMap['regs']]
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
			for el in self._devMap['regs']:
				if attrName.lower() == el.keys()[0].lower():
					address = el[el.keys()[0]]['address']
					sdb_address = self.initAddress+(address*4)
					position = el[el.keys()[0]]['bit_position']
					size = el[el.keys()[0]]['size']
					access = el[el.keys()[0]]['access'].split()[0]

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
		else:
			self.logMessage("writeAttribute::Cannot write %s attribute"%attrName, self.ERROR)

	## readAttribute(attrName)
	#  This function uses the initial device address obtained from the SDB to read the value using the alinSDB read
	#  functions. Then it uses the information in the pickle file to apply the proper mask and return the masked value
	#  @param attrName String containing the attribute name to write
	#  @return Numeric value for te selected attribute
	def readAttribute(self,attrName):
		value = None
		if attrName is not None and self._devMap:
			for el in self._devMap['regs']:
				if attrName.lower() == el.keys()[0].lower():
					address = el[el.keys()[0]]['address']
					sdb_address = self.initAddress+(address*4)
					position = el[el.keys()[0]]['bit_position']
					size = el[el.keys()[0]]['size']
					access = el[el.keys()[0]]['access'].split()[0]

					mask = (2**size - 1) << position
					value = self.sdbDrv.readAddress(sdb_address)
					value = (value&mask)>>position
					
					self.logMessage("readAttribute::Attribute %s address: %s value=%s"%(attrName, hex(sdb_address), hex(value)), self.DEBUG)
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
			for el in self._devMap['regs']:
				if attrName.lower() == el.keys()[0].lower():
					address = el[el.keys()[0]]['address']
					position = el[el.keys()[0]]['bit_position']
					size = el[el.keys()[0]]['size']
					access = el[el.keys()[0]]['access'].split()[0]
					desc = el[el.keys()[0]]['description']
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
		else:
			self.logMessage("getAttributeInfo::Cannot get %s attribute info"%attrName, self.ERROR)
		return valueDict
