#!/usr/bin/python

import os, re, sys
import pickle
from alin.base import *
from distutils.sysconfig import get_python_lib

#DEFAULT_PATH = "/home/projects/alba-em/deviceslib/"

class Generator():
	def __init__(self):
		self.wboutput = {}
		
		#self.default_path = os.path.dirname(alin.__file__)+"/deviceslib/"
		self.default_path = get_python_lib()+"/alin/deviceslib/"
		if not os.path.exists(self.default_path):
			os.makedirs(self.default_path)
			
	def getInstallationPath(self):
		return self.default_path

	def processWBData(self,filename=''):
		
		self.fread = []
		self.wb_filename = filename
		try:
			with open(self.wb_filename) as f:
				self.fread = [" ".join(l.split()) for l in f]
		except Exception, e:
			print "Error while opening in wb file: %s"%str(e)
			return
		
		self.wboutput = {}
		self.wboutput["product"] = self.getInputProduct()
		self.wboutput["vendorid"] = self.getInputVendorID()
		devName = self.getInputName()
		self.wboutput["devname"] = devName
		
		if devName is not None:
			offset = 0
			l = 0
			while l<len(self.fread):
				# Read device description
				if "name = " in self.fread[l] or "description =" in self.fread[l]:
					if self.fread[l].split()[0] not in self.wboutput.keys():
						self.wboutput[self.fread[l].split()[0]] = re.search('"(.*)"',self.fread[l].split("=")[1]).group(1)
					else:
						self.wboutput[self.fread[l].split()[0]] += re.search('"(.*)"',self.fread[l].split("=")[1]).group(1)
						
				# Read registers				
				elif "reg {" in self.fread[l]:
					reg_name = ""
					bit_position = 0
					l += 1
					while "};" not in self.fread[l]:
	
						if "align" in self.fread[l]:
							offset += int(self.fread[l].split("=")[1].replace(";",""))
						elif "prefix" in self.fread[l]:
							reg_name += re.search('"(.*)"',self.fread[l].split("=",1)[1]).group(1)
						elif "field {" in self.fread[l]:
							l += 1
	
							size = 0
							type = ""
							description = ""
							field_name = ""
							store_reg = True
							while "};" not in self.fread[l]:
								if "prefix =" in self.fread[l]:
									if "reserved" in self.fread[l].lower():
										store_reg = False							
									else:
										field_name = re.search('"(.*)"',self.fread[l].split("=",1)[1]).group(1)
										store_reg = True
								elif "access_bus =" in self.fread[l]:
									access = self.fread[l].split("=")[1].replace(";","")
								elif "type = " in self.fread[l] and "BIT" in self.fread[l]:
									size = 1
								elif "size = " in self.fread[l]:
									size = int(self.fread[l].split("=")[1].replace(";",""))
								elif "description = " in self.fread[l]:
									description = re.search('"(.*)"',self.fread[l].split("=",1)[1]).group(1)
								elif "align" in self.fread[l]:
									bit_offset = int(self.fread[l].split("=")[1].replace(";",""))
									if bit_position % bit_offset: 
										ad = bit_offset - (bit_position % bit_offset)
										bit_position += ad
								l +=1
	
							if store_reg:
								data = {}
								if field_name != "":
									reg = reg_name+"_"+field_name
								else:
									reg = reg_name
								data["bit_position"] = bit_position
								data["size"] = size
								data["access"] = access
								data["description"] = description
								bit_position += size
								data["address"] = offset
	
								if "regs" not in self.wboutput.keys():
									self.wboutput["regs"]={}
								
								self.wboutput["regs"][reg.upper()] = data
								
						l+=1
					
					offset +=1
				# Increment line counter
				l += 1
			
			# Write output to file
			file_generated = True
			try:
				with open(self.default_path+devName,"w") as f:
					pickle.dump(self.wboutput, f)
			except Exception, e:
				print str(e)
				file_generated = False
				return None
				
		return devName

	def removeDevice(self, devname=''):
		if os.path.isfile(self.default_path+devname):
			os.remove(self.default_path+devname)
			return True
		return False


	def getInputVendorID(self):
		vendorID = None
		
		for ln in self.fread:
			if "vendor_id = " in ln:
				vendorID = re.search('"(.*)"',ln.split("=")[1]).group(1)
				break
			
		if vendorID == None:
			while not vendorID:
				vendorID = raw_input ("VendorID not found in file %s.\nEnter VENDOR ID code (hex format, max. 8 bytes)" \
					"(i.e: a1ba for Alba or ce42 for CERN) or enter 'Q' to quit: "%self.wb_filename)
				if vendorID.lower() == "q":
					print "\nProgram aborted!!!\n"
					sys.exit()
				try:
					vendorID = int(vendorID.lower(),16)
					if vendorID > 0xffffffffffffffff:
						print "Number exceeds maximum value. Please enter hexadecimal " \
							"(max. 8 bytes) vendor ID value!!\n "
						vendorID = None
					else:
						return vendorID
				except:
					print "Incorrect number format!!! Please enter hexadecimal vendor ID value!!\n"
		
		return vendorID
	
	def getInputProduct(self):
		product = None
		
		for ln in self.fread:
			if "device_id = " in ln:
				product = re.search('"(.*)"',ln.split("=")[1]).group(1)
				break
			
		if product == None:
			while not product:
				product = raw_input ("\nProduct not found in file %s.\nEnter PRODUCT (hex format, max 4 bytes)" \
					"or enter 'Q' to quit: "%self.wb_filename)
				if product.lower() == "q":
					print "\nProgram aborted!!!\n"
					sys.exit()
				try:
					product = int(product.lower(),16)
					if product > 0xffffffff:
						print "Number exceeds maximum value. Please enter hexadecimal "\
							"(max. 4 bytes) product value!!\n"
						product = None
					else:
						return product
				except:
					print "Incorrect number format!!! Please enter hexadecimal product value!!\n"
		
		return product
	
	def getInputName(self):
		devname = None

		for ln in self.fread:
			if "name = " in ln:
				devname = re.search('"(.*)"',ln.split("=")[1]).group(1).rstrip().upper()
				break
			if "reg {" in ln:
				break
		
		if devname == None:
			while not devname:
				devname = raw_input ("\nDevice Name not found in file%s.\nEnter assigned DEVICE_NAME (max. lenght 10 chars) or enter 'Q' to quit: "%self.wb_filename)
				if devname.lower() == "q":
					print "\nProgram aborted!!!\n"
					sys.exit()
				
				devname = devname.replace(" ","_")
				if len(devname)>10:
					print "Name exceeds maximum lenght allowed.\nPlease enter name with a lenght lower than 10 characters\n"
					devname = None
				else:
					devname = devname.upper()
				
		return devname

