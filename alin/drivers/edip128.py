# EAeDIP128-6 Python Driver
#
# Created: March 2015
#      by: Manolo Broseta at ALBA Computing Division
#




from alin.base import AlinLog
from alin.base import getConfigData
from image_res import *
import math
import select
import smbus
import sys
import time

_CONFIG_MASK = "EDIP128_"

_DEFAULT_I2C_ADDRESS = 0x94
_DEFAULT_I2C_BUS = 7

_DC1_BYTE = 0x11
_DC2_BYTE = 0x12

_ACK_VALUE = 0x06
_NACK_VALUE = 0x15

_DATA_LEN = 32


class EDIP128(AlinLog):
	def __init__(self, debug=False):
		AlinLog.__init__(self, debug=False, loggerName='EDIP128')
		
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
	
	def SendData(self,arg):
		self.logMessage("SendData(): %s"%arg, self.DEBUG)
		
		cmds_list = []
		try:
			if "^" in arg:
				cmds_list.append(arg)
			else:
				cmds_list.append(arg[arg.index('#'):3])
				cmds_list = cmds_list + arg[(arg.index('#')+3):].split(",")
		except Exception, e:
			self.logMessage("SendData() Error!! Can't decode command %s due to %s"%(arg, str(e)), self.ERROR)
			return

		lst = []
		for cmd in cmds_list:
			if "^" in cmd:
				if cmd[1] in ['L','M','J']:
					lst.append(ord(cmd[1])-64)
			else:
				try:
					lst.append(int(cmd))
				except: 
					if '"' in cmd: 
						cmd = cmd.replace('"','')
					for ch in cmd:
						if ord(ch) == 0x23:
							lst.append(0x1B)
						else:
							lst.append(ord(ch))

		send_list = []
		send_list.append(_DC1_BYTE)
		bcc = _DC1_BYTE

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
			self.i2c.write_i2c_block_data(self._i2c_address, 0, send_list)
			ret_value = self.i2c.read_byte(self._i2c_address)
		except Exception, e:
			self.logMessage("SendData() Error!! Not possible to access I2C due to %s"%str(e), self.ERROR)
			return
		
		return(ret_value)

	def SetProtocol(self, size=32,timeout=0):
		self.logMessage("SetProtocol() size=%d timeout=%d"%(size, timeout), self.DEBUG)
		send_list = [_DC2_BYTE, 3, 0x44, size, timeout]
		
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
			self.i2c.write_block_data(self._i2c_address, 0, send_list)
			ret_value = self.i2c.read_byte(self._i2c_address)
			self.logMessage("SetProtocol() Returned value=%s"%str(ret_value), self.DEBUG)
		except Exception, e:
			self.logMessage("SetProtocol() Error!! Not possible to access I2C due to %s"%str(e), self.ERROR)
			return
		
		return(ret_value)

	def GetProtocol(self):
		self.logMessage("GetProtocol()", self.DEBUG)
		# Start Request for content of send buffer 
		send_list = [_DC2_BYTE, 0x01, 0x50]
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
			self.i2c.write_block_data(self._i2c_address, 0, send_list)
			
			ret_value = []	
			if self.i2c.read_byte(self._i2c_address) == _ACK_VALUE:
				ret_value = self.i2c.read_i2c_block_data(self._i2c_address,0)
				self.logMessage("GetProtocol() Returned value=%s"%str(ret_value), self.DEBUG)
		except Exception, e:
			self.logMessage("GetProtocol() Error!! Not possible access I2C due to %s"%str(e), self.ERROR)
			return
			
		return ret_value

	def GetData(self):
		self.logMessage("GetData()", self.DEBUG)
		# Start Request for content of send buffer 
		send_list = [_DC2_BYTE, 0x01, 0x53]
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
			self.i2c.write_block_data(self._i2c_address, 0, send_list)
			
			ret_value = []	
			if self.i2c.read_byte(self._i2c_address) == _ACK_VALUE:
				ret_value = self.i2c.read_i2c_block_data(self._i2c_address,0)
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
