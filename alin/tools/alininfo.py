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

from alin.base import *

import getopt
import json
import os
import pickle
import select
import sys
import threading
import time

OFFSET = 0x00 #0x100
#DEVICE_FOLDER = "/home/projects/alba-em/deviceslib/"


class FPGADataSaving(threading.Thread):
	def __init__(self, period= 1, count=0):
		threading.Thread.__init__(self)
		
		self.period = period
		self.count = count
		
		self._endProcess = False
		self._processEnded = False
		
				
	def end(self):
		self._endProcess = True
				
	def getProcessEnded(self):
		return self._processEnded
	
	def saveFPGAData(self):
		dev_list = [('WB-HRMY-CROSSBAR', 0), 
					('WB-HRMY-CROSSBAR', 1), 
					('WB-HRMY-CROSSBAR', 2), 
					('WB-FMC-FV-CONTROL', 0),
					('WB-HRMY-AVERAGE', 0), 
					('WB-HRMY-AVERAGE', 1), 
					('WB-HRMY-AVERAGE', 2), 
					('WB-HRMY-AVERAGE', 3), 
					('WB-HRMY-FIFO', 0), 
					('WB-HRMY-FIFO', 1), 
					('WB-HRMY-FIFO', 2), 
					('WB-HRMY-FIFO', 3),
					('WB-FMC-ADC-CORE', 0), 
					('WB-HRMY-MEMORY', 0), 
					('WB-HRMY-ID-GEN', 0), 
					('SPI', 0), 
					('WB-EM2-DIGITAL_IO', 0),
					]

		out_dict = {}
		dev_dict = []
		for dev in dev_list:
			d = AlinDevice(device=dev[0], number=dev[1], debug=False)
			if dev[0] == 'WB-HRMY-MEMORY':
				att_list = d.getAttributesList()
				temp = {}
				for att in att_list:
					if att != "V_DATA":
						val = d.readAttribute(att)
						temp[att] = val
			else:
				temp = d.getDeviceData()
			dev_dict.append([dev[0]+" "+str(dev[1]), temp])
			
		out_dict['Last update'] = {'DATE': time.strftime("%d/%m/%Y"), 'TIME': time.strftime("%H:%M:%S")}
		out_dict['Data'] = dev_dict

		jsondata = json.dumps(out_dict, indent=4, skipkeys=True, sort_keys=True)
		with open("/var/www/static/fpga_data.json","w") as out_file:
			out_file.write(jsondata)
		out_file.close()


	def run(self): 
		data_dict = {}
		count = 0
		i = []
		print "\nPress <ENTER> to abort or stop file generation!!\n"
		while i==[] and not self._endProcess:
			try:
				print "Generating File count: %s out of %s"%(str(count),str(self.count))
				self.saveFPGAData()
				count += 1
				if (self.count == 0) or (self.count != 0 and count<self.count):
					i, o, e = select.select( [sys.stdin], [], [], self.period )
				else:
					self._endProcess = True
			except KeyboardInterrupt:
				self._endProcess = True
				break
				
		self._processEnded = True

class AlinInfo():
	def __init__(self, offset=0):
		
		self.app = AlinSDB(debug=False)
		self.app.getData(offset)
		self.jsonThread = None
		
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
			device = AlinDevice(dev, devnum, debug=False)
			device.writeAttribute(reg,data)
			
			value = device.readAttribute(reg)
			txt = "%s "%reg.upper()
			txt = txt.ljust(30,'.')
			txt += ": %s"%hex(value)
			print "\n"+txt+"\n"
			
	def readDeviceReg(self, dev=None, devnum=0, reg=None):
		if dev is not None and reg is not None:
			device = AlinDevice(dev, devnum, debug=False)
			value = device.readAttribute(reg)
			txt = "%s "%reg.upper()
			txt = txt.ljust(30,'.')
			txt += ": %s"%hex(value)
			print "\n"+txt+"\n"
			
	def infoDeviceReg(self, dev=None, devnum=0, reg=None):
		if dev is not None and reg is not None:
			temp = {}
			device = AlinDevice(dev, devnum, debug=False)
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
			device = AlinDevice(debug=False)
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
				
				for idx,el in sorted(temp.items()):
					txt = "%s "%idx
					txt = txt.ljust(30,'.')
					txt += ": %s"%hex(el)
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
			
			
	def generateFPGADataFile(self, period, time):
		self.jsonThread = FPGADataSaving(period=period, count=time)
		self.jsonThread.start()
		
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
	print BOLD+"\t-f <period>,<times>"+END
	print "\t\tGenerates the FPGA json file to used in the fpga-html page\n"
	print "\t\tI.e.: alin -f 20  --> This will generate files continuosly every 20 seconds\n"
	print "\t\tI.e.: alin -b 20, 5 --> this will generate just 5 files every 20 secons\n"
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
		short_cmds = "o:l:r:w:g:s:b:f:itmd:v:"
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

	# 8- generate the FPGA file to used in the FPGA.html web page
	if "-f" in opts_dict.keys():
		try:
			period = int(opts_dict["-f"].split(",")[0])
			times = int(opts_dict["-f"].split(",")[1])
		except:
			try:
				period = int(opts_dict["-f"].split(",")[0])
			except:
				period = 1
			times = 0
		al.generateFPGADataFile(period,times)
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