def help():
	BOLD = '\033[1m'
	END = '\033[0m'
	
	print "ALINGEN is a tool that generates a pickle file for a device that contains a dict with the device information extracted from the wishbone file."
	print "This wishbone file, passed as argument and used to generate the FPGA code block, contains the register mapping and detailed infor for a"
	print "particular FPGA block.\nIt should be used as follows\n"
	print BOLD+"\t# alingen <command_1> <wb_file>"+END
	print "\nList of available commands are:\n"
	print BOLD+"\t-g <wb_filename> or ---generate=<wb_filename>:"+END
	print "\t\tGenerates te picklefile for the specified wb file.\n"
	print BOLD+"\t--help:"+END
	print "\t\tShows this help\n"
	print BOLD+"\t-d <devname> or --delete=<devname>:"+END
	print "\t\tDeletes an specific device pickle file."
	print "\n"
	
def generate_wb_file(file):
	if not file.endswith(".wb"):
		print "\nIncorrect filename selected: %s"%file
	else:
		name = gen.processWBData(file)
		if name is not None:
			print "\nDevice file generated succesfully!!"			
			print "* Generated device name ==>\t%s\n"%name
			print "* Located in: ==>\t\t%s\n"%gen.getInstallationPath()
		else:
			print "\nPROCESS ABORTED: Error while writing the output file!!\n"


if __name__ == "__main__":
	import os.path
	import getopt
	
	try:
		short_cmds = "d:hg:"
		long_cmds = ["help","delete=","generate="]
		opts, args = getopt.getopt(sys.argv[1:], short_cmds, long_cmds)
	except getopt.GetoptError as err:
		print (err) # will print something like "option -a not recognized"
		print "\nFor detailed command help use: alin --help\n" 
		sys.exit(2)
		
	opts_dict = dict(opts)

	# 0- show help
	if "-h" in opts_dict.keys() or "--help" in opts_dict.keys():
		help()
		sys.exit()
	
	gen = Generator()
	
	# 1- delete a device
	devname = None
	if "-d" in opts_dict.keys():
		devname = opts_dict["-d"]
	elif "--delete=" in opts_dict.keys():
		devname = opts_dict["--delete="]
	if devname is not None:
		if gen.removeDevice(devname):
			print "\nFile %s succesfully deleted"%devname
		else:
			print "\nNot possible to delete %s. File does not exits"%devname
		sys.exit()

	#2- generate a device file
	wb_file = None
	if "-g" in opts_dict.keys():
		wb_file = opts_dict["-g"]
	elif "--generate=" in opts_dict.keys():
		wb_file = opts_dict["--generate="]
		
	if wb_file is not None:
		if os.path.isdir(wb_file):
			wb_file_list = os.listdir(wb_file)
			for el in wb_file_list:
				generate_wb_file(wb_file+"/"+el)
		else:
			generate_wb_file(wb_file)
	else:
		help()

	sys.exit()
