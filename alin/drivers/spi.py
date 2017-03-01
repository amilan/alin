## @package alinspinctrl.py 
#    File containing the device class, to access device registers
#
#    Author = "Jose Avila & Manuel Broseta"
#    Copyright = "Copyright 2015, ALBA"
#    Version = "1.1"
#    Email = "javila@cells.es"
#    Status = "Development"
#    History:
#   01/08/2015 - file created by Jose Avila
#    06/11/2015 - File included in SW project by M.Broseta
#                 Doxygen detailed info addedfrom ctabem_dev import *

__author__ = "Jose Avila & Manuel Broseta"
__copyright__ = "Copyright 2015, ALBA"
__license__ = "GPLv3 or later"
__version__ = "1.0"
__email__ = "javila@cells.es"+" mbroseta@cells.es"
__status__ = "Development"

from alin.base import AlinDevice
from alin.base import getConfigData

import os
import threading
import time


_CONFIG_MASK = "SPI_"

_CA1_EEPROM     = 0x00 # Chip Select for the EEPROM Memory of Current Amplifier #1.
_CA1_PEXP1      = 0x01 # Chip Select for the Port Expander 1 of the Current Amplifier #1
_CA1_PEXP2      = 0x02 # Chip Select for the Port Expander 2 of the Current Amplifier #1
_CA1_DAC        = 0x03 # Chip Select for the DAC of the Current Amplifier #1.
_CA1_TEMP       = 0x04 # Chip Select for the Temperature Sensor of Current Amplifier #1

_CA2_EEPROM     = 0x05 # Chip Select for the EEPROM Memory of Current Amplifier #2.
_CA2_PEXP1      = 0x06 # Chip Select for the Port Expander 1 of the Current Amplifier #2
_CA2_PEXP2      = 0x07 # Chip Select for the Port Expander 2 of the Current Amplifier #2
_CA2_DAC        = 0x08 # Chip Select for the DAC of the Current Amplifier #2.
_CA2_TEMP       = 0x09 # Chip Select for the Temperature Sensor of Current Amplifier #2

_CA3_EEPROM     = 0x0a # Chip Select for the EEPROM Memory of Current Amplifier #3.
_CA3_PEXP1      = 0x0b # Chip Select for the Port Expander 1 of the Current Amplifier #3
_CA3_PEXP2      = 0x0c # Chip Select for the Port Expander 2 of the Current Amplifier #3
_CA3_DAC        = 0x0d # Chip Select for the DAC of the Current Amplifier #3.
_CA3_TEMP       = 0x0e # Chip Select for the Temperature Sensor of Current Amplifier #3

_CA4_EEPROM     = 0x0f # Chip Select for the EEPROM Memory of Current Amplifier #4.
_CA4_PEXP1      = 0x10 # Chip Select for the Port Expander 1 of the Current Amplifier #4
_CA4_PEXP2      = 0x11 # Chip Select for the Port Expander 2 of the Current Amplifier #4
_CA4_DAC        = 0x12 # Chip Select for the DAC of the Current Amplifier #4.
_CA4_TEMP       = 0x13 # Chip Select for the Temperature Sensor of Current Amplifier #4

_CACB_TEMP      = 0x14 # Chip Select for the Temperature Sensor of CA Carrier Board. Active Low.
_CACB_EEPROM    = 0x15 # Chip Select for the EEPROM Memory of CA Carrier Board.

_FEB_PEXP1      = 0x18 # Chip Select for the Port Expander 1 of the Front End Board
_FEB_PEXP2      = 0x19 # Chip Select for the Port Expander 2 of the Front End Board
_FEB_PEXP3      = 0x1a # Chip Select for the Port Expander 3 of the Front End Board
_FEB_TEMP       = 0x1b # Chip Select for the Temperature Sensor of the Front End Board
_FEB_EEPROM     = 0x1c # Chip Select for the EEPROM of the Front End Board

_N_CHANNELS     = 4 # Number of channels defined

_N_DIFF_IO_PORTS    = 9 # Number of I/O pins
_N_HS_IO_PORTS      = 4 # Number of high speed I/O ports
_N_SUPPLY_PORTS     = 4 # Number of Supply Ports

