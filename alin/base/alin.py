## @package alin.py 
#	File used to read SDB information form spec card
#
#	Author = "Manolo Broseta"
#	Copyright = "Copyright 2015, ALBA"
#	Version = "1.1"
#	Email = "mbroseta@cells.es"
#	Status = "Development"
#	History:
#   30/03/2015 - file created
#	20/10/2015 - Several modifications done
#	             Doxygen detailed info added
__author__ = "Manolo Broseta"
__copyright__ = "Copyright 2015, ALBA"
__license__ = "GPLv3 or later"
__version__ = "1.1"
__email__ = "mbroseta@cells.es"
__status__ = "Development"

from spec_libc import *
from simulated_spec import *

from alinlog import *

import subprocess
import os

from distutils.sysconfig import get_python_lib

__CONFIG_FILE__ = "Config"
__CONFIG_MASK__ = "ALIN_"

## alinSDB class
#
# Main class to read spec memory using te spec_libc library.
# It reads the memory searching for the SDB structure. Provides access to the SDB structured memory
# reading or writing to specific memory positions or devices.
class AlinSDB(AlinLog):
	OFFSET = 0x00 #0x100
	SDB_MAGIC = 0x5344422d

	SDB_RECORD_INTERCONNECT = 0x00
	SDB_RECORD_DEVICE = 0x01
	SDB_RECORD_BRIDGE = 0x02
	SDB_RECORD_INTEGRATION = 0x80
	SDB_RECORD_REPO_URL = 0x81
	SDB_RECORD_SYNTHESIS = 0x82
	SDB_RECORD_EMPTY = 0xff
	
	## The constructor.
	#  @param offset (not mandatory) Start address where the SDB structure is located in memory
	def __init__(self, offset=OFFSET, debug=False):
		AlinLog.__init__(self, debug=False, loggerName='AlinSDB')
		
		self.init_offset = offset
		self.sdb_structure = []
		self._fw_version = None

		self._debug = debug
		self._debuglevel = None
		self._specsimulated = False
		# Get default configuration from config file
		self.getConfigData()
		
		#try:
			#subprocess.call(['modprobe -a','spec.ko'])
		#except:
			#pass
		
		
		if self._specsimulated:
			self.spec = SimulatedSpec()
		else:
			self.spec = Spec()
			
		# Logging
		self.setLogLevel(self._debuglevel)
		self.logEnable(self._debug)
	
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
							self.logMessage("%s::getConfigData(): Can't get DEBUGLEVEL %s"%(__CONFIG_MASK__, self._debug, str(e)),self.ERROR)
					elif cm.startswith("SIMULATED_"):
						try:
							self._specsimulated = True if cm.split("=")[1].lower() == "true" else False
							self.logMessage("%s::getConfigData(): SIMULATED set to %s"%(__CONFIG_MASK__,self._specsimulated),self.INFO)
						except Exception, e:
							self.logMessage("%s::getConfigData(): Can't get SIMULATED flag %s"%(__CONFIG_MASK__, self._debug, str(e)),self.ERROR)
					 
		except Exception, e:
			self.logMessage("%s::getConfigData():: Not possible to get config file due to:"%__CONFIG_MASK__,self.ERROR)
			self.logMessage(str(e),self.ERROR)
			
	def setLogLevel(self, level):
		self._debuglevel = level
		self.logLevel(self._debuglevel)
		
	def getFWVersion(self):
		self.logMessage("getFWVersion:: Version=%s"%self._fw_version, self.DEBUG)
		return self._fw_version

	## getData(address=0).
	#  This function reads the memory searching for the SDB structure. The result is stored in the sdb_structure
	#  @param address (not mandatory) Start address where the SDB structure is located in memory
	def getData(self, address=0):
		self.logMessage("getData:: Address %s"%str(address), self.DEBUG)
		self.base_address = address
		if self.__check():		
			self.device_bridges = [0]
			self.sdb_structure = []
			self.devices_counter = 0
			bus_level = 0
			
			# Get devices in every block of devicesper bridge
			bridge_pos = 0
			while (bridge_pos!=len(self.device_bridges) and bridge_pos<len(self.device_bridges)):
				if bridge_pos!=0:
					add_data = self.sdb_structure[self.device_bridges[bridge_pos]]['sdb_record_type']
					self.base_address = self.getAddress(add_data)
					bus_level +=1
				
				devs = self.__getDevices(self.base_address)
				if devs>0:
					for el in range(devs):
						subaddress = el*64
						dev_address = self.base_address + subaddress
						self.__readBlock(el, bus_level, dev_address)
						self.devices_counter +=1
				bridge_pos+=1
		self.logMessage("getData:: End", self.DEBUG)
		
	## readAddress(address)
	#  This function reads a 4-byte block in a given memory position.
	#  @param address Address to read. It should be multiple of 4
	#  @return Data read
	def readAddress(self,address):
		if address % 4:
			address -= (address % 4)
		rdata = self.spec.specReadL(address, hexformat=False)
		self.logMessage("readAddress:: Address=%s Value=%s"%(hex(address),hex(rdata)), self.DEBUG)
		return rdata
		
	## writeAddress(self,address, data_w=0)
	#  This function writes a 4-byte block in a given memory position.
	#  @param address Address to read. It should be multiple of 4
	#  @param data_w Data to write
	def writeAddress(self,address, data_w=0):
		if address % 4:
			address -= (address % 4)
		self.spec.specWriteL(address, data_w)
		self.logMessage("writeAddress:: Address=%s Value=%s"%(hex(address),hex(data_w)), self.DEBUG)
		self.readAddress(address)
		
	## readData()
	#  This function returns the SDB structure read from memory
	#  @return SDB structure
	def readData(self):
		self.logMessage("readData:: SDB structure read", self.DEBUG)
		return self.sdb_structure

	## loadFile(filename):
	#  This function loads a new bin file un the FPGA. It gets its SDB structure 
	#  @param filename  Bin file to write in the FPGA
	#  @return Boolean value that indicates if the file has been successfully loaded
	def loadFile(self,filename):
		self.filename = filename
		val = self.spec.specLoadBitstream(self.filename)	
		temp = 'cp -f '+self.filename+' /lib/firmware/fmc'
		os.system(temp)
		#os.system('rmmod spec')
		#temp = 'modprobe spec fw_name="/fmc/'+self.filename.split("/")[-1]+'" show_sdb=2'
		#os.system(temp)
		#os.system('dmesg | grep spec')
		#val = True
		if val:
			self.logMessage("loadFile:: File %s loaded succesfully"%filename, self.DEBUG)
			# Reload data after loading the new file
			self.getData(self.init_offset)
		else:
			self.logMessage("loadFile:: Problems loading file %s"%filename, self.ERROR)
		
		return val
		
	## readAddressRange(init_address, end_address)
	#  This function returns a list that contains all memry values between two given address positions
	#  @param init_address Initial address to read from 
	#  @param end_address End address to read to	
	#  @return Data block whcih contains the data in memory for the given address values
	def readAddressRange(self,init_address, end_address):
		if init_address % 4:
			init_address -= (init_address % 4)
		if end_address % 16:
			end_address += (15 - (end_address % 16))
		block = []
		line = []
		for add in range(init_address, end_address+4, 4):
			if add % 16  == 0:
				line.append(add)
			rdata = self.spec.specReadL(add, hexformat=False)
			temp = (rdata&0xff000000)>>24
			line.append(temp)
			temp = (rdata&0x00ff0000)>>16
			line.append(temp)
			temp = (rdata&0x0000ff00)>>8
			line.append(temp)
			temp = (rdata&0x000000ff)
			line.append(temp)
			if add % 16 == 12:
				block.append(line)
				line = []
		self.logMessage("readAddressRange:: Read address range from %s to %s"%(hex(init_address), hex(end_address+4)), self.DEBUG)				
		return block

	## getDeviceMemory(devname="",vend="", prod="")
	#  This function reads the memory for a particualr device name, vendorId and ProductId. The three items have to much, otherwise the function returns None
	#  @param init_address Initial address to read from 
	#  @param end_address End address to read to
	#  @return The data memory block for te specified device
	def getDeviceMemory(self,devname="",vend="", prod=""):
		self.logMessage("getDeviceMemory:: Read device  Memory for device vendor=%s prodcut=%s"%(hex(vend),hex(prod)), self.DEBUG)
		for el in self.sdb_structure:
			if (el['interconnect'] == self.SDB_RECORD_BRIDGE) or\
				(el['interconnect'] == self.SDB_RECORD_INTERCONNECT) or\
				(el['interconnect'] == self.SDB_RECORD_DEVICE):
				name = ''.join([chr(a) for a in el['name']])
				vendor = ''.join(['%02x'%a for a in el['vendor']])
				device = ''.join(['%02x'%a for a in el['device']])		
				if (devname != "" and devname.lower() in name.lower()) or \
					((vend != "" and vend == int(vendor,16)) and \
					(prod != "" and prod == int(device,16))):
					data = {}
					init_add = self.getAddress(el['first_address'])+el['base_address']
					end_add =  self.getAddress(el['last_address'])+el['base_address']
					
					if init_add % 4:
						init_add -= (init_add % 4)
					if end_add % 4:
						end_add -= (end_add % 4)
					block = []
					for add in range(init_add, end_add+4, 4):
						rdata = self.spec.specReadL(add, hexformat=False)
						block.append(rdata)			
					data['init_add'] = init_add
					data['end_add'] = end_add
					data['data'] = block
					return data
		self.logMessage("getDeviceMemory:: Nothing to show", self.DEBUG)
		return None

	## getAddress(*args)
	#  This function converts a block of four 4 bytes to an address value
	#  @param args Block of bytes that contain the address
	#  @return Calculated address
	def getAddress(self,*args):
		data = args[0]
		address = 0
		for el in data:
			address = (address<<8) + el
		return address

	## __check() 
	#  Private function that checks if the SDB magic number extis in the base address
	#  @return Boolean value that indicates if the SDB MAgic number is found
	def __check(self):
		# Read SDB Magic #
		rdata = self.spec.specReadL(self.base_address, hexformat=False)
		if (rdata==self.SDB_MAGIC):
			self.logMessage("__check:: SDB Magic number found at %s address"%hex(self.base_address), self.DEBUG)
			return True
		else:
			self.logMessage("__check:: SDB Magic not found!!", self.ERROR)
		return False
	


	## __getDevices(address)
	#  Private function that retruns the number of devices found in the SDB for a given address
	#  @param address location where the SDB record is located
	#  @return Number of devices for that SDB record
	def __getDevices(self, address):
		# Get number of devices #
		rdata = self.spec.specReadL(address+4, hexformat=False)
		devices = int((rdata&0xffff0000)>>16)
		self.logMessage("__getDevices:: %s decives found in address %s"%(str(devices),hex(address)), self.DEBUG)
		return devices

	## __readBlock(dev=0, bus=0, address=0)
	#  Private function that reads the SDB structure for a given device, bus and address
	#  @param dev Number of the device in the bus
	#  @param bus Layer of the SDB record
	#  @param address Location to read the record
	def __readBlock(self, dev=0, bus=0, address=0):
		data_block = []
		for i in range (0,16):
			data = self.spec.specReadL(address+(i*4),hexformat=False)
			temp = (data&0xff000000)>>24
			data_block.append(temp)
			temp = (data&0x00ff0000)>>16
			data_block.append(temp)
			temp = (data&0x0000ff00)>>8
			data_block.append(temp)
			temp = (data&0x000000ff)
			data_block.append(temp)

		sdb_component = {}
		sdb_component['dev_num'] = self.devices_counter
		sdb_component['bus'] = bus
		sdb_component['devnum_in_bus'] = dev
		sdb_component['base_address'] = self.base_address
		sdb_component['dev_address'] = address
		sdb_component['interconnect'] = data_block[63]
		
		if sdb_component['interconnect'] == self.SDB_RECORD_REPO_URL:
			# REPOSITORY-URL RECORD TYPE0xfa0L

			sdb_component['repo_url'] = [(data_block[i]) for i in range(0,63)]
		elif sdb_component['interconnect'] == self.SDB_RECORD_SYNTHESIS:
			# SYNTHESIS RECORD TYPE
			sdb_component['name'] = [(data_block[i]) for i in range(0,16)]
			sdb_component['commit_id'] = [(data_block[i]) for i in range(16,32)]
			sdb_component['tool_name'] = [(data_block[i]) for i in range(32,40)]
			sdb_component['tool_ver'] = [(data_block[i]) for i in range(40,44)]
			sdb_component['date'] = [(data_block[i]) for i in range(44,48)]
			sdb_component['usr_name'] = [(data_block[i]) for i in range (48,63)]			
		else:
			# REST OF RECORD DEVICES HAVE SIMILAR SDB STRUCTURE
			sdb_component['sdb_record_type'] = [(data_block[i]) for i in range(0,8)]
			if sdb_component['interconnect'] != self.SDB_RECORD_INTEGRATION:
				sdb_component['first_address'] = [(data_block[i]) for i in range(8,16)]
				sdb_component['last_address'] = [(data_block[i]) for i in range(16,24)]
			sdb_component['vendor'] = [(data_block[i]) for i in range(24,32)]
			sdb_component['device'] = [(data_block[i]) for i in range(32,36)]
			sdb_component['version'] = [(data_block[i]) for i in range(36,40)]
			sdb_component['date'] = [(data_block[i]) for i in range(40,44)]
			sdb_component['name'] = [(data_block[i]) for i in range (44,63)]
			
			if sdb_component['interconnect'] == self.SDB_RECORD_INTEGRATION:
				self._fw_version = "".join([str(a) for a in sdb_component['version'][:2]])+"."+"".join([str(a) for a in sdb_component['version'][2:]])

			if sdb_component['interconnect'] == self.SDB_RECORD_BRIDGE:
				self.device_bridges.append(self.devices_counter)
		
		self.sdb_structure.append(sdb_component)
		self.logMessage("__readBlock:: %s record type found at bus level %s address %s"%(hex(sdb_component['interconnect']), str(bus), hex(address)), self.DEBUG)
		
