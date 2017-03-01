## @package memory.py 
#    File containing the device class, to control the ADC
#
#    Author = "Manuel Broseta"
#    Copyright = "Copyright 2016, ALBA"
#    Version = "1.0"
#    Email = "mbroseta@cells.es"
#    Status = "Development"
#    History:
#   27/01/2016 - file created by Manuel Broseta

__author__ = "Manuel Broseta"
__copyright__ = "Copyright 2016, ALBA"
__license__ = "GPLv3 or later"
__version__ = "1.0"
__email__ = "mbroseta@cells.es"
__status__ = "Development"


from alin.base import AlinDevice
from alin.base import getConfigData
import os
import threading
import time

import csv

_CONFIG_MASK = "MEMORY_"

_DEFAULT_BUFFER_SIZE = 4000

class Memory(AlinDevice):
    def __init__(self, dev='WB-HRMY-MEMORY', debug=False):
        AlinDevice.__init__(self, device=dev, debug=debug, logger='FPGAMEM')

        # Get default configuration from config file
        self._debug = debug
        self._device = dev
        self.configure()
        
        self._memmng_thread = None
        
        self.logMessage("__init__() Initialized ", self.DEBUG)
            

    def configure(self):
        # Get default configuration from config file
        configDict = getConfigData(_CONFIG_MASK)
        self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else self._debug
        self._debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 40
        self._device = configDict["DEVICE_"] if "DEVICE_" in configDict.keys() else self._device
        self._buffer_size = int(configDict["BUFFERSIZE_"]) if "BUFFERSIZE_" in configDict.keys() else _DEFAULT_BUFFER_SIZE        

        self.setDevice(devname=self._device)
        
        # Logging
        self.logLevel(self._debuglevel)
        self.logEnable(self._debug)
        
        self.logMessage("configure() %s configured"%_CONFIG_MASK, self.INFO)                

    def init(self):
        #Configuration of memory block
        self.logMessage("start(): Configuration of memory block", self.INFO)

        try:
            # Resets data in Memory
            self.writeAttribute('ctl_RST',1)
            # Save all the data after the trigger(0).
            self.writeAttribute('ctl_OnTrigger',0)
            #  When this bit is chnged from 0 to 1 all memory is deleted.
            self.writeAttribute('ctl_save',0)
            # When this Data ID is received Trigger is generated.
            self.writeAttribute('ctl_TRIGID',0x01)
            # Mask of ID, only the bits set at 1 will be checked to identify the data to save.
            # DATAID & IDMASK == ID & IDMASK
            self.writeAttribute('ctl_IDMask',0)
            self.writeAttribute('ctl_RST',0)
            
            self._memmng_thread = None
            self._memmng_thread = MemoryMangementThread(self, debug=self._debug)
            self._memmng_thread.setDaemon(True)
            
            self._memmng_thread.start()
            self.logMessage("start() Memory Management thread started",self.DEBUG)

        except Exception, e:
            self.logMessage("start() Not possible due to: %s"%str(e),self.ERROR)
            
    def stop(self):
        self.logMessage("stop() Stopping Management thread....",self.DEBUG)
        if self._memmng_thread is not None:
            self._memmng_thread.end()
        
        while not self._memmng_thread.getProcessEnded():
            self.logMessage("stop(): Waiting process to die", self.DEBUG)
            time.sleep(0.5)
            pass  
        
        self.logMessage("stop() Memory Management Thread stopped", self.DEBUG)
            
        
    def getMemoryLenData(self):
        #self.logMessage("getMemoryLenData(): Configuration of memory block", self.DEBUG)
        retval = None
        try:
            retval = self.readAttribute('Len_nDATA')
            self.logMessage("getMemoryLenData(): len data = %s"%str(retval), self.DEBUG)
        except Exception, e:
            self.logMessage("getMemoryLenData() Not possible due to: %s"%str(e),self.ERROR)
            
        return retval
    
    def getMemoryOverflow(self):
        retval = None
        try:
            retval = bool(self.readAttribute('CTL_MOF'))
        except Exception, e:
            self.logMessage("getMemoryOverflow() Not possible due to: %s"%str(e),self.ERROR)
        return retval    
    
    def getMemoryLastData(self, ndata=0):
        self.logMessage("getMemoryLastData(): Returns the last %d values in memory"%ndata, self.DEBUG)
        
        retval = []
        if ndata != 0:
            try:
                for i in range(0, ndata):
                    if self.readAttribute('Len_nDATA') != 0:
                        data = {}
                        data['id'] = self.readAttribute('v_id')
                        data['timestamp'] = self.readAttribute('v_T_stamp')
                        data['data'] = self.readAttribute('v_data')
                        retval.append(data)                        
                    else:
                        self.logMessage("getMemoryLenData() Buffer empty",self.DEBUG)
                        break
            except Exception, e:
                self.logMessage("getMemoryLenData() Not possible due to: %s"%str(e),self.ERROR)
        
        #print retval
        return retval
        
    def getMemoryBuffer(self):
        self.logMessage("getMemoryBuffer(): getting buffer",self.DEBUG)
        ret_val = []
        if self._memmng_thread is not None:
            ret_val = self._memmng_thread.getBuffer()
            self._memmng_thread.clearBuffer()
            
        return ret_val
        
    def clearMemoryBuffer(self):
        self.logMessage("clearMemoryBuffer(): clearing buffer",self.DEBUG)
        if self._memmng_thread is not None:
            self._memmng_thread.clearBuffer()
            
    def writeRegister(self, register, value):
        self.logMessage("writeRegister(): Register %s value=%s"%(str(register),str(value)),self.DEBUG)
        self.writeAttribute(register,value)
    
    def readRegister(self, register):
        value = self.readAttribute(register)
        self.logMessage("readRegister(): Register %s read value=%s"%(str(register),str(value)),self.DEBUG)
        return value        
    
        
