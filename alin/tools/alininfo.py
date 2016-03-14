#----------------------------------------------------------------------------------------------------------------------
#   
#	ctemsdb.py file
#
#	File used to read SDB information form spec card
#	History:
#   30/03/2015 - file created
#
#----------------------------------------------------------------------------------------------------------------------
__author__ = "Manolo Broseta"
__copyright__ = "Copyright 2015, ALBA"
__license__ = "GPLv3 or later"
__version__ = "1.0"
__email__ = "mbroseta@cells.es"
__status__ = "Development"

import os
import pickle
import getopt, sys
import select

from alin.base import *

OFFSET = 0x00 #0x100
#DEVICE_FOLDER = "/home/projects/alba-em/deviceslib/"


class AlinInfo():
	def __init__(self, offset=0):
		
		self.app = AlinSDB()
		self.app.getData(offset)
		
	def showDevice(devfile=""):
		dev_map = {}
		output = open(devfile, 'rb')
		dev_map = pickle.load(output)
		return dev_map

	def showInfo(self):
		sdb_data = self.app.readData()
		for el in sdb_data:
			print "BaseAdress: \t\t%s"%hex(el['base_address'])
			print "BusPath level:  \t%s.%s"%(el['bus'],el['devnum_in_bus'])

			if el['interconnect'] == self.app.SDB_RECORD_INTEGRATION: #Informative integration structure#
				print "Record type\t\tIntegration Record"
			elif el['interconnect'] == self.app.SDB_RECORD_REPO_URL: #Empty record
				print "Record type\t\tRepository-Url"
				print "Url\t\t\t0x00: %s"%''.join([chr(a) for a in el['repo_url']])
				print "Record Type\t\t0x3f: %s\n"%hex(el['interconnect'])
				continue
			elif el['interconnect'] == self.app.SDB_RECORD_SYNTHESIS: #Empty record
				print "Record type\t\tSynthesis Record"
				print "Project \t\t0x00: %s"%''.join([chr(a) for a in el['name']])
				print "Commit_id\t\t0x10: %s"%' '.join(['%02x'%a for a in el['commit_id']])
				print "Tool name\t\t0x00: %s"%''.join([chr(a) for a in el['tool_name']])
				print "Tool ver\t\t0x00: %s"%' '.join(['%02x'%a for a in el['tool_ver']])
				print "Date\t\t\t0x28: %s"%' '.join(['%02x'%a for a in el['date']])
				print "User name\t\t0x00: %s"%''.join([chr(a) for a in el['usr_name']])
				print "Record Type\t\t0x3f: %s\n"%hex(el['interconnect'])
				continue
			elif el['interconnect'] == self.app.SDB_RECORD_INTERCONNECT: #SDB Interconnect#/
				print "Record type\t\tSDB Interconnect"
				print "Magic 'SDB-'\t\t0x00: %s"%' '.join(['%02x'%(el['sdb_record_type'][i]) for i in range(0,4)])
				print "Number of Records\t0x04: %s"%' '.join(['%02x'%(el['sdb_record_type'][i]) for i in range(4,6)])
				print "SDB Version\t\t0x06: %02x"%el['sdb_record_type'][6]
				print "Bus type\t\t0x07: %02x"%el['sdb_record_type'][7]
				print "First address\t\t0x08: %s"%' '.join(['%02x'%a for a in el['first_address']])
				print "Last address\t\t0x10: %s"%' '.join(['%02x'%a for a in el['last_address']])
			elif el['interconnect'] == self.app.SDB_RECORD_DEVICE: #Device definition#/
				print "Record type\t\tDevice Record"
				print "ABI class\t\t0x00: %s"%' '.join(['%02x'%(el['sdb_record_type'][i]) for i in range(0,2)])
				print "ABI version major\t0x04: %02x"%el['sdb_record_type'][2]
				print "ABI version minor\t0x06: %02x"%el['sdb_record_type'][3]
				print "Bus-specific field\t0x07: %s"%' '.join(['%02x'%(el['sdb_record_type'][i]) for i in range(4,8)])
				print "First address\t\t0x08: %s"%' '.join(['%02x'%a for a in el['first_address']])
				print "Last address\t\t0x10: %s"%' '.join(['%02x'%a for a in el['last_address']])

			elif el['interconnect'] == self.app.SDB_RECORD_BRIDGE: #Bridge to sub-bus definition#/
 				print "Record type\t\tBridge Record"
				print "SDB Child\t\t0x00: %s"%' '.join(['%02x'%(el['sdb_record_type'][i]) for i in range(0,8)])
				print "First address\t\t0x08: %s"%' '.join(['%02x'%a for a in el['first_address']])
				print "Last address\t\t0x10: %s"%' '.join(['%02x'%a for a in el['last_address']])
			elif el['interconnect'] == self.app.SDB_RECORD_EMPTY: #Empty record
				# reserved #
				continue

			print "Vendor  \t\t0x18: %s"%' '.join(['%02x'%a for a in el['vendor']])
			print "Device  \t\t0x20: %s"%' '.join(['%02x'%a for a in el['device']])
			print "Version \t\t0x24: %s"%' '.join(['%02x'%a for a in el['version']])
			print "Date\t\t\t0x28: %s"%' '.join(['%02x'%a for a in el['date']])
			print "Name\t\t\t0x2c: %s"%''.join([chr(a) for a in el['name']])
			print "Record Type\t\t0x3f: %s\n"%hex(el['interconnect'])			
			
	def showTree(self):
		print "#\tBusPath\tVendorId\tProduct\t\tAddress range(hex)\tDescription"

		sdb_data = self.app.readData()
		for el in sdb_data:
			add_val = "..........."
			if el['interconnect']==self.app.SDB_RECORD_REPO_URL:
				vendor_device = "..<< Repository-url >>.."
				name = ''.join([chr(a) for a in el['repo_url']])
			elif el['interconnect']== self.app.SDB_RECORD_SYNTHESIS:				
				vendor_device = "....<< Synthesis >>....."
				name = ''.join([chr(a) for a in el['name']])
			elif el['interconnect']== self.app.SDB_RECORD_INTEGRATION:
				vendor = ''.join(['%02x'%a for a in el['vendor']])
				device = ''.join(['%02x'%a for a in el['device']])
				vendor_device = vendor+":"+device
				name = ''.join([chr(a) for a in el['name']])
			else:
				first_address = self.app.getAddress(el['first_address'])
				last_address = self.app.getAddress(el['last_address'])
				add_val = hex(first_address+el['base_address'])+"-"+hex(last_address+el['base_address'])
				vendor = ''.join(['%02x'%a for a in el['vendor']])
				device = ''.join(['%02x'%a for a in el['device']])
				vendor_device = vendor+":"+device
				name = ''.join([chr(a) for a in el['name']])
			print "%s\t%s.%s\t%s\t%s\t\t%s"%(str(el['dev_num']),str(el['bus']),str(el['devnum_in_bus']),vendor_device,add_val,name)


	def loadFile(self,filename=None):
		if filename is not None and os.path.isfile(filename):
			ret = self.app.loadFile(filename)
			if ret:
				print('\nThe bitstream has been successfully loaded\n')
			else:
				print('\nThe bitstream loading has FAILED or cannot find the bitstream!!!\n')
				
	def readAddress(self,address=0):
		print "\nPress 'Enter' to stop reading the address:\n"
		i = []
		while i==[]:
			value = self.app.readAddress(address)
			sys.stdout.write("\rSDB Read data: Address=%s Value=%s"%(hex(address),format(value,'#010x')))
			sys.stdout.flush()
			i, o, e = select.select( [sys.stdin], [], [], 1 )

	def writeAddress(self,address=0, data=0):
		if address != OFFSET:
			self.app.writeAddress(address,data)
			
	def readMemoryBlock(self, init_address=0, end_address=0):
		if init_address == end_address or init_address > end_address:
			end_address = init_address+4
				
		rd_blk = []
		rd_blk = self.app.readAddressRange(init_address,end_address)
		for el in rd_blk:
			print "%06x"%el[0],
			print ' '.join([("%02x"%el[a]) for a in range(1,17)]),
			print " >",''.join([chr(el[a]) if el[a]>0x1F and el[a]<0x80 else c86hr(0x2E) for a in range(1,17)]),"<"
			
	def showDeviceMemory(self):
		print "Select device from the list:\n"
		self.showTree()
		devnum = raw_input("\nSelect device number to show (any other key to exit):")

		block = []
		sdb_data = self.app.readData()
		if  len(sdb_data)>int(devnum):
			el = sdb_data[int(devnum)]
			if (el['interconnect'] == self.app.SDB_RECORD_BRIDGE) or\
				(el['interconnect'] == self.app.SDB_RECORD_INTERCONNECT) or\
				(el['interconnect'] == self.app.SDB_RECORD_DEVICE):
					init_add = self.app.getAddress(el['first_address'])+el['base_address']
					end_add =  self.app.getAddress(el['last_address'])+el['base_address']
					print "\nVendor: %s"%''.join(['%02x'%a for a in el['vendor']])
					print "Device: %s"%''.join(['%02x'%a for a in el['device']])
					print "Name: %s"%''.join([chr(a) for a in el['name']])
					print "First address=%s"%hex(init_add)
					print "Last address=%s\n"%hex(end_add)
					block = self.app.readAddressRange(init_add,end_add)
			else:
				print "** Not possible to show device map for this device **"
		else:
			print "** Incorrect device num **"
		
		if block != [] :
			for el in block:
				print "%06x"%el[0],
				print ' '.join([("%02x"%el[a]) for a in range(1,17)]),
				print " >",''.join([chr(el[a]) if el[a]>0x1F and el[a]<0x80 else chr(0x2E) for a in range(1,17)]),"<"
			
			
	def writeDeviceReg(self, dev=None, devnum=0, reg=None, data=0):
		if dev is not None and reg is not None:
			device = AlinDevice(dev, devnum)
			device.writeAttribute(reg,data)
			
			value = device.readAttribute(reg)
			txt = "%s "%reg.upper()
			txt = txt.ljust(30,'.')
			txt += ": %s"%hex(value)
			print "\n"+txt+"\n"
			
	def readDeviceReg(self, dev=None, devnum=0, reg=None):
		if dev is not None and reg is not None:
			device = AlinDevice(dev, devnum)
			value = device.readAttribute(reg)
			txt = "%s "%reg.upper()
			txt = txt.ljust(30,'.')
			txt += ": %s"%hex(value)
			print "\n"+txt+"\n"
			
	def infoDeviceReg(self, dev=None, devnum=0, reg=None):
		if dev is not None and reg is not None:
			temp = {}
			device = AlinDevice(dev, devnum)
			temp = device.getAttributeInfo(reg)
			try:
				print "\nDescriptrion:"
				dp = temp['desc'].split("\\n")
				for el in dp:
					print "\t",el
			except:
				print "\n%s\n"%temp['desc']
			try:
				print "\nAddress: \t%s"%hex(temp['address'])
			except:
				print "\nAddress: \tNot found"
				
			print "RegAddress: \t%s"%hex(temp['regaddress'])				
			print "Bit position: \t%s"%str(temp['position'])
			print "Size: \t\t%s"%str(temp['size'])
			print "Type: \t\t%s"%temp['access']
			txt = "%s "%reg.upper()
			txt = txt.ljust(30,'.')
			try:
				txt += ": %s"%hex(temp['value'])
			except:
				txt += ": None"
			print "\n"+txt+"\n"

	def infoDevice(self, dev=None, devnum=0):
		if dev is not None:
			device = AlinDevice()
			devinfo = device.setDevice(dev, devnum)
			if devinfo is not None:
				temp = []
				temp = device.getDeviceData()
				
				print "\nDevice:\t\t%s"%dev.upper()
				print "VendorId:\t%#0.016x"%long(devinfo['vendorid'],16)
				print "Product:\t%#0.08x"%long(devinfo['product'],16)
				print "First Address:\t%s"%hex(devinfo['first_address'])
				print "Last Address:\t%s"%hex(devinfo['last_address'])
				print "Description:\t%s\n"%devinfo['description']
				
				for el in temp:
					txt = "%s "%el[0]
					txt = txt.ljust(30,'.')
					txt += ": %s"%el[1]
					print txt
				print "\n"
			else:
				print "\nInvalid device name\n"
					
	def infoDeviceList(self):
		devfolder = os.environ.get('ALINPATH', 'Not Set')
		if devfolder != 'Not Set':
			devfolder = devfolder +"/deviceslib"			

			onlyfiles = [ f for f in os.listdir(devfolder) if os.path.isfile(os.path.join(devfolder,f)) ]
			
			if onlyfiles != []:
				print "List of devices:\n"
				for f in onlyfiles:
					print "- ",f.upper()
				print "\n"
			else:
				print "\nNo devices found on devicelib folder!!\n"			
		else:
			print "ALINPATH not set\n"
			
		