## SPICtrl class
#
# Main class that takes care of the SPI Driver control. The ALba INstrumentation Low Speed HW configuration and monitoring is done via a SPI bus.
# The SPI lines are controlled from the FPGA and the controlled devices with this SPI bus are placed in the Front-End Board (FEB), in the Current
# Amplifiers Carrier Board (CACB) and in the 4 Current Amplifiers (CAp pickel file created with the coresponding memory area defined in the SDB
# This API provides functions to control and get information of the devices connected to that SPI bus
class Spi(AlinDevice):
    ## The constructor.
    #  @param device Device name of tha file that contains the SPI core registers mapping
    def __init__(self, dev='SPI', debug=False):
        AlinDevice.__init__(self, device=dev, debug=debug, logger='SPI    ')

        # Get default configuration from config file
        self._debug = debug
        self._device = dev
        self.configure()
                
        # Init variables 
        self._ca_init = [False]*_N_CHANNELS
        self._inversion = [None]*_N_CHANNELS
        self._post_filter = [None]*_N_CHANNELS
        self._pre_filter = [None]*_N_CHANNELS
        self._filter = [None]*_N_CHANNELS
        self._ti_gain = [None]*_N_CHANNELS
        self._v_gain = [None]*_N_CHANNELS
        self._range = [None]*_N_CHANNELS
        self._dacgain = [None]*_N_CHANNELS
        
        self._diff_io_ports_h = None # I/O ports from 9 to 15 (only 9 is used)
        self._diff_io_ports_l = None # I/O ports from 0 to 8
        self._hs_io_ports = None
        self._supply_ports = None
        self._dac_gain = None
        
        self._eeprom_dict = {'CA1': _CA1_EEPROM,
                             'CA2': _CA2_EEPROM,
                             'CA3': _CA3_EEPROM,
                             'CA4': _CA4_EEPROM,
                             'CACB': _CACB_EEPROM,
                             'FEB': _FEB_EEPROM,
                             }
        
        self._semaphore = threading.Semaphore(1)
        
        self.logMessage("__init__() Initialized ", self.DEBUG)
            
    def configure(self):
        # Get default configuration from config file
        configDict = getConfigData(_CONFIG_MASK)
        self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else self._debug
        self._debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 40
        self._device = configDict["DEVICE_"] if "DEVICE_" in configDict.keys() else self._device

        self.setDevice(devname=self._device)
        
        # Logging
        self.logLevel(self._debuglevel)
        self.logEnable(self._debug)
        
        self.logMessage("configure() %s configured"%_CONFIG_MASK, self.DEBUG)     
        
    def init(self):
        self.logMessage("init(): Starting SPI channels", self.DEBUG)
        
        for i in range(0,4):
            self.caInit(i)
            self.caSetRange(i, '1ma')
            self.caSetFilter(i, '3200Hz')
            self.caSetOffset(i, 2048)
            self.caSetInv(i,0)
   
        self.logMessage("init(): Starting FE board", self.DEBUG)
        self.feInit()
            
        self.logMessage("init(): SPI module Started!!", self.DEBUG)
        
    ## caReadTemp(channel)
    #  This function reads the temperature of the current amplifer modules.
    #  @param chennel There are four CA blocks. This parameters is used to select the CA block to read its temperature 
    def caReadTemp(self, channel):
        if channel<0 or channel>3:
            self.logMessage("caReadTemp::Incorrect channel %s"%(str(channel)), self.ERROR)
            return 

        caTempList = [_CA1_TEMP, _CA2_TEMP, _CA3_TEMP, _CA4_TEMP]    
        
        # Protect SPI Read/Write
        self._semaphore.acquire(True)                

        self.logMessage("caReadTemperature::Reading temp CA%s"%(str(channel)), self.DEBUG)

        try:
            value = self.__spiRead(caTempList[channel], 0, 0, 0, 1, 0x0d)        
        except: 
            self.logMessage("caReadTemperature::Incorrect channel %s"%(str(channel)), self.ERROR)
            self._semaphore.release()
            return    

        value = value*0.0625
        self.logMessage("caReadTemperature::Temperature of CA%s: %.4f" %(str(channel), value), self.DEBUG)
        
        # Protect SPI Read/Write
        self._semaphore.release()        
        
        return value
    
    
    ## caCBReadTemp()
    #  This function reads the temperature of the current amplifer carrier board
    #  @param chennel There are four CA blocks. This parameters is used to select the CA block to read its temperature 
    def caCBReadTemp(self):
        
        # Protect SPI Read/Write
        self._semaphore.acquire(True)        
        
        self.logMessage("caCBReadTemp::Reading temp CACB", self.DEBUG)
        value = self.__spiRead(_CACB_TEMP, 0, 0, 0, 1, 0x0d)
        value = value*0.0625
        self.logMessage("caCBReadTemp::Temperature of Current Amplifier Carrier Board: %.4f" %(value), self.DEBUG)
        
        # Protect SPI Read/Write
        self._semaphore.release()
        
        return value    
    
    ## caInit(channel)
    #  This function initializes a current amplifer modules.
    #  @param channel There are four CA blocks. This parameters is used to select the CA block to read its temperature 
    def caInit(self, ch):
        self.logMessage("caInit::Init CA%s"%str(ch), self.DEBUG)
        if ch<0 or ch>3:
            self.logMessage("caInit::Incorrect channel %s"%(str(ch)), self.ERROR)
            return 

        caAddrSet = [[_CA1_EEPROM, _CA1_PEXP1, _CA1_PEXP2, _CA1_DAC],
                     [_CA2_EEPROM, _CA2_PEXP1, _CA2_PEXP2, _CA2_DAC],
                     [_CA3_EEPROM, _CA3_PEXP1, _CA3_PEXP2, _CA3_DAC],
                     [_CA4_EEPROM, _CA4_PEXP1, _CA4_PEXP2, _CA4_DAC],
                    ]
        
        # Step1: Dummy readings all items CA module and DAC load 0V 
        self.logMessage("caInit::Step 1 dummy readings CA%d module"%ch, self.DEBUG)        
        self.caReadTemp(ch)
        
        # Protect SPI Read/Write
        self._semaphore.acquire(True)                
        
        self.__spiRead(caAddrSet[ch][1], 1, 0x4100, 0x10, 1, 0x08)
        self.__spiRead(caAddrSet[ch][2], 1, 0x4100, 0x10, 1, 0x08)
        self.__spiRead(caAddrSet[ch][0], 1, 0x0300, 0x10, 1, 0x08)
        self.__spiWrite(caAddrSet[ch][3], 1, 0, 0x0c, 0, 0)
        
        # Step2: Real initialization:
        # - PE1: write IODIR register all to 0 (all bits as output)
        self.__spiWrite(caAddrSet[ch][1], 1, 0x00400000, 0x18, 0, 0)
        val = self.__spiRead(caAddrSet[ch][1], 1, 0x00004100, 0x10, 1, 0x08)
        self.logMessage("caInit::Value of IODIR register of PE1 of CA%d : %d" %(ch, val), self.DEBUG)

        # - PE2: write IODIR register all to 0 (all bits as output)
        self.__spiWrite(caAddrSet[ch][2], 1, 0x00400000, 0x18, 0, 0)
        val = self.__spiRead(caAddrSet[ch][2], 1, 0x00004100, 0x10, 1, 0x08)
        self.logMessage("caInit::Value of IODIR register of PE1 of CA%d : %d" %(ch, val), self.DEBUG)
                       
        # Step3: Configuration of both Port Expanders of Current Amplifier:
        # INVERSION ON;  TI_GAIN 10k; POST_F 3200Hz; PRE_F 3500Hz; V_GAIN 1
        self.__spiWrite(caAddrSet[ch][1], 1, 0x00400908, 0x18, 0, 0)
        val = self.__spiRead(caAddrSet[ch][1], 1, 0x00004109, 0x10, 1, 0x08)
        self.logMessage("caInit::Value of GPIO register of PE1 of CA%d : %d" %(ch, val), self.DEBUG)
        self.__spiWrite(caAddrSet[ch][2], 1, 0x00400918, 0x18, 0, 0)
        val = self.__spiRead(caAddrSet[ch][2], 1, 0x00004109, 0x10, 1, 0x08)
        self.logMessage("caInit::Value of GPIO register of PE1 of CA%d : %d" %(ch, val), self.DEBUG)
        
        # Protect SPI Read/Write
        self._semaphore.release()
        
        self.caReadTemp(ch)
        self.logMessage("caInit::Init CA%s complete!!"%str(ch), self.DEBUG)
        
        # Init local variables
        self._ca_init[ch] = True
        self._inversion[ch] = True

        self._post_filter[ch] = '3200'
        self._pre_filter[ch] = '3500'
        self._filter[ch] = '3200'
        
        self._ti_gain[ch] = '10k'
        self._v_gain[ch] = '1'
        self._range[ch] = '1mA'
        
    def caGetInit(self, channel):
        if channel<0 or channel>3:
            self.logMessage("caGetInit::Incorrect channel %s"%(str(channel)), self.ERROR)
            return None

        val = None
        try:
            val = self._ca_init[channel]
            self.logMessage("caGetInit::Get Init state CA%d=%s"%(channel,str(val)), self.DEBUG)
        except:
            self.logMessage("caGetInit::Incorrect parameters channel=%d"%(channel), self.ERROR)

        return val        
        
    ## caSetTIGain(channel,gain)
    #  This function sets the Trans Impedance Gain for a particular CA channel
    #  @param channel There are four CA blocks. This parameters is used to select the CA block to read its temperature 
    #  @param gain Gain value expected 
    def caSetTIGain(self, channel, gain ):
        if channel<0 or channel>3:
            self.logMessage("caSetTIGain::Incorrect channel %s"%(str(channel)), self.ERROR)
            return 

        maskErase = 0x87    #Mask to erase the TI Gain bits (bits D6-D3)
        caAddrSet = [_CA1_PEXP1, _CA2_PEXP1, _CA3_PEXP1, _CA4_PEXP1]
        caTIGainSet = {'10k':    0x08,
                        '1M':    0x10,
                        '100M':    0x20,
                        '1G':    0x40,
                        '10G':    0x00
                        }
        
        try:
            caAddr = caAddrSet[channel]
            maskGain = caTIGainSet[gain]
        except:
            self.logMessage("caSetTIGain::Incorrect parameters channel=%d gain=%s"%(channel,gain), self.ERROR)
            return
        
        # Protect SPI Read/Write
        self._semaphore.acquire(True) 
        self.logMessage("caSetTIGain::Set Transimpedance CA%s gain %s"%(str(channel),str(gain)), self.DEBUG)
        
        #Process to generate data to send from read data
        val = self.__spiRead(caAddr, 1, 0x00004109, 0x10, 1, 0x08)
        val = val & maskErase        #bits D6-D3 erased
        val = val | maskGain        #bits D6-D3 set according to the mask
        val = val | 0x00400900        #necessary bits (opcode and address) are added for proper communication
        self.__spiWrite(caAddr, 1, val, 0x18, 0, 0)
        
        #read GPIO register of PE1 (just for confirmation, it can be commented)
        val = self.__spiRead(caAddr, 1, 0x00004109, 0x10, 1, 0x08)
        
        # update local variable
        self._ti_gain[channel] = gain

        # Protect SPI Read/Write
        self._semaphore.release()

        
    def caGetTIGain(self, channel):
        if channel<0 or channel>3:
            self.logMessage("caGetTIGain::Incorrect channel %s"%(str(channel)), self.ERROR)
            return None

        val = None
        try:
            val = self._ti_gain[channel]
            self.logMessage("caGetTIGain::Get Transimpedance CA%d gain=%s"%(channel,val), self.DEBUG)
        except:
            self.logMessage("caGetTIGain::Incorrect parameters channel=%d"%(channel), self.ERROR)

        return val
        
        
    ## caInv(channel,inv)
    #  This function sets the Inverse gain for a particular CA channel
    #  @param channel There are four CA blocks. This parameters is used to select the CA block to read its temperature 
    #  @param inv Inverse gain value expected 
    def caSetInv(self, channel, inv ):
        if channel<0 or channel>3:
            self.logMessage("caSetInv::Incorrect channel %s"%(str(channel)), self.ERROR)
            return

        maskErase = 0x7f    #Mask to erase the INV bit (bit D7)
        caAddrSet = [_CA1_PEXP1, _CA2_PEXP1, _CA3_PEXP1, _CA4_PEXP1]
        try:
            caAddr = caAddrSet[channel]
        except:
            self.logMessage("caSetInv::Incorrect channel=%d"%(channel,gain), self.ERROR)
            return
        
        # Protect SPI Read/Write
        self._semaphore.acquire(True) 
        self.logMessage("caSetInv::Set Inversion %s CA%d"%(inv, channel), self.DEBUG)
        
        if inv:
            maskInv = 0x00 #inversion by default
        else:
            maskInv = 0x80
            
        #Process to generate data to send from read data
        val = self.__spiRead(caAddr, 1, 0x00004109, 0x10, 1, 0x08)
        val = val & maskErase        #bit D7 erased
        val = val | maskInv            #bit D7 set according to the mask
        val = val | 0x00400900        #necessary bits (opcode and address) are added for proper communication
        self.__spiWrite(caAddr, 1, val, 0x18, 0, 0)
        
        #read GPIO register of PE1 (just for confirmation, it can be commented)
        val = self.__spiRead(caAddr, 1, 0x00004109, 0x10, 1, 0x08)

        # update local variable
        self._inversion[channel] = inv
        
        # Protect SPI Read/Write
        self._semaphore.release()
        
    def caGetInv(self, channel):
        if channel<0 or channel>3:
            self.logMessage("caGetInv::Incorrect channel %s"%(str(channel)), self.ERROR)
            return None
        
        val = None
        try:
            val = self._inversion[channel]
            self.logMessage("caGetInv::Get Inversion CA%d value=%s"%(channel, val), self.DEBUG)
        except:
            self.logMessage("caGetInv::Incorrect parameters channel=%d"%(channel), self.ERROR)

        return val
        
    ## caPostFilter(channel,postf)
    #  This function sets a the post filter value for a particular CA channel
    #  @param channel There are four CA blocks. This parameters is used to select the CA block to read its temperature 
    #  @param postf Postfilter value to set
    def caSetPostFilter(self, channel, postf ):
        if channel<0 or channel>3:
            self.logMessage("caSetPostFilter::Incorrect channel %s"%(str(channel)), self.ERROR)
            return
    
        maskErase = 0xf8    # Mask to erase the Post Filter bits (bits D2-D0)
        caAddrSet = [_CA1_PEXP1, _CA2_PEXP1, _CA3_PEXP1, _CA4_PEXP1]
        caPostFilterSet = {'3200Hz':    0x00,
                            '100Hz':    0x04,
                            '10Hz':    0x02,
                            '1Hz':    0x01,
                        }
        try:
            caAddr = caAddrSet[channel]
            maskPostf = caPostFilterSet[postf]
        except:
            self.logMessage("caSetPostFilter::Incorrect channel=%s or PostF=%s"%(str(channel),postf), self.ERROR)
            return
        
        # Protect SPI Read/Write
        self._semaphore.acquire(True)         
        self.logMessage("caSetPostFilter::Set PostFilter CA%s value: %s"%(str(channel), postf), self.DEBUG)
        
        #Process to generate data to send from read data
        val = self.__spiRead(caAddr, 1, 0x00004109, 0x10, 1, 0x08)
        val = val & maskErase        #bit D7 erased
        val = val | maskPostf            #bit D7 set according to the mask
        val = val | 0x00400900        #necessary bits (opcode and address) are added for proper communication
        self.__spiWrite(caAddr, 1, val, 0x18, 0, 0)
        
        #read GPIO register of PE1 (just for confirmation, it can be commented)
        val = self.__spiRead(caAddr, 1, 0x00004109, 0x10, 1, 0x08)
        self.logMessage("caSetPostFilter::Value of GPIO register of PE1 of CA%d : %d" %(channel, val), self.DEBUG)
        
        # update local variable
        self._post_filter[channel] = postf

        # Protect SPI Read/Write
        self._semaphore.release()
        
    def caGetPostFilter(self, channel):
        if channel<0 or channel>3:
            self.logMessage("caGetPostFilter::Incorrect channel %s"%(str(channel)), self.ERROR)
            return None
        
        val = None
        try:
            val = self._post_filter[channel]
            self.logMessage("caGetPostFilter::Get PostFilter CA%d value=%s"%(channel, val), self.DEBUG)
        except:
            self.logMessage("caGetPostFilter::Incorrect parameters channel=%d"%(channel), self.ERROR)

        return val
    
    ## caPreFilter(channel,postf)
    #  This function sets a the pre filter value for a particular CA channel
    #  @param channel There are four CA blocks. This parameters is used to select the CA block to read its temperature 
    #  @param pref Prefilter value to set
    def caSetPreFilter(self, channel, pref ):
        if channel<0 or channel>3:
            self.logMessage("caSetPreFilter::Incorrect channel %s"%(str(channel)), self.ERROR)
            return None

        maskErase = 0x0f    # Mask to erase the Post Filter bits (bits D7-D4)
        caAddrSet = [_CA1_PEXP2, _CA2_PEXP2, _CA3_PEXP2, _CA4_PEXP2]
        caPreFilterSet = {'3500Hz':    0x10,
                            '100Hz':    0x20,
                            '10Hz':    0x40,
                            '1Hz':    0x80,
                            '0.5Hz':    0x00,
                        }
        
        try:
            caAddr = caAddrSet[channel]
            maskPref = caPreFilterSet[pref]
        except:
            self.logMessage("caSetPreFilter::Incorrect channel=%d or PreF=%s"%(channel,pref), self.ERROR)
            return

        # Protect SPI Read/Write
        self._semaphore.acquire(True)    
        self.logMessage("caSetPreFilter::Set PostFilter CA%s value: %s"%(str(channel), pref), self.DEBUG)
            
        #Process to generate data to send from read data
        val = self.__spiRead(caAddr, 1, 0x00004109, 0x10, 1, 0x08)
        val = val & maskErase        #bit D7 erased
        val = val | maskPref            #bit D7 set according to the mask
        val = val | 0x00400900        #necessary bits (opcode and address) are added for proper communication
        self.__spiWrite(caAddr, 1, val, 0x18, 0, 0)
        
        #read GPIO register of PE1 (just for confirmation, it can be commented)
        val = self.__spiRead(caAddr, 1, 0x00004109, 0x10, 1, 0x08)
        
        # update local variable
        self._pre_filter[channel] = pref

        # Protect SPI Read/Write
        self._semaphore.release()        
        
    def caGetPreFilter(self, channel):
        val = None

        if channel<0 or channel>3:
            self.logMessage("caGetPreFilter::Incorrect channel %s"%(str(channel)), self.ERROR)
            return None

        try:
            val = self._pre_filter[channel]
            self.logMessage("caGetPreFilter::Get PreFilter CA%d value=%s"%(channel, val), self.DEBUG)
        except:
            self.logMessage("caGetPreFilter::Incorrect parameters channel=%d"%(channel), self.ERROR)

        return val
        
    ## caVGain(channel,vgain)
    #  This function sets the voltage Gain for a particular CA channel
    #  @param channel There are four CA blocks. This parameters is used to select the CA block to read its temperature 
    #  @param vgain Voltage gain value to set
    def caSetVGain(self, channel, vgain ):
        if channel<0 or channel>3:
            self.logMessage("caSetVGain::Incorrect channel %s"%(str(channel)), self.ERROR)
            return None

        maskErase = 0xf0    #Mask to erase the TI Gain bits (bits D3-D0)
        caAddrSet = [_CA1_PEXP2, _CA2_PEXP2, _CA3_PEXP2, _CA4_PEXP2]
        caVGainSet = {'1':    0x08,
                    '10':    0x04,
                    '50':    0x02,
                    '100':    0x01,
                    'sat':    0x00
                    }
        
        try:
            caAddr = caAddrSet[channel]
            maskVgain = caVGainSet[vgain]
        except:
            self.logMessage("caSetVGain::Incorrect parameters channel=%d gain=%s"%(channel,str(gain)), self.ERROR)
            return

        # Protect SPI Read/Write
        self._semaphore.acquire(True)  
        self.logMessage("caSetVGain::Set Voltage CA%d gain %s"%(channel,str(vgain)), self.DEBUG)

        #Process to generate data to send from read data
        val = self.__spiRead(caAddr, 1, 0x00004109, 0x10, 1, 0x08)
        val = val & maskErase        #bits D6-D3 erased
        val = val | maskVgain        #bits D6-D3 set according to the mask
        val = val | 0x00400900        #necessary bits (opcode and address) are added for proper communication
        self.__spiWrite(caAddr, 1, val, 0x18, 0, 0)
        
        #read GPIO register of PE1 (just for confirmation, it can be commented)
        val = self.__spiRead(caAddr, 1, 0x00004109, 0x10, 1, 0x08)
        
        # update local variable
        self._v_gain[channel] = vgain

        # Protect SPI Read/Write
        self._semaphore.release()        
        
    def caGetVGain(self, channel):
        if channel<0 or channel>3:
            self.logMessage("caGetVGain::Incorrect channel %s"%(str(channel)), self.ERROR)
            return

        val = None
        try:
            val = self._v_gain[channel]
            self.logMessage("caGetVGain::Get Voltage gain CA%d value=%s"%(channel, val), self.DEBUG)
        except:
            self.logMessage("caGetVGain::Incorrect parameters channel=%s"%(channel), self.ERROR)

        return val
        
    ## caRange(channel,rang)
    #  This function sets the range for a particular CA channel, which results of combining the transimpedance and voltage gains
    #  @param channel There are four CA blocks. This parameters is used to select the CA block to read its temperature 
    #  @param rang Range value to set
    def caSetRange(self, channel, rang ):
        if channel<0 or channel>3:
            self.logMessage("caRange::Incorrect channel %s"%(str(channel)), self.ERROR)
            return None

        self.logMessage("caRange::Set range value %s for CA%s"%(str(rang), str(channel)), self.DEBUG)

        # unit fixed to mA
        range_vals = {  '1mA':     {'tigain': '10k',    'vgain': '1'},
                        '100uA':   {'tigain': '10k' ,    'vgain': '10'},
                        '10uA':    {'tigain': '1M',    'vgain': '1'},
                        '1uA':     {'tigain': '1M',    'vgain': '10'},
                        '100nA':   {'tigain': '100M',    'vgain': '1'},
                        '10nA':    {'tigain': '1G',    'vgain': '1'},
                        '1nA':     {'tigain': '10G',    'vgain': '1'},
                        '100pA':   {'tigain': '10G',    'vgain': '10'},
                    }
        
        for el in range_vals.keys():
            if el.lower() == rang.lower():
                self.caSetTIGain(channel,range_vals[el]['tigain'])
                self.caSetVGain(channel,range_vals[el]['vgain'])
        
                # update local variable
                self._range[channel] = el
                return

        self.logMessage("caRange::Incorrect range Value %s"%(str(rang)), self.ERROR)
        return
        
    def caGetRange(self, channel):
        if channel<0 or channel>3:
            self.logMessage("caGetRange::Incorrect channel %s"%(str(channel)), self.ERROR)
            return None
        
        val = None
        try:
            val = self._range[channel]
            self.logMessage("caGetRange::Get range CA%d value=%s"%(channel, val), self.DEBUG)
        except:
            self.logMessage("caGetRange::Incorrect parameters channel=%d"%(channel), self.ERROR)

        return val

            
    ## caFilter(channel,vgain)
    #  This function sets the Filter for a particular CA channel, setting the pre and post filters.
    #  @param channel There are four CA blocks. This parameters is used to select the CA block to read its temperature 
    #  @param filt Filter value to set
    def caSetFilter(self, channel, filt ):
        if channel<0 or channel>3:
            self.logMessage("caSetFilter::Incorrect channel %s"%(str(channel)), self.ERROR)
            return None

        self.logMessage("caSetFilter::Set filter value %s for CA%s"%(str(filt), str(channel)), self.DEBUG)
        
        filter_vals = {'3200Hz':    {'post': '3200Hz',    'pre': '3500Hz'},
                        '100Hz':    {'post': '100Hz',     'pre': '100Hz'},
                        '10Hz':     {'post': '10Hz',      'pre': '10Hz'},
                        '1Hz':      {'post': '1Hz',       'pre': '1Hz'},
                        '0.5Hz':    {'post': '1Hz',       'pre': '0.5Hz'},
                        }
        
        for el in filter_vals.keys():
            if el.lower() == filt.lower():
                self.caSetPostFilter(channel,filter_vals[el]['post'])
                self.caSetPreFilter(channel,filter_vals[el]['pre'])

                # update local variable
                self._filter[channel] = el
                return

        self.logMessage("caSetFilter::Incorrect Filter Value %s"%(str(filt)), self.ERROR)
        return
        
        
    def caGetFilter(self, channel):
        if channel<0 or channel>3:
            self.logMessage("caGetFilter::Incorrect channel %s"%(str(channel)), self.ERROR)
            return None

        val = None
        try:
            val = self._filter[channel]
            self.logMessage("caGetFilter::Get filter CA%d value=%s"%(channel, val), self.DEBUG)
        except:
            self.logMessage("caGetFilter::Incorrect parameters channel=%d"%(channel), self.ERROR)

        return val
    
    def caSetOffset(self, channel, gain ):
        if channel<0 or channel>3:
            self.logMessage("caSetFilter::Incorrect channel %s"%(str(channel)), self.ERROR)
            return None        
        
        caAddrSet = [_CA1_DAC, _CA2_DAC, _CA3_DAC, _CA4_DAC]
        
        try:
            caAddr = caAddrSet[channel]
            dacgain = int(gain)
        except:
            self.logMessage("caSetOffset::Incorrect parameters channel=%d gain=%s"%(channel,str(gain)), self.ERROR)
            return

        # Protect SPI Read/Write
        self._semaphore.acquire(True)
        self.logMessage("caSetOffset::Set DAC gain value %s for CA%s"%(str(gain), str(channel)), self.DEBUG)
        
        #Process to generate data to send from read data
        dacgain = dacgain & 0x0FFF
        self.__spiWrite(caAddr, 1, dacgain, 0x0C, 0, 0)


        # update local variable
        self._dacgain[channel] = dacgain
        
        # Protect SPI Read/Write
        self._semaphore.release()

        
    def caGetOffset(self, channel):
        if channel<0 or channel>3:
            self.logMessage("caGetOffset::Incorrect channel %s"%(str(channel)), self.ERROR)
            return None
        
        val = None
        try:
            val = self._dacgain[channel]
            self.logMessage("caGetOffset::Get DAC gain CA%d value=%s"%(channel, val), self.DEBUG)
        except:
            self.logMessage("caGetOffset::Incorrect parameters channel=%d"%(channel), self.ERROR)

        return val

    ## feInit(channel)
    #  This function initializes the frontend board
    #  @param none 
    def feInit(self):
        
        # Protect SPI Read/Write        
        self._semaphore.acquire(True)
        self.logMessage("feInit::Init FrontEnd", self.DEBUG)

        # Step1: Dummy writtings to 0 to all PEXP 
        self.__spiWrite(_FEB_PEXP1, 1, 0x00400000, 0x18, 0, 0)
        val = self.__spiRead(_FEB_PEXP1, 1, 0x00004100, 0x10, 1, 0x08)
        self.logMessage("feInit::Value of IODIR register of FE board PE1: %d" %(val), self.DEBUG)

        self.__spiWrite(_FEB_PEXP2, 1, 0x00400000, 0x18, 0, 0)
        val = self.__spiRead(_FEB_PEXP2, 1, 0x00004100, 0x10, 1, 0x08)
        self.logMessage("feInit::Value of IODIR register of FE board PE2: %d" %(val), self.DEBUG)

        self.__spiWrite(_FEB_PEXP3, 1, 0x00400000, 0x18, 0, 0)
        val = self.__spiRead(_FEB_PEXP3, 1, 0x00004100, 0x10, 1, 0x08)
        self.logMessage("feInit::Value of IODIR register of FE board PE3: %d" %(val), self.DEBUG)
        
        self._diff_io_ports_h = 0 # I/O ports from 9 to 15 (only 9 is used)
        self._diff_io_ports_l = 0 # I/O ports from 0 to 8
        self._hs_io_ports = 0
        self._supply_ports = 0
        self._dac_gain = 0
        
        # Protect SPI Read/Write        
        self._semaphore.release()

    ## feReadTemp()
    #  This function reads the temperature of the front end board
    #  @param chennel There are four CA blocks. This parameters is used to select the CA block to read its temperature 
    def feReadTemp(self):
        # Protect SPI Read/Write                
        self._semaphore.acquire(True)
        self.logMessage("feReadTemp::Reading temp FEB", self.DEBUG)

        value = self.__spiRead(_FEB_TEMP, 0, 0, 0, 1, 0x0d)
        value = value*0.0625
        self.logMessage("feReadTemp::Temperature of Front End Board: %.4f" %(value), self.DEBUG)
        
        # Protect SPI Read/Write        
        self._semaphore.release()
        
        return value    

    def feSetGPIODirection(self, num, dir=False ):
        if num<=0 or num>_N_DIFF_IO_PORTS:
            self.logMessage("feGPIODirection::Incorrect port number %s, expected value between 1 and %d"%(str(num),_N_DIFF_IO_PORTS), self.ERROR)
            return
        
        # Protect SPI Read/Write        
        self._semaphore.acquire(True)
        self.logMessage("feGPIODirection::Set direction for Input %s to %s"%(str(num),str(dir)), self.DEBUG)

        # dir value = 0 means port is set as Input.
        # dir value = 1 means port is set as Output
        val = 1 if dir == 0 else 0
        
        # GPIO number 9 is in PEXP1, the rest are in PEXP2
        if num == 9: 
            #Process to generate data to send from read data
            addr = _FEB_PEXP1
            bit_pos = 0
        else:
            addr = _FEB_PEXP2
            bit_pos = num-1

        rdval = self.__spiRead(addr, 1, 0x00004109, 0x10, 1, 0x08)
        rdval = rdval & (0xFF - (0x01<<bit_pos))
        rdval = rdval | (val<<bit_pos)
        rdval = rdval | 0x00400900        #necessary bits (opcode and address) are added for proper communication
        self.__spiWrite(addr, 1, rdval, 0x18, 0, 0)
        
        self.logMessage("feGPIODirection::Set address %s value %s (%s)"%(hex(addr),str(val),hex(val)), self.DEBUG)

        # Protect SPI Read/Write        
        self._semaphore.release()

    def feGetGPIODirection(self, num):
        if num<=0 or num>_N_DIFF_IO_PORTS:
            self.logMessage("feGetGPIODirection::Incorrect port number %s, expected value between 1 and %d"%(str(num),_N_DIFF_IO_PORTS), self.ERROR)
            return

        self._semaphore.acquire(True)
        self.logMessage("feGetGPIODirection::Returns direction for Input %s"%(str(num)), self.DEBUG)
        
        # GPIO number 9 is in PEXP1, the rest are in PEXP2
        if num == 9: 
            #Process to generate data to send from read data
            addr = _FEB_PEXP1
            bit_pos = 0
        else:
            addr = _FEB_PEXP2
            bit_pos = num-1

        rdval = self.__spiRead(addr, 1, 0x00004109, 0x10, 1, 0x08)
        rdval = (rdval >> bit_pos) & 0x01
        
        self.logMessage("feGetGPIODirection:: GPIO %s set to %s"%(str(num),str(rdval)), self.DEBUG)
        
        # Protect SPI Read/Write        
        self._semaphore.release()

        return rdval


    def feSetDIODirection(self, num, dir=False ):
        if num<=0 or num>_N_HS_IO_PORTS:
            self.logMessage("feDIODirection::Incorrect port number %s, expected value between 1 and %d"%(str(num),_N_HS_IO_PORTS), self.ERROR)
            return

        # Protect SPI Read/Write        
        self._semaphore.acquire(True)
        self.logMessage("feDIODirection::Set direction for Input %s to %s"%(str(num),str(dir)), self.DEBUG)
        
        # dir value = 0 means port is set as Input.
        # dir value = 1 means port is set as Output
        val = 1 if dir == 0 else 0
        
        addr = _FEB_PEXP3
        bit_pos = num-1

        rdval = self.__spiRead(addr, 1, 0x00004109, 0x10, 1, 0x08)
        rdval = rdval & (0xFF - (0x01<<bit_pos))
        rdval = rdval | (val<<bit_pos)
        rdval = rdval | 0x00400900        #necessary bits (opcode and address) are added for proper communication
        self.__spiWrite(addr, 1, rdval, 0x18, 0, 0)
        
        self.logMessage("feDIODirection::Set address %s value %s (%s)"%(hex(addr),str(val),hex(rdval)), self.DEBUG)

        # Protect SPI Read/Write        
        self._semaphore.release()
        
    def feGetDIODirection(self, num):
        if num<=0 or num>_N_HS_IO_PORTS:
            self.logMessage("feGetDIODirection::Incorrect port number %s, expected value between 1 and %d"%(str(num),_N_HS_IO_PORTS), self.ERROR)
            return

        # Protect SPI Read/Write        
        self._semaphore.acquire(True)
        self.logMessage("feGetDIODirection::Returns direction for Input %s"%(str(num)), self.DEBUG)
        
        addr = _FEB_PEXP3
        bit_pos = num-1

        rdval = self.__spiRead(addr, 1, 0x00004109, 0x10, 1, 0x08)
        rdval = (rdval >> bit_pos) & 0x01
        
        self.logMessage("feGetDIODirection:: GPIO %s set to %s"%(str(num),str(rdval)), self.DEBUG)
        
        # Protect SPI Read/Write        
        self._semaphore.release()

        return rdval

    def feSetSupplyPort(self, num, dir=False ):
        if num<=0 or num>_N_SUPPLY_PORTS:
            self.logMessage("feSetSupplyPort::Incorrect port number %s, expected value between 1 and %d"%(str(num),_N_SUPPLY_PORTS), self.ERROR)
            return

        # Protect SPI Read/Write        
        self._semaphore.acquire(True)
        self.logMessage("feSetSupplyPort::Set direction for Input %s to %s"%(str(num),str(dir)), self.DEBUG)
        
        val = 1 if dir else 0
        
        addr = _FEB_PEXP1
        bit_pos = num

        rdval = self.__spiRead(addr, 1, 0x00004109, 0x10, 1, 0x08)
        rdval = rdval & (0xFF - (0x01<<bit_pos))
        rdval = rdval | (val<<bit_pos)
        rdval = rdval | 0x00400900        #necessary bits (opcode and address) are added for proper communication
        self.__spiWrite(addr, 1, rdval, 0x18, 0, 0)
        
        self.logMessage("feSetSupplyPort::Set address %s value %s"%(hex(addr),hex(rdval)), self.DEBUG)

        # Protect SPI Read/Write        
        self._semaphore.release()        
        
    def feGetSupplyPort(self, num):
        if num<=0 or num>_N_SUPPLY_PORTS:
            self.logMessage("feGetSupplyPort::Incorrect port number %s, expected value between 1 and %d"%(str(num),_N_SUPPLY_PORTS), self.ERROR)
            return

        # Protect SPI Read/Write        
        self._semaphore.acquire(True)
        self.logMessage("feGetSupplyPort::Returns direction for Input %s"%(str(num)), self.DEBUG)
        
        addr = _FEB_PEXP1
        bit_pos = num

        rdval = self.__spiRead(addr, 1, 0x00004109, 0x10, 1, 0x08)
        rdval = (rdval >> bit_pos) & 0x01
        
        self.logMessage("feGetSupplyPort:: GPIO %s set to %s"%(str(num),str(rdval)), self.DEBUG)
        
        # Protect SPI Read/Write        
        self._semaphore.release()

        return rdval

    def feSetDACGain(self, gain ):
        if gain>1:
            self.logMessage("feSetDACGain::Incorrect gain value", self.ERROR)
            return

        # Protect SPI Read/Write        
        self._semaphore.acquire(True)
        self.logMessage("feSetDACGain::Set GAIN Dac to %s"%(str(gain)), self.DEBUG)
        
        addr = _FEB_PEXP3
        bit_pos = 0x07

        rdval = self.__spiRead(addr, 1, 0x00004109, 0x10, 1, 0x08)
        rdval = rdval & (0xFF - (0x01<<bit_pos))
        rdval = rdval | (gain<<bit_pos)
        rdval = rdval | 0x00400900        #necessary bits (opcode and address) are added for proper communication
        self.__spiWrite(addr, 1, rdval, 0x18, 0, 0)
        
        if gain:
            msg = "Output: 0 - 5V"
        else:
            msg = "Output: 0 - 2.5V"
        self.logMessage("feSetDACGain::Gain set to %s"%(msg), self.DEBUG)

        # Protect SPI Read/Write        
        self._semaphore.release()
        
    def feGetDACGain(self):
        # Protect SPI Read/Write        
        self._semaphore.acquire(True)
        self.logMessage("feGetDACGain:: Read Gain DAC", self.DEBUG)
        
        addr = _FEB_PEXP3
        bit_pos = 0x07

        rdval = self.__spiRead(addr, 1, 0x00004109, 0x10, 1, 0x08)
        rdval = (rdval >> bit_pos) & 0x01
        
        if rdval:
            msg = "Output: 0 - 5V"
        else:
            msg = "Output: 0 - 2.5V"

        self.logMessage("feGetDACGain::Gain set to %s"%(msg), self.DEBUG)
        
        # Protect SPI Read/Write        
        self._semaphore.release()

        return rdval

    def eempromRead(self, name, start_add=0, num_bytes=0):
        ret_value = []
        if name.upper() in self._eeprom_dict.keys() and num_bytes > 0:
            # Protect SPI Read/Write        
            self._semaphore.acquire(True)
            
            self.logMessage("eempromRead:: Read eeprom %s"%name.upper(), self.DEBUG)
            
            eemprom_add = self._eeprom_dict[name.upper()]
            
            for el in range(0,num_bytes):
                addr = 0x00000300 | ((start_add + el) & 0x000000ff)
                
                rdval = self.__spiRead(eemprom_add, 1, addr, 0x10, 1, 0x08)
                rdval = rdval & 0xFF
            
                ret_value.append(rdval)
            
            self.logMessage("eempromRead:: %s Read data=[%s]"%(name.upper(),', '.join(map(hex, ret_value))), self.DEBUG)
            # Protect SPI Read/Write        
            self._semaphore.release()
        else:
            self.logMessage("eempromRead::Invalid eeprom data", self.ERROR)
        return ret_value

    def eempromWrite(self, name, start_add=0, data=[]):
        if name.upper() in self._eeprom_dict.keys() and len(data) > 0:
            # Protect SPI Read/Write        
            self._semaphore.acquire(True)
            
            self.logMessage("eempromRead:: Write eeprom %s"%name.upper(), self.DEBUG)
            
            eemprom_add = self._eeprom_dict[name.upper()]
            
            for el in range(0,len(data)):
                try:
                    wdata = data[el]
                except:
                    break
                
                # Write first the WREN command
                self.__spiWrite(eemprom_add, 1, 0x00000006, 0x08, 0, 0)
                
                # Write address and data
                add = 0x00020000 | (((start_add + el) & 0x0FF) << 8)
                add = add | (wdata & 0x0FF)
                
                self.__spiWrite(eemprom_add, 1, add, 0x18, 0, 0)
                
            self.logMessage("eempromWrite:: %s Write data=[%s]"%(name.upper(),', '.join(map(hex, data))), self.DEBUG)
            # Protect SPI Read/Write        
            self._semaphore.release()
        else:
            self.logMessage("eempromRead::Invalid eeprom data", self.ERROR)



    ## __spiRead(attrName)
    #  Private function used to control the SPI Driver read protocol
    #  @param attrName String containing the attribute name to write
    #  @return Numeric value for te selected attribute    
    def __spiRead(self, spiDev, tx, tx_data, tx_data_lenght, rx, rx_data_lenght ):
        self.logMessage("__spiRead:: Chip select:%s tx=%s tx_data=%s tx_data_lenght=%s--> rx=%s rx_data_lenght=%s"%(hex(spiDev), hex(tx), hex(tx_data), hex(tx_data_lenght), hex(rx), hex(rx_data_lenght)), self.DEBUG)
        try:
            ready = self.readAttribute('stat_ready')
            while not ready:
                ready = self.readAttribute('stat_ready')
            
            self.writeAttribute('ctl_tx',tx)
            self.writeAttribute('ctl_tx_data', tx_data)
            self.writeAttribute('ctl_tx_data_length', tx_data_lenght)
            
            self.writeAttribute('ctl_rx',rx)
            self.writeAttribute('ctl_rx_data_length',rx_data_lenght)
            
            self.writeAttribute('ctl_spi_addr',spiDev)
            
            self.writeAttribute('ctl_start',0x01)
            value = self.readAttribute('ctl_rx_data')
            
            self.logMessage("__spiRead:: rx_data=%s"%(hex(value)), self.DEBUG)
            
        except Exception, e:
            self.logMessage("__spiRead::Problem reading to the SPI!!! Exception: %s"%(str(e)), self.ERROR)
            value = None
        return value
    
    
    ## __spiWrite(attrName)
    #  Private function used to control the SPI Driver read protocol
    #  @param attrName String containing the attribute name to write
    #  @return Numeric value for te selected attribute    
    def __spiWrite(self, spiDev, tx, tx_data, tx_data_lenght, rx, rx_data_lenght ):
        self.logMessage("__spiWrite:: Chip select:%s tx=%s tx_data=%s tx_data_lenght=%s--> rx=%s rx_data_lenght=%s"%(hex(spiDev), hex(tx), hex(tx_data), hex(tx_data_lenght), hex(rx), hex(rx_data_lenght)), self.DEBUG)
        try:
            ready = self.readAttribute('stat_ready')
            while not ready:
                ready = self.readAttribute('stat_ready')
            
            self.writeAttribute('ctl_tx',tx)
            self.writeAttribute('ctl_tx_data', tx_data)
            self.writeAttribute('ctl_tx_data_length', tx_data_lenght)
            
            self.writeAttribute('ctl_rx',rx)
            self.writeAttribute('ctl_rx_data_length',rx_data_lenght)
            
            self.writeAttribute('ctl_spi_addr',spiDev)
            
            self.writeAttribute('ctl_start',0x01)

            self.logMessage("__spiWrite:: write successfull!!", self.DEBUG)
        except Exception,  e:
            self.logMessage("__spiWrite::Problem writing to the SPI!!! Exception: %s"%(str(e)), self.ERROR)