class MemoryMangementThread(threading.Thread):
    def __init__(self, parent=None, debug=None):
        threading.Thread.__init__(self)
        self._parent = parent
        
        self._endProcess = False
        self._processEnded = False
        
        self._acqdata_semaphore = False
        
        self._thr_databuffer = []
        
    def end(self):
        self._parent.logMessage("stopMemoryManagement() Stopping Acquisition thread....",self._parent.INFO)
        self._endProcess = True
        
    def getProcessEnded(self):
        return self._processEnded
    
    def getBuffer(self):
        tmp = []
        self.setAcqSemaphore(True)
        tmp = self._thr_databuffer
        self._thr_databuffer = []
        self.setAcqSemaphore(False)
        return  tmp
    
    def clearBuffer(self):
        self.setAcqSemaphore(True)        
        self._thr_databuffer = []
        self.setAcqSemaphore(False)        
        
    def setAcqSemaphore(self, value):
        self._acqdata_semaphore = value
            
    def run(self): 
        mem_of = False
        total_data = 0
        start_time = time.time()
        counter = 0
        while not (self._endProcess):
            len_mem_data = self._parent.readAttribute('LEN_NDATA')
            if len_mem_data != 0 and len_mem_data is not None:
                # Sets semaphore to acquiring data
                if mem_of:
                    mem_of = False
                    self._parent.logMessage("MemoryMangementThread() Overflow reset",self._parent.INFO)
                    total_data = 0        
                    start_time = time.time()

                if self._acqdata_semaphore == False:
                    read_ids = []
                    for x in range (0, len_mem_data):
                        total_data += 1
                        
                        rd_id = self._parent.readAttribute('V_ID')
                        rd_ts = self._parent.readAttribute('V_T_STAMP')
                        rd_data = self._parent.readAttribute('V_DATA')
                        
                        if rd_id not in read_ids:
                            read_ids.append(rd_id)
                        
                        #maxlenght = self._thr_databuffer_maxlenght[rd_id] 
                        #if maxlenght is not None and len(self._thr_databuffer[rd_id])<maxlenght:
                        self._thr_databuffer.append([rd_id, rd_ts, rd_data])
                        self._parent.logMessage("MemoryMangementThread() Data acquired ID=%s TS=%s Value=%s"%(hex(rd_id),hex(rd_ts),hex(rd_data)),self._parent.INFO)
                    
                    self._parent.logMessage("MemoryMangementThread() %s data acquired with IDs: %s"%(len(self._thr_databuffer),', '.join(map(hex, read_ids))),self._parent.INFO)
            else:
                ovf = self._parent.readAttribute('CTL_MOF')
                if ovf and not mem_of:
                    mem_of =True
                    acq_time = time.time() - start_time
                    self._parent.logMessage("MemoryMangementThread() Memory Overflow detected!! Waiting to empty buffer.....",self._parent.INFO)
                    self._parent.logMessage("MemoryMangementThread() Total data get in %s secs, since last OVF = %s"%(str(acq_time),str(total_data)),self._parent.INFO)
                  

        self._processEnded = True        