def help():
	BOLD = '\033[1m'
	END = '\033[0m'
	
	print "ALIN usage as follows:\n"
	print BOLD+"\t# alin <command_1>=<value> <command_2>=<value>....."+END
	print "\nCommands are optional. By default, short SDB structure info is shown (alin -t)."
	print "List of available commands are:\n"
	print BOLD+"\t-r <address> or ---read=<address>:"+END
	print "\t\tContinuous read of a memory address. This read will be updated every second until 'enter' key will be pressed."
	print "\t\tI.e.: alin -r 0x3100\n"
	print BOLD+"\t-m or --map:"+END
	print "\t\tShows the available devices list and lets the user to select which device memory map to show.\n"
	print BOLD+"\t-i or --info:"+END
	print "\t\tTo display the detailed SDB structure.\n"
	print BOLD+"\t-t or --tree:"+END
	print "\t\tShort list of SDB structure.\n"	
	print BOLD+"\t--help:"+END
	print "\t\tShows this help\n"
	print BOLD+"\t-l <filename.bin> or --load=<filename.bin>:"+END
	print "\t\tTo load a new binary file into the Spec FPGA."
	print "\t\tThe file location has to be specified, i.e.: alin load='/lib/firmware/fmc/spec-init.bin'.\n"
	print BOLD+"\t-o <value> or --offset=<value>:"+END
	print "\t\tTo define the address position where the SDB magic number is located. By defult offset values is 0x100.\n"
	print BOLD+"\t-b <init_addr>,<end_add> or --block=<init_add>,<end_add>:"+END
	print "\t\tThis shows range of data memory from the init address <init_add> to the end address defined in <end_add>."
	print "\t\tI.e.: alin -b 0x100,0x11f\n"
	print BOLD+"\t-w <address>,<value> or --write=<address>,<value>:"+END
	print "\t\tThis commands lets write a value in a certain position."
	print "\t\tI.e.: alin -w 0x3100,0x01\n"
	print BOLD+"\t-d <devname>,<device_number> command <values1>,<value2> or --dev=<devname>,<device_number> command1 <values1>,<value2>:"+END
	print "\t\tThis command is use to get information abput a particular device and provide individual control for each of its registers"
	print "\t\tIf not <devname> is specified, it shows the complete list of available devices"
	print "\t\tIf there are severel devices of the same type, <device_number> specifies the the number of the device to access. Default value is 0"
	print "\t\tThe list of command available for a device are:"
	print BOLD+"\t\t\t-[None]:"+END+"\t\tWithout commands, it shows general information about the device and its registers"
	print BOLD+"\t\t\t-g <regname>:"+END+" \t\tGets the value of regsiter. I.e.: alin --dev='<VendorID:Product>' -g <REG_NAME>"
	print BOLD+"\t\t\t-v <regname>:"+END+" \t\tViews the complete register info. I.e.: alin -d '<VendorID:Product>' -v <REG_NAME>"
	print BOLD+"\t\t\t-s <regname>,<value>:"+END+" \tSetss a <value> to the regsiter <regname>. I.e.: alin dev='<VendorID:Product>' -s <REG_NAME> data=0x<hex_value>"
	print "\n"
	
