# EAeDIP128-6 Python Driver
#
# Created: March 2015
#      by: Manolo Broseta at ALBA Computing Division
#

import smbus
import time, sys, select, math

from image_res import *

from alin.base import AlinLog

from distutils.sysconfig import get_python_lib

__CONFIG_FILE__ = "Config"
__CONFIG_MASK__ = "DISPLAY_"


class DisplayDriver(AlinLog):
	DEFAULT_I2C_ADDRESS = 0x94
	DEFAULT_I2C_BUS = 8
	
	DC1_BYTE = 0x11
	DC2_BYTE = 0x12
	
	ACK_VALUE = 0x06
	NACK_VALUE = 0x15
	
	DATA_LEN = 32
	
	def __init__(self, debug=False):
		AlinLog.__init__(self, debug=False, loggerName='DisplayDrv')
		
		self._debug = debug
		self._debuglevel = None
		self._i2c_address = self.DEFAULT_I2C_ADDRESS
		self._i2c_busnum = self.DEFAULT_I2C_BUS
		# Get default configuration from config file
		self.getConfigData()
		

		self.bus = smbus.SMBus(self._i2c_busnum)
		
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
					elif cm.startswith("I2C_BUS_"):
						try:
							self._i2c_busnum = int(cm.split("=")[1])
							self.logMessage("%s::getConfigData(): I2C_BUS_ set to %d"%(__CONFIG_MASK__,self._i2c_busnum),self.INFO)
						except Exception, e:
							self.logMessage("%s::getConfigData(): Can't get I2C_BUS_ %s"%(__CONFIG_MASK__, self._debug, str(e)),self.ERROR)
					elif cm.startswith("I2C_ADDRESS_"):
						try:
							self._i2c_address = int(cm.split("=")[1],16)
							self.logMessage("%s::getConfigData(): I2C_ADDRESS_ set to %s"%(__CONFIG_MASK__,hex(self._i2c_address)),self.INFO)
						except Exception, e:
							self.logMessage("%s::getConfigData(): Can't get I2C_ADDRESS_ %s"%(__CONFIG_MASK__, self._debug, str(e)),self.ERROR)
					 
		except Exception, e:
			self.logMessage("%s::getConfigData():: Not possible to get config file due to:"%__CONFIG_MASK__,self.ERROR)
			self.logMessage(str(e),self.ERROR)
			
	def setLogLevel(self, level):
		self._debuglevel = level
		self.logLevel(self._debuglevel)
	
	def SendData(self,arg):
		self.logMessage("SendData(): %s"%arg, self.DEBUG)
		
		try:
			cmds_list = arg.replace(","," ").split(" ")
		except:
			cmds_list = arg

		lst = []
		for cmd in cmds_list:
			if "^" in cmd:
				if cmd[1] in ['L','M','J']:
					lst.append(ord(cmd[1])-64)
			else:
				if cmd.isdigit():
					lst.append(int(cmd))
				else:
					for ch in cmd:
						if ord(ch) == 0x23:
							lst.append(0x1B)
						else:
							lst.append(ord(ch))
	#				if '#Z' not in cmd:
	#					lst.append(0x0A)

		send_list = []
		send_list.append(self.DC1_BYTE)
		bcc = self.DC1_BYTE

		# Fisrt value to be sent is te len of the protocol
		send_list.append(len(lst))
		
		# build the list to send
		for it in lst:
			bcc = bcc + it
			send_list.append(it)
		
		bcc = bcc + len(lst)
		
		# Add the checksum as last element
		bcc = bcc & 0xff
		send_list.append(bcc)
		
		if self._debug:
			txt = "SendData(): I2C_DATA= "
			for el in send_list:
				txt += hex(el)+", "
			self.logMessage(txt, self.DEBUG)
		
		try:
			self.bus.write_block_data(self._i2c_address, 0, send_list)
			ret_value = self.bus.read_byte(self._i2c_address)
		except Exception, e:
			self.logMessage("SendData() Error!! Not possible to access I2C due to %s"%str(e), self.ERROR)
			return
		
		return(ret_value)

	def SetProtocol(self, size=32,timeout=0):
		self.logMessage("SetProtocol() size=%d timeout=%d"%(size, timeout), self.DEBUG)
		send_list = [self.DC2_BYTE, 3, 0x44, size, timeout]
		
		# build the list to send
		bcc = 0
		for it in send_list:
			bcc = bcc + it
		
		# Add the checksum as last element
		bcc = bcc & 0xff
		send_list.append(bcc)

		if self._debug:
			txt = "SetProtocol(): I2C_WRITE_DATA= "
			for el in send_list:
				txt += hex(el)+", "
			self.logMessage(txt, self.DEBUG)

		try:
			self.bus.write_block_data(self._i2c_address, 0, send_list)
			ret_value = self.bus.read_byte(self._i2c_address)
			self.logMessage("SetProtocol() Returned value=%s"%str(ret_value), self.DEBUG)
		except Exception, e:
			self.logMessage("SetProtocol() Error!! Not possible to access I2C due to %s"%str(e), self.ERROR)
			return
		
		return(ret_value)

	def GetProtocol(self):
		self.logMessage("GetProtocol()", self.DEBUG)
		# Start Request for content of send buffer 
		send_list = [self.DC2_BYTE, 0x01, 0x50]
		bcc = 0
		for it in send_list:
			bcc = bcc + it
		bcc = bcc & 0xff
		send_list.append(bcc)

		if self._debug:
			txt = "GetProtocol(): I2C_WRITE_DATA= "
			for el in send_list:
				txt += hex(el)+", "
			self.logMessage(txt, self.DEBUG)
			
		try:
			self.bus.write_block_data(self._i2c_address, 0, send_list)
			
			ret_value = []	
			if self.bus.read_byte(self._i2c_address) == self.ACK_VALUE:
				ret_value = self.bus.read_i2c_block_data(self._i2c_address,0)
				self.logMessage("GetProtocol() Returned value=%s"%str(ret_value), self.DEBUG)
		except Exception, e:
			self.logMessage("GetProtocol() Error!! Not possible access I2C due to %s"%str(e), self.ERROR)
			return
			
		return ret_value

	def GetData(self):
		self.logMessage("GetData()", self.DEBUG)
		# Start Request for content of send buffer 
		send_list = [self.DC2_BYTE, 0x01, 0x53]
		bcc = 0
		for it in send_list:
			bcc = bcc + it
		bcc = bcc & 0xff
		send_list.append(bcc)

		if self._debug:
			txt = "GetData(): I2C_WRITE_DATA= "
			for el in send_list:
				txt += hex(el)+", "
			self.logMessage(txt, self.DEBUG)

		try:
			self.bus.write_block_data(self._i2c_address, 0, send_list)
			
			ret_value = []	
			if self.bus.read_byte(self._i2c_address) == self.ACK_VALUE:
				ret_value = self.bus.read_i2c_block_data(self._i2c_address,0)
				self.logMessage("GetData() Returned value=%s"%str(ret_value), self.DEBUG)			
		except Exception, e:
			self.logMessage("GetData() Error!! Not possible access I2C due to %s"%str(e), self.ERROR)
			return
		
		return ret_value
	
	def ClearScreen(self):
		self.logMessage("ClearScreen()", self.DEBUG)
		r_d = self.SendData("^L")
		r_d = self.SendData("#DL")
		r_d = self.SendData("#RL 0,0,128,64")
		return r_d
			
	def PanelSettings(self, bright= 100, illumination=True):
		self.logMessage("PanelSettings() bright=%d illumination=%s"%(bright, illumination), self.DEBUG)
		if bright >100 : bright = 100
		self.SendData("#YH "+str(bright))	
		self.SendData("#YL "+str(int(illumination)))

	def DrawImage(self,pos_x=0,pos_y=0,image=[]):
		self.logMessage("DrawImage() X pos=%d Y pos=%d"%(pos_x, pos_y), self.DEBUG)
		width = image[0]
		real_width = ((width/8)*8)+8
		if real_width>128:real_width = 128
		blocks = real_width/8
		height = image[1]
		init_pos_x = pos_x
		init_pos_y = pos_y

		#for a in range(0,len(image)-2,blocks):
		for a in range(len(image)-2):
			y = ((a * 8) / real_width)
			x = ((a * 8 ) - (y * real_width)) 
			
			y += init_pos_y
			x += init_pos_x
			
			if x>120 or y>63: pass
		
			#dato = image[(a+2):(a+2+blocks)]
			#dato_inv = [int("{:08b}".format(a)[::-1],2) for a in dato]
			#temp = "#UL  "+str(x)+","+str(y)+","+str(blocks*8)+",1"
			#for a in dato_inv:
			#	temp += ","+str(a)
			dato = image[a+2]
			dato_inv = int("{:08b}".format(dato)[::-1],2)
			temp = "#UL  "+str(x)+","+str(y)+",8,1,"+str(dato_inv)
			self.SendData(temp)
			if self._debug:
				self.logMessage(temp, self.DEBUG)