def main():
	try:
		short_cmds = "o:l:r:w:g:s:b:itmd:v:"
		long_cmds = ["help","offset=","load=","read=","write=","block=","info","tree","map","dev=","list"]
		opts, args = getopt.getopt(sys.argv[1:], short_cmds, long_cmds)
	except getopt.GetoptError as err:
		print (err) # will print something like "option -a not recognized"
		print "\nFor detailed command help use: alin --help\n" 
		sys.exit(2)

	opts_dict = dict(opts)
	
	# 0- show help
	if "--help" in opts_dict.keys():
		help()
		sys.exit()
	
	# 1- Offset commnad
	if "-o" in opts_dict.keys():
		offset = int(opts_dict["-o"],16)
	elif "--offset=" in opts_dict.keys():
		offset = int(opts_dict["--offset="],16)
	else:
		offset = OFFSET
		
	al = AlinInfo(offset)

	# 2- Load new file command
	filename = None
	if "-l" in opts_dict.keys():
		filename = opts_dict["-l"]
	elif "--load=" in opts_dict.keys():
		filename = opts_dict["--load="]
	if filename is not None:
		al.loadFile(filename)
		
	# 3- Continuous read of an address
	address = None
	if "-r" in opts_dict.keys():
		address=int(opts_dict["-r"],16)
	elif "--read=" in opts_dict.keys():	
		address=int(opts_dict["--read="],16)
	if address is not None:
		al.readAddress(address)
		sys.exit()

	# 4- Continuous read of an address
	address = None
	data = None
	if "-w" in opts_dict.keys():
		try:
			address = int(opts_dict["-w"].split(",")[0],16)
			data = int(opts_dict["-w"].split(",")[1],16)
		except:
			print "Invalid address/data"
			sys.exit()
	elif "--write=" in opts_dict.keys():	
		try:
			address = int(opts_dict["--write="].split(",")[0],16)
			data = int(opts_dict["--write="].split(",")[1],16)
		except:
			print "Invalid address/data"
			sys.exit()
	if address is not None and data is not None:
		al.writeAddress(address,data)
		sys.exit()
		
	# 5- Reads a block of memory
	init_address = None
	end_address = None
	if "-b" in opts_dict.keys():
		try:
			init_address = int(opts_dict["-b"].split(",")[0],16)
			end_address = int(opts_dict["-b"].split(",")[1],16)
		except:
			print "Invalid init_address/end_address"
			sys.exit()
	elif "--block=" in opts_dict.keys():	
		try:
			init_address = int(opts_dict["--block="].split(",")[0],16)
			end_address = int(opts_dict["--block="].split(",")[1],16)
		except:
			print "Invalid init_address/end_address"
			sys.exit()
	if init_address is not None and end_address is not None:
		al.readMemoryBlock(init_address,end_address)
		sys.exit()

	# 6- Reads/Writes a device
	dev = None
	if "-d" in opts_dict.keys():
		try:
			dev = opts_dict["-d"].split(",")[0]
			dev_num = int(opts_dict["-d"].split(",")[1])
		except:
			dev = opts_dict["-d"]
			dev_num = 0
	elif "--dev=" in opts_dict.keys():
		try:
			dev = opts_dict["--dev="].split(",")[0]
			dev_num = int(opts_dict["--dev="].split(",")[1])
		except:
			dev = opts_dict["-d"]
			dev_num = 0
	if dev == 'list':
		al.infoDeviceList()
		sys.exit()
	elif dev is not None:
		reg_name = None
		data = None
		if "-s" in opts_dict.keys():
			try:
				reg_name = opts_dict["-s"].split(",")[0]
				data = int(opts_dict["-s"].split(",")[1],16)
			except:
				print "Invalid address/data"
				sys.exit()
			if reg_name is not None and data is not None:
				al.writeDeviceReg(dev, dev_num, reg_name,data)
				sys.exit()
		elif "-g" in opts_dict.keys():
			try:
				reg_name = opts_dict["-g"]
			except:
				print "Invalid address/data"
				sys.exit()
			if reg_name is not None:
				al.readDeviceReg(dev, dev_num, reg_name)
				sys.exit()
		elif "-v" in opts_dict.keys():
			try:
				reg_name = opts_dict["-v"]
			except:
				print "Invalid address/data"
				sys.exit()
			if reg_name is not None:
				al.infoDeviceReg(dev, dev_num, reg_name)
				sys.exit()
		else:
			al.infoDevice(dev, dev_num)
		sys.exit()
		
	# 7- shows the memory map of a device
	if "-m" in opts_dict.keys() or "--map" in opts_dict.keys():
		al.showDeviceMemory()
		sys.exit()
		
	# X- Reads a block of memory
	if "-i" in opts_dict.keys() or "--info" in opts_dict.keys():
		al.showInfo()
	elif "-t" in opts_dict.keys() or "--tree" in opts_dict.keys():
		al.showTree()
	else:
		al.showTree()
		
	sys.exit()

	
if __name__ == "__main__":
    main()	
