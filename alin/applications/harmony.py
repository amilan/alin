## @package alinspinctrl.py 
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
from alin.base import AlinLog
from alin.base import getConfigData

from alin.drivers.adccore import AdcCore
from alin.drivers.average import Average
from alin.drivers.dac import Dac
from alin.drivers.digitalio import DigitalIO
from alin.drivers.fpga import FPGA
from alin.drivers.fifo import Fifo
from alin.drivers.idgen import IDGen
from alin.drivers.memory import Memory
from alin.drivers.spi import Spi 

from datetime import datetime

import math
import os
from random import uniform
import signal
import threading
import time

_CONFIG_MASK = "HARMONY_"

_STATES = {"STATE_INIT":0,
           "STATE_ON": 1,
           "STATE_RUNNING":2,
           "STATE_ACQUIRING":3,
           "STATE_FAULT":4,
           }

_FILTER = ['3200hz', '100hz', '10hz', '1hz', '0.5hz']
_TRIGGERMODE = ['SOFTWARE','HARDWARE','AUTOTRIGGER']
_RANGE = ['1ma', '100ua', '10ua', '1ua', '100na', '10na', '1na', '100pa']
_POLARITY = ['FALLING','RISING']
_TRIGINPUTS = ['DIO_1','DIO_2','DIO_3','DIO_4','DIFF_IO_1','DIFF_IO_2','DIFF_IO_3','DIFF_IO_4','DIFF_IO_5','DIFF_IO_6','DIFF_IO_7','DIFF_IO_8','DIFF_IO_9']
_GPIO_TYPE = ['OUTPUT','INPUT']

_ACQ_TYPES = ['TIME_INSIDE_FIFO_RANGE', 'TIME_ABOVE_FIFO_RANGE',]

_CHANNELS = [ 1, 2, 3, 4]

_5V_RANGE_VALUE = 5
_10V_RANGE_VALUE = 10

_ADC_CH_ID_1 = 0x1
_ADC_CH_ID_2 = 0x2
_ADC_CH_ID_3 = 0x3
_ADC_CH_ID_4 = 0x4

_FIFO_ID_1 = 0x11
_FIFO_ID_2 = 0x12
_FIFO_ID_3 = 0x13
_FIFO_ID_4 = 0x14

_AVG_ID_1 = 0x21
_AVG_ID_2 = 0x22
_AVG_ID_3 = 0x23
_AVG_ID_4 = 0x24

_CNT0_ID = 0x30
_CNT1_ID = 0x31

_TEMPORAL_ID = 0xE0
_IDGEN_ID = 0xF0


_AUTO_RANGE_LOWER_LIM = 5
_AUTO_RANGE_HIGHER_LIM = 90

_AUTO_RANGE_PERIOD = 0.5

def handleError(f):
    def handleProblems(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception, e:
            print str(e)
            return None
    return handleProblems

class caRangeAutoThread(threading.Thread):
    def __init__(self, parent=None, channel=None):
        threading.Thread.__init__(self)
        0x31
        self._parent = parent
        
        self._dSPI = parent._dSPI
        self.setSaturationLimits(_AUTO_RANGE_HIGHER_LIM,_AUTO_RANGE_LOWER_LIM)
        
        self._channel = channel
        self._rangeidx = 0
        
        self.th_endProcess = False
        self.th_processEnded = False
        
    def end(self):
        self._parent.logMessage("caRangeAutoThread() Stopping Range Auto thread channel %s...."%str(self._channel),self._parent.INFO)
        self.th_endProcess = True
        
    def getProcessEnded(self):
        return self.th_processEnded
    
    def setInitialRange(self, rang="1ma"):
        try:
            self._rangeidx = _RANGE.index(rang.lower())
        except:
            self._rangeidx = 0
            
    def setSaturationLimits(self, max=0, min=0):
        try:
            self._higherlim = max
        except:
            self._higherlim = _AUTO_RANGE_HIGHER_LIM
        try:
            self._lowerlim = min
        except:
            self._lowerlim = _AUTO_RANGE_LOWER_LIM
            
    def run(self):
        while not (self.th_endProcess):
            insvolt = self._parent.getInstantVoltage(self._channel-1)
            
            percentage_insvolt = (abs(insvolt)*100)/10.
            curr_idx = self._rangeidx
            
            if percentage_insvolt > self._higherlim:
                # Increase Range
                if curr_idx > 0:
                    curr_idx = curr_idx - 1
            elif percentage_insvolt < self._lowerlim:
                # Decrease Range
                if curr_idx < (len(_RANGE)-1):
                    curr_idx = curr_idx + 1
            else:
                # Do not anything
                pass

            if curr_idx != self._rangeidx:
                self._rangeidx = curr_idx
                param = _RANGE[self._rangeidx]
                self._parent.logMessage("caRangeAutoThread() Change range in channel %s to %s"%(str(self._channel),param),self._parent.INFO)                    
                self._dSPI.caSetRange(self._channel-1, param)
            
            time.sleep(_AUTO_RANGE_PERIOD)
        self.th_processEnded = True

class AcquisitionThread(threading.Thread):
    def __init__(self, parent=None, debug=None):
        threading.Thread.__init__(self)
        self._parent = parent
        
        self._dMEMORY = parent._dMEM
        self._dADCCORE = parent._dADCCORE
        
        self._trig_mode = parent._trigmode
        self._trig_input = _TRIGINPUTS.index(parent._triginput)
        self._sw_trig_flag = False
        self._trig_flag = None
        
        self._endProcess = False
        self._processEnded = False
        
        self._acquiring_flag = False
        self._saving_data_enabled = False
        self._num_triggers = None
        self._parent._validtriggers = 0
        self._acq_auto_stop = False
        self._acq_ready = False
        
        
        self._time_start = datetime.utcnow()
        
        self._acq_ch_completed = [False]*len(_CHANNELS)
        
        self.clearTemporalBuffers()

    def end(self):
        self._parent.logMessage("AcquisitionThread() Stopping Acquisition thread....",self._parent.INFO)
        self._endProcess = True
        
    def getProcessEnded(self):
        return self._processEnded

    def saveDataEnable(self, value=False):
        self._saving_data_enabled = value
    
    def clearTemporalBuffers(self):
        self._temporal_readdata = [[] for x in range(0,4)]
        self._temporal_counter = 1
        self._partial_data_acquired = False
        self._acq_ch_completed = [False]*len(_CHANNELS)
           
    def calculateAVG(self, channel):
        calculated_avg = 0
        for el in self._temporal_readdata[channel]:
            calculated_avg += el[1]
        calculated_avg = calculated_avg/len(self._temporal_readdata[channel])

        return calculated_avg
    
    def setNumTriggers(self, value=None):
        if value is not None and value >=1 and value != "":
            self._num_triggers = value
            self._acq_auto_stop = True
        else:
            self._num_triggers = 0
            self._acq_auto_stop = False
        self._acq_ready = True
        self._parent.logMessage("AcquisitionThread(): Number of Triggers = %s"%str(self._num_triggers),self._parent.INFO)            

    def setAcquiringFlag(self, value):
        self._acquiring_flag = value
        if value:
            self._parent.setState('STATE_ACQUIRING')
            self._acq_ch_completed = [False]*len(_CHANNELS)
            self._sw_trig_flag = True
            self._parent.logMessage("AcquisitionThread() acquisition channels reset",self._parent.INFO)            
        else:
            text = '[%s]' % ', '.join(map(str, self._acq_ch_completed))
            self._parent.logMessage("AcquisitionThread() acquisition channels completed %s"%text,self._parent.INFO)
            if self._acq_ch_completed.count(False) == 0:
                self._parent.setState('STATE_RUNNING')
                self._parent._validtriggers = self._parent._validtriggers + 1
                if self._acq_auto_stop:
                    try:
                        self._num_triggers = self._num_triggers - 1
                        self._parent.logMessage("AcquisitionThread(): Number of Triggers pending = %s"%str(self._num_triggers),self._parent.INFO)
                        if self._num_triggers <= 0:
                            self._num_triggers = None
                            self._parent.stopAcq("STOP_FROM_THREAD")
                            self.end()
                    except:
                        self._num_triggers = None
                        self._parent.stopAcq("STOP_FROM_THREAD")
                        self.end()
                else:
                    self._num_triggers = self._num_triggers + 1
        
    def getAcquiringFlag(self):        
        return self._acquiring_flag
    
    def calculateCurrent(self, value):
        if value>0x7fffffff:
            value-=0x100000000
        aux_value = value/float(self._parent.fifosize)/2.;
        return self._dADCCORE.convertADCToVoltage(aux_value)
    
    def saveTrigger(self, timestamp, state=False):
        if state:
            trig_state = state;
        else:
            if self._trig_mode in ['SOFTWARE','AUTOTRIGGER']:
                trig_state = self._sw_trig_flag
            else:
                try:
                    trig_state = self._parent.getGPIOValue(self._trig_input+1)
                except:
                    self._parent.logMessage("AcquisitionThread(): Not possible to read trigger state input=%s"%str(self._trig_input), self._parent.ERROR)
                
        if self._trig_flag != trig_state:
            if self._trig_flag is not None:
                self._parent._trigger_data.append([timestamp,int(self._trig_flag)])
                self._trig_flag = trig_state
                self._parent._trigger_data.append([timestamp,int(self._trig_flag)])
            else:
                self._trig_flag = trig_state
                self._parent._trigger_data.append([timestamp,int(self._trig_flag)])
        self._sw_trig_flag = False
        
    
    def run(self): 
        _id_to_buffer = {_AVG_ID_1: 0, 
                         _AVG_ID_2: 1,
                         _AVG_ID_3: 2,
                         _AVG_ID_4: 3,
                        }

        while not (self._endProcess):
            # Temporal until TS will be implemented
            current_time = datetime.utcnow()
            diff = current_time - self._time_start
            data_ts = (diff.days * 24 * 60 * 60 + diff.seconds) + diff.microseconds * 1.0e-6
            
            data = self._dMEMORY.getMemoryBuffer()
            if len(data) > 0:
                acq_type = self._parent._acq_type
                acq_partial_counts = self._parent._acqtime_counts
                read_ids = [a[0] for a in data]
                msg = "AcquisitionThread(): Acquiring... "
                msg += " CH1(%s)"%str(read_ids.count(_AVG_ID_1))
                msg += " CH2(%s)"%str(read_ids.count(_AVG_ID_2))
                msg += " CH3(%s)"%str(read_ids.count(_AVG_ID_3))
                msg += " CH4(%s)"%str(read_ids.count(_AVG_ID_4))
                msg += " IDGEN(%s)"%str(read_ids.count(_IDGEN_ID))
                msg += " CNT1(%s)"%str(read_ids.count(_CNT1_ID))
                msg += " TotalAcq=%s"%str(len(data))
                self._parent.logMessage(msg, self._parent.INFO)

                if self._acq_ready:
                    for el in data:
                        data_id = el[0]
                        # Temporally commented until TS will be implemented
                        #data_ts = el[1]
                        data_val = el[2]
                    
                        if acq_type == 'TIME_ABOVE_FIFO_RANGE':
                            if data_id in _id_to_buffer.keys():
                                channel = _id_to_buffer[data_id]
                                data_val = self._parent.convertVoltToCurr(channel, self.calculateCurrent(data_val))

                                self._temporal_readdata[_id_to_buffer[data_id]].append([data_ts,data_val])
                            
                                tmp_buff_len = len(self._temporal_readdata[channel])
                                if  tmp_buff_len == acq_partial_counts:
                                    avg_data = self.calculateAVG(channel)
                                
                                    self._parent._ch_readdata[channel].append([data_ts,avg_data])
                                    self._acq_ch_completed[channel] = True
                                    self._parent.logMessage("AcquisitionThread(): Acquisition COMPLETED CH%s  Counts=%s Value=%s"%(str(channel+1),str(tmp_buff_len),str(avg_data)), self._parent.INFO)
                                 
                                    self.setAcquiringFlag(False)
                            else:
                                self._parent._general_buffer.append([data_id, data_ts,data_val])
                            
                                if data_id == _IDGEN_ID:
                                    self.clearTemporalBuffers()
                                    self.setAcquiringFlag(True)
                                    self.saveTrigger(data_ts, state=True)
                                if data_id == _CNT1_ID:
                                    self._temporal_counter += 1
                                    if self._temporal_counter > acq_partial_counts:
                                        if not self._partial_data_acquired:
                                            self._parent.partialAcquisitionReset()
                                        self._partial_data_acquired = True
                        else:
                            if data_id == _IDGEN_ID:
                               self.setAcquiringFlag(True)
                               self.saveTrigger(data_ts,state=True)
                            if data_id in _id_to_buffer.keys():
                                channel = _id_to_buffer[data_id]
                                data_val = self._parent.convertVoltToCurr(channel, self.calculateCurrent(data_val))

                                self._parent._ch_readdata[channel].append([data_ts,data_val])
                                self._acq_ch_completed[channel] = True
                                self._parent.logMessage("AcquisitionThread(): Acquisition COMPLETED CH%s Value=%s"%(str(channel+1),data_val), self._parent.INFO)
                            
                                self.setAcquiringFlag(False)
                            else:
                                self._parent._general_buffer.append([data_id, data_ts,data_val])
            
            # Check trigger input
            self.saveTrigger(data_ts)
            
            time.sleep(0.1)

        self._processEnded = True


class Harmony(AlinLog):
    def __init__(self, debug=False):
        AlinLog.__init__(self, debug=False, loggerName='HARMONY')
        
        # Get default configuration from config file
        self._debug = debug
        self.configure()

        self._dFPGA = FPGA()
        # Temporal. To Be Deleted when read command withparams will be supported in the SCPI
        self.device = None
        self.num = None
        self.attribute = None
        
        self._dSPI = Spi()        
        self._dMEM = Memory()
        self._dIDGEN = IDGen()
        self._dADCCORE = AdcCore()
        self._dDAC = Dac()
        self._dFIFO_1 = Fifo(number=0)
        self._dFIFO_2 = Fifo(number=1)
        self._dFIFO_3 = Fifo(number=2)
        self._dFIFO_4 = Fifo(number=3)

        self._dAVERAGE_1 = Average(number=0)
        self._dAVERAGE_2 = Average(number=1)
        self._dAVERAGE_3 = Average(number=2)
        self._dAVERAGE_4 = Average(number=3)
        self._dDIGITALIO = DigitalIO()
        
        # applications
        self._MEMMW = None

        # Buffers for ADC channel readings
        self._acq_thread = None
        self.clearDataBuffers()
        
        # Electrometer attributes '0' disable. 
        self._range = None
        self._filter = None
        self._trigmode = None
        self._trigpol = None
        self._acqtime = None
        self._acqlowtime = None
        self._acqtime_counts = None
        self._acqntriggers = None
        self._validtriggers = None
        self._trigdelay = None
        self._triginput = None
        
        self._acq_type = None
        
        self._max_fifosizes = [0 for i in range(0,4)]
        
        self._caRange_autoTh = [None for i in range(0,4)]
        self._caRange_satlimits = [[_AUTO_RANGE_HIGHER_LIM,_AUTO_RANGE_LOWER_LIM] for i in range(0,4)]
        
        # State control 
        self._state = None
        self.setState("STATE_INIT")
        
        self.logMessage("__init__() Initialized ", self.INFO)
        
    def configure(self):
        # Get default configuration from config file
        configDict = getConfigData(_CONFIG_MASK)
        self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else self._debug
        self._debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 40
        
        # Logging
        self.logLevel(self._debuglevel)
        self.logEnable(self._debug)
        
        self.logMessage("configure() %s configured"%_CONFIG_MASK, self.INFO)

    def reconfigure(self):
        self.logMessage("reconfigure(): reconfiguring applications and associted devices", self.INFO)
                
        # reconfigure applications
        self.configure()
        
        # reconfigure devices
        self._dSPI.configure()        
        self._dMEM.configure()
        self._dIDGEN.configure()
        self._dADCCORE.configure()
        self._dDAC.configure()
        self._dFIFO_1.configure()
        self._dFIFO_2.configure()
        self._dFIFO_3.configure() 
        self._dFIFO_4.configure()
        self._dAVERAGE_1.configure()
        self._dAVERAGE_2.configure()
        self._dAVERAGE_3.configure()
        self._dAVERAGE_4.configure()
        self._dDIGITALIO.configure()
        self._dFPGA.configure()
        
        self.logMessage("reconfigure(): Done!!", self.INFO)
        300
    def setState(self, state):
        if state in _STATES.keys():
            self._state = state
        else:
            self.logMessage("setState(): Invalid State %d"%str(state), self.ERROR)
            
    def getState(self):
        return self._state
    
    def isAcquiring(self):
        st = self.getState()
        if st == "STATE_RUNNING" or st == "STATE_ACQUIRING":
            return True
        else:
            return False

    def clearDataBuffers(self):
        self._ch_readdata = [[] for x in range(0,4)]
        self._general_buffer = []
        self._trigger_data = []
        
        if self._acq_thread is not None:
            self._acq_thread.setNumTriggers(self._acqntriggers)

        self.logMessage("clearDataBuffers()", self.INFO)

    def partialAcquisitionReset(self):
        self._dDIGITALIO.writeAttribute('DIS_STP_DIS1_M', 0x03)
        self._dDIGITALIO.writeAttribute('DIS_STP_WD1', 0x01)
        self._dDIGITALIO.writeAttribute('DIS_STP_DIS1_M', 0x02)
        self.logMessage("partialAcquisitionReset()", self.INFO)
        
    @handleError
    def start(self):
        self.logMessage("start():", self.INFO)
        
        self._dSPI.init()
        self._dADCCORE.init()
        self._dMEM.init()
        self._dIDGEN.init()
        self._dDAC.init()
        self._dFIFO_1.init()
        self._dFIFO_2.init()
        self._dFIFO_3.init()
        self._dFIFO_4.init()
        self._dAVERAGE_1.init()
        self._dAVERAGE_2.init()
        self._dAVERAGE_3.init()
        self._dAVERAGE_4.init()
        self._dDIGITALIO.init()
        self._dFPGA.init()
        
        self.setRange("1mA")
        self.setFilter("3200Hz")
        self.setTrigMode("SOFTWARE")
        self.setTrigPol("RISING")
        self.setTrigInput('DIO_1')
        self.setTrigDelay(0)
        self.setAcqTime(100)
        self.setAcqLowTime(100)
        self.setAcqNTriggers(0)
        
        self.fifosize = 0
        
        # Configure IOPorts as input
        for el in range(1,len(_TRIGINPUTS)+1):
            self.setGPIOConfig(el,1)        
        
        # Buffers for ADC channel readings
        self.clearDataBuffers()
        if self._acq_thread is not None:
            self.stopAcq()
        self._acq_thread = None
        
        self.setState("STATE_ON")
        
        self.logMessage("init(): Harmony module initialized", self.INFO)
        
    @handleError
    def stop(self):
        self.logMessage("stop(): End Harmony control module", self.INFO)
        
        if self.isAcquiring():
            if self._acq_thread is not None:
                self.stopAcq()
            self._acq_thread = None
        
        self._dMEM.stop()
                
        self.logMessage("stop(): Harmony process dead!!", self.INFO)

    def shareApplications(self, applications):
        self.logMessage("shareApplications(): Getting needed applications layers", self.INFO)
        
        self._MEMMW = applications['MEMORY_APP']['pointer']
    
    @handleError
    def setRange(self, range):
        if not self.isAcquiring() and (range.lower() in _RANGE or range.lower() == "auto"):
            self._range = range
            for ch in _CHANNELS:
                self.caSetRange(ch, self._range)
            self.logMessage("setRange(): Range set to %s"%str(self._range), self.INFO)
            
            self.saveUserData(item='range', data=range)            
        else:
            self.logMessage("setRange(): Not possible set Range when State is %s"%str(self.getState()), self.ERROR)
            
    @handleError
    def getRange(self):
        return self._range
        
    @handleError
    def setFilter(self, filter):
        if not self.isAcquiring() and filter.lower() in _FILTER:
            self._filter = filter
            
            for ch in _CHANNELS:
                self.caSetFilter(ch, self._filter)
            self.logMessage("setFilter(): Filter set to %s"%str(self._filter), self.INFO)
            
            self.saveUserData(item='filter', data=filter)             
        else:
            self.logMessage("setFilter(): Not possible set Filter %s when State is %s"%(str(self._filter),str(self.getState())), self.ERROR)
            
    @handleError
    def getFilter(self):
        return self._filter
    
    @handleError
    def setTrigMode(self, value):
        trigmode = str(value).upper()
        if not self.isAcquiring() and trigmode in _TRIGGERMODE:
            self._trigmode = trigmode
            
            self.logMessage("setTrigMode(): Trigger mode set to %s"%str(self._trigmode), self.INFO)
            
            self.saveUserData(item='trigmode', data=value)             
        else:
            self.logMessage("setTrigMode(): Not possible set Trigger Mode. State=%s value=%s"%(str(self.getState()),str(trigmode)), self.ERROR)
            
    @handleError
    def getTrigMode(self):
        return self._trigmode    
    
    @handleError
    def setTrigPol(self, value):
        trigpol = str(value).upper()
        if not self.isAcquiring() and trigpol in _POLARITY:
            self._trigpol = trigpol
            
            self.logMessage("setTrigPol(): Trigger polarity set to %s"%str(self._trigpol), self.INFO)
            
            self.saveUserData(item='trigpol', data=value)                         
        else:
            self.logMessage("setTrigPol(): Not possible set Trigger polarity State=%s Value=%s"%(str(self.getState()),str(trigpol)), self.ERROR)
            
    @handleError
    def getTrigPol(self):
        return self._trigpol
    
    @handleError
    def setAcqLowTime(self, value):
        # Acqtime in miliseconds
        acqlowtime = int(value)
        if not self.isAcquiring():
            self._acqlowtime = acqlowtime
            self.logMessage("setAcqLowTime(): Acquisition low time set to %s miliseconds"%str(self._acqlowtime), self.INFO)

            self.saveUserData(item='acqlowtime', data=value)             
        else:
            self.logMessage("setAcqLowTime(): Not possible set Acquisition low time polarity when State is %s"%str(self.getState()), self.ERROR)
            
    @handleError
    def getAcqLowTime(self):
        return self._acqlowtime
    
    @handleError
    def setAcqTime(self, value):
        # Acqtime in miliseconds
        acqtime = int(value)
        if not self.isAcquiring():
            self._acqtime = acqtime
            self.logMessage("setAcqTime(): Acquisition time set to %s miliseconds"%str(self._acqtime), self.INFO)

            self.saveUserData(item='acqtime', data=value)             
        else:
            self.logMessage("setAcqTime(): Not possible set Acquisition time polarity when State is %s"%str(self.getState()), self.ERROR)
            
    @handleError
    def getAcqTime(self):
        return self._acqtime    
    
    @handleError
    def setTrigDelay(self, value):
        trigdelay = int(value)        
        if not self.isAcquiring():
            self._trigdelay = trigdelay
            self.logMessage("setTrigDelay(): Trigger delay set to %s"%str(self._trigdelay), self.INFO)

            self.saveUserData(item='trigdelay', data=value)             
        else:
            self.logMessage("setTrigDelay(): Not possible set Trigger delay polarity when State is %s"%str(self.getState()), self.ERROR)
            
    @handleError
    def getTrigDelay(self):
        return self._trigdelay
    
    @handleError
    def setTrigInput(self, value):
        triginput = str(value).upper()
        if not self.isAcquiring() and triginput in _TRIGINPUTS:
            self._triginput =  triginput
            
            self.logMessage("setTrigInput(): Trigger input set to %s"%str(self._triginput), self.INFO)

            self.saveUserData(item='triginput', data=value)                         
        else:
            self.logMessage("setTrigInput(): Not possible set Trigger input when State is %s"%str(self.getState()), self.ERROR)
            
    @handleError
    def getTrigInput(self):
        return self._triginput    
    
    @handleError
    def setAcqNTriggers(self, value):
        # Acqtime in miliseconds
        if not self.isAcquiring():
            self._acqntriggers = int(value)
            self.logMessage("setAcqNTriggers(): Acquisition triggers set to %s "%str(self._acqntriggers), self.INFO)

            self.saveUserData(item='acqntriggers', data=value)             
        else:
            self.logMessage("setAcqNTriggers(): Not possible set Acquisition triggers when State is %s"%str(self.getState()), self.ERROR)
            
    @handleError
    def getAcqNTriggers(self):
        if self._acqntriggers is not None:
            return self._acqntriggers
        else:
            return 0
    
    
    def startAcq(self, command=None):
        def calculateMask(*args):
            nor_value = ~reduce(lambda x, y: x|y, args)
            and_value = reduce(lambda x, y: x&y, args)
            mask = (nor_value | and_value)  & 0xff
            return mask
        
        self.logMessage("startAcq()", self.INFO)
        st = self.getState()
        
        if not self.isAcquiring():
            self.setState("STATE_RUNNING")            
            
            #self.logMessage("startAcq(): Range set to %s"%self._range, self.INFO)
            #self.logMessage("startAcq(): Filter set to %s"%self._filter, self.INFO)
            self.logMessage("startAcq(): Trigger mode set to %s"%self._trigmode, self.INFO)
            self.logMessage("startAcq(): Trigger polarity set to %s"%self._trigpol, self.INFO)
            self.logMessage("startAcq(): Acquisition time set to %s"%self._acqtime, self.INFO)
            self.logMessage("startAcq(): Acquisition low time set to %s"%self._acqlowtime, self.INFO)
            self.logMessage("startAcq(): Trigger input set to %s"%self._triginput, self.INFO)
            self.logMessage("startAcq(): Trigger delay set to %s"%self._trigdelay, self.INFO)
            
            try:
                # 1. Assure acquisition thread is stopped
                if self._acq_thread is not None:
                    self.stopAcq()
                    self._acq_thread.end()
                    self._acq_thread.join()
                    self._acq_thread = None
                    
                self._dADCCORE.init()
                self._dIDGEN.init()
                self._dFIFO_1.init()
                self._dFIFO_2.init()
                self._dFIFO_3.init()
                self._dFIFO_4.init()
                self._dAVERAGE_1.init()
                self._dAVERAGE_2.init()
                self._dAVERAGE_3.init()
                self._dAVERAGE_4.init()
                self._dDIGITALIO.init()
                
                # 2. initializes memory stopping to save data 
                self.logMessage("startAcq(): (1/14) Stop memory saving to configure devices", self.INFO)
                self._dADCCORE.writeAttribute('ID_CH1_ID', 0)
                self._dADCCORE.writeAttribute('ID_CH2_ID', 0)
                self._dADCCORE.writeAttribute('ID_CH3_ID', 0)
                self._dADCCORE.writeAttribute('ID_CH4_ID', 0)
                self._dADCCORE.writeAttribute('CTL_RST', 0x01)
                self._dADCCORE.writeAttribute('CTL_ADQ_M', 0x00)
                self._dADCCORE.writeAttribute('CTL_RANGE', 0x01)
                self._dADCCORE.writeAttribute('CTL_ADC_OS',0x06)
                self._dADCCORE.writeAttribute('CTL_DBL_RATE',0x00)                
                self._dMEM.writeAttribute('CTL_SAVE', 0x00)
                self._dMEM.writeAttribute('CTL_ONTRIGGER', 0x00)

                # 4 configure Average module
                self.logMessage("startAcq(): (2/14) configure Average modules", self.INFO)
                self._dAVERAGE_1.writeAttribute('AVG_CTL_ENA', 0x03)
                self._dAVERAGE_1.writeAttribute('AVG_CTL_PRE_DIV', 0x00)
                self._dAVERAGE_2.writeAttribute('AVG_CTL_ENA', 0x03)
                self._dAVERAGE_2.writeAttribute('AVG_CTL_PRE_DIV', 0x00)
                self._dAVERAGE_3.writeAttribute('AVG_CTL_ENA', 0x03)
                self._dAVERAGE_3.writeAttribute('AVG_CTL_PRE_DIV', 0x00)
                self._dAVERAGE_4.writeAttribute('AVG_CTL_ENA', 0x03)
                self._dAVERAGE_4.writeAttribute('AVG_CTL_PRE_DIV', 0x00)

                self._dAVERAGE_1.writeAttribute('ID_CFG_ID_IN', _FIFO_ID_1)
                self._dAVERAGE_2.writeAttribute('ID_CFG_ID_IN', _FIFO_ID_2)
                self._dAVERAGE_3.writeAttribute('ID_CFG_ID_IN', _FIFO_ID_3)
                self._dAVERAGE_4.writeAttribute('ID_CFG_ID_IN', _FIFO_ID_4)
                
                self._dAVERAGE_1.writeAttribute('ID_CFG_ID_IP', _ADC_CH_ID_1)
                self._dAVERAGE_2.writeAttribute('ID_CFG_ID_IP', _ADC_CH_ID_2)
                self._dAVERAGE_3.writeAttribute('ID_CFG_ID_IP', _ADC_CH_ID_3)
                self._dAVERAGE_4.writeAttribute('ID_CFG_ID_IP', _ADC_CH_ID_4)

                self._dAVERAGE_1.writeAttribute('ID_CFG_ID_OUT', _AVG_ID_1)
                self._dAVERAGE_2.writeAttribute('ID_CFG_ID_OUT', _AVG_ID_2)
                self._dAVERAGE_3.writeAttribute('ID_CFG_ID_OUT', _AVG_ID_3)
                self._dAVERAGE_4.writeAttribute('ID_CFG_ID_OUT', _AVG_ID_4)
                
                #3. Calculates Acquisition time. Sampleacqtime value in milliseconds
                self._acqtime_counts = 1
                sampleacqtime = self._dADCCORE.getMinSampleAcqTime()
                self._max_fifosizes = self._dFIFO_1.getMaxFIFOSize()                

                if (self._acqtime > (self._max_fifosizes*sampleacqtime)):
                    self.logMessage("startAcq(): (3/14) Configure acquisition time case ACQTIME > FIFO_MAX_SIZE", self.INFO)                            

                    self._acq_type = 'TIME_ABOVE_FIFO_RANGE'

                    # 3.1.1 Calculate partial divisions and fifo size
                    def searchPartialDivisions():
                        maxsize = (self._max_fifosizes * sampleacqtime)
                        
                        divs = 1
                        for i in range(1,self._max_fifosizes):
                            if (self._acqtime/i) <= maxsize:
                                divs = i
                                break

                        divsize = int((self._acqtime/divs)/sampleacqtime)
                        
                        return divs, divsize
                    
                    self._acqtime_counts, self.fifosize = searchPartialDivisions()

                    # 3.1.2 Configure Counter 1 to count partial divisions
                    self.logMessage("startAcq(): (3.1/14) Counter 1 configured to count the %s partial acquisitions"%str(self._acqtime_counts), self.INFO)                            
                    self._dDIGITALIO.writeAttribute('CNT1_STP_OUT_ID', _CNT1_ID)
                    #self._dDIGITALIO.writeAttribute('CNT1_STP_SRC_ID', _ADC_CH_ID_1)
                    self._dDIGITALIO.writeAttribute('CNT1_STP_SRC_ID', _AVG_ID_4)
                    self._dDIGITALIO.writeAttribute('CNT1_STP_SIG', 0x00)
                    self._dDIGITALIO.writeAttribute('CNT1_STP_TRIG', 0x01)
                    self._dDIGITALIO.writeAttribute('CNT1_STP_SRC', 0x0E)
                    self._dDIGITALIO.writeAttribute('CNT1_V_CNT_V', 0x00)                
                    self._dDIGITALIO.writeAttribute('TRG1_V_CNT_V', self.fifosize)
                    
                    self._dDIGITALIO.writeAttribute('DIS_STP_DIS1_ID', _IDGEN_ID)
                    self._dDIGITALIO.writeAttribute('CNT1_STP_DIS', 0x01)
                    
                    self._dDIGITALIO.writeAttribute('DIS_STP_DIS1_M', 0x03)
                    self._dDIGITALIO.writeAttribute('DIS_STP_WD1', 0x01)
                    
                    self._dDIGITALIO.writeAttribute('DIS_STP_DIS1_M', 0x02)
                    
                    # 3.1.3 Calculates memory mask and trigger
                    mem_trig = _CNT1_ID
                    maskval = calculateMask(_AVG_ID_1, _AVG_ID_2, _AVG_ID_3, _AVG_ID_4, _IDGEN_ID, _CNT1_ID)
                else:
                    self.logMessage("startAcq(): (3/14) Configure acquisition time case ACQTIME <= FIFO_MAX_SIZE", self.INFO)                            

                    self._acq_type = 'TIME_INSIDE_FIFO_RANGE'

                    # 3.2.1 Calculate fifo size, memory mak and triger
                    self.fifosize = int(self._acqtime/sampleacqtime)
                    mem_trig = _IDGEN_ID
                    maskval = calculateMask(_AVG_ID_1, _AVG_ID_2, _AVG_ID_3, _AVG_ID_4, _IDGEN_ID)

                # 4. Initializes FIFO and FIFO size
                # Added -1 due to FIFO by default is storing 1 more data than requested
                self.logMessage("startAcq(): (4/14) Initialize FIFO", self.INFO)
                self._dFIFO_1.writeAttribute('MEM_CTL_ID_OUT', 0x00)
                self._dFIFO_2.writeAttribute('MEM_CTL_ID_OUT', 0x00)
                self._dFIFO_3.writeAttribute('MEM_CTL_ID_OUT', 0x00)
                self._dFIFO_4.writeAttribute('MEM_CTL_ID_OUT', 0x00)
                
                self.logMessage("startAcq(): (4.1/14) Configure FIFO size to %s data"%str(self.fifosize-1), self.INFO)                
                self._dFIFO_1.writeAttribute('FIFO_SIZE_SIZE',self.fifosize-1)
                self._dFIFO_2.writeAttribute('FIFO_SIZE_SIZE',self.fifosize-1)
                self._dFIFO_3.writeAttribute('FIFO_SIZE_SIZE',self.fifosize-1)
                self._dFIFO_4.writeAttribute('FIFO_SIZE_SIZE',self.fifosize-1)

                # 5. Initializes FIFO with empty data using the ID GEN, before enabling the ADC
                self.logMessage("startAcq(): (5/14) Initialize FIFO", self.INFO)
                self._dFIFO_1.writeAttribute('MEM_CTL_ID_IN', _TEMPORAL_ID)
                self._dFIFO_2.writeAttribute('MEM_CTL_ID_IN', _TEMPORAL_ID)
                self._dFIFO_3.writeAttribute('MEM_CTL_ID_IN', _TEMPORAL_ID)
                self._dFIFO_4.writeAttribute('MEM_CTL_ID_IN', _TEMPORAL_ID)
                self._dIDGEN.writeAttribute('WAIT_TIME', 0x00)  
                self._dIDGEN.writeAttribute('TS_ID_ID_OUT', _TEMPORAL_ID)
                self._dIDGEN.writeAttribute('DATA_GEN_DATA', 0x00)
                
                for i in range(0, self.fifosize+1):
                    self._dIDGEN.writeAttribute('ID_GEN_CTL_MTRIG', 0x01)
                self._dIDGEN.writeAttribute('TS_ID_ID_OUT', 0x00)

                self._dFIFO_1.writeAttribute('MEM_CTL_ID_IN', _ADC_CH_ID_1)
                self._dFIFO_2.writeAttribute('MEM_CTL_ID_IN', _ADC_CH_ID_2)
                self._dFIFO_3.writeAttribute('MEM_CTL_ID_IN', _ADC_CH_ID_3)
                self._dFIFO_4.writeAttribute('MEM_CTL_ID_IN', _ADC_CH_ID_4)

                self._dFIFO_1.writeAttribute('MEM_CTL_ID_OUT', _FIFO_ID_1)
                self._dFIFO_2.writeAttribute('MEM_CTL_ID_OUT', _FIFO_ID_2)
                self._dFIFO_3.writeAttribute('MEM_CTL_ID_OUT', _FIFO_ID_3)
                self._dFIFO_4.writeAttribute('MEM_CTL_ID_OUT', _FIFO_ID_4)

                # 6. Check Trigger Type and configure trigger inputs, for hw trigger or counter for SW trigger
                self.logMessage("startAcq(): (6/14) trigger mode %s"%self._trigmode, self.INFO)            
                if self._trigmode in ["SOFTWARE",'AUTOTRIGGER']:
                    # 6.1.1 Configure IDGEN to generate the SW trigger 
                    self.logMessage("startAcq(): (6.1/14) ID Gen configured to set SW triggers", self.INFO)                                
                    self._dIDGEN.writeAttribute('ID_GEN_CTL_ETI', 0x00)
                    self._dIDGEN.writeAttribute('ID_GEN_CTL_CLKE', 0x01)
                    self._dIDGEN.writeAttribute('DATA_GEN_DATA', 0x00)
                    #self._dIDGEN.writeAttribute('TS_ID_ID_OUT', _IDGEN_ID)
                    
                    # 6.1.2 Configure Counter 0 to count the number of triggers generated
                    self.logMessage("startAcq(): (6.2/14) CNT0 configured to count SW triggers", self.INFO)                                
                    self._dDIGITALIO.writeAttribute('CNT0_STP_OUT_ID', 0x00)
                    self._dDIGITALIO.writeAttribute('CNT0_STP_SRC_ID', _IDGEN_ID)
                    self._dDIGITALIO.writeAttribute('CNT0_STP_SIG', 0x00)
                    self._dDIGITALIO.writeAttribute('CNT0_V_CNT_V', 0x00)
                    self._dDIGITALIO.writeAttribute('CNT0_STP_SRC', 0x0E)
                    self._dDIGITALIO.writeAttribute('CNT0_STP_DIS', 0x07)
                    self._dDIGITALIO.writeAttribute('TRG0_V_CNT_V', 0x01)
                    
                    if self._trigmode == 'AUTOTRIGGER':
                        # 6.1.3 Configure Counter 3 to count the number of triggers generated
                        self.logMessage("startAcq(): (6.3/14) CNT2 configured to count SW autotriggers", self.INFO)                                
                        # This calculates the number of FPGA clocks (16ns)
                        total_counts = int((self._acqtime + self._acqlowtime)/40e-6)
                        self._dDIGITALIO.writeAttribute('CNT2_STP_SIG', 0x00)
                        self._dDIGITALIO.writeAttribute('CNT2_STP_OUT_ID', _IDGEN_ID)
                        self._dDIGITALIO.writeAttribute('CNT2_STP_TRIG', 0x02)
                        self._dDIGITALIO.writeAttribute('CNT2_STP_SRC', 0x00)
                        self._dDIGITALIO.writeAttribute('TRG2_V_CNT_V', total_counts)
                        self._dDIGITALIO.writeAttribute('CNT2_STP_DIS', 0x07)
                    else:
                        self._dDIGITALIO.writeAttribute('CNT2_STP_DIS', 0x00)
                        self._dDIGITALIO.writeAttribute('CNT2_STP_OUT_ID', 0x00)
                    
                else:
                    # 6.2.1 Configure HW trigger input
                    self.logMessage("startAcq(): (6.1/14) Trigger Input %s configures"%str(self._triginput), self.INFO)                                
                    tg_input = _TRIGINPUTS.index(self._triginput)
                    tg_pol = _POLARITY.index(self._trigpol)
                    
                    self.setGPIOConfig(tg_input+1,0x01, pol=tg_pol)
                    
                    # 6.2.2 Configure Counter 0 to count the number of HW triggers received
                    self.logMessage("startAcq(): (6.2/14) Counter 0 configured to count HW triggers ", self.INFO)
                    self._dDIGITALIO.writeAttribute('CNT0_STP_OUT_ID', _CNT0_ID)
                    self._dDIGITALIO.writeAttribute('CNT0_STP_SIG', 0x00)
                    self._dDIGITALIO.writeAttribute('CNT0_STP_TRIG', 0x00)
                    self._dDIGITALIO.writeAttribute('CNT0_STP_SRC', tg_input+1)
                    self._dDIGITALIO.writeAttribute('TRG0_V_CNT_V', 0x01)
                    self._dDIGITALIO.writeAttribute('CNT0_V_CNT_V', 0x00)
                    self._dDIGITALIO.writeAttribute('CNT0_STP_DIS', 0x07)
                    
                    
                    self.logMessage("startAcq(): (6.3/14) ID GEN configured to generate ID when CNT0_ID is generated", self.INFO)            
                    self._dIDGEN.writeAttribute('ID_GEN_CTL_ETI', 0x01)
                    self._dIDGEN.writeAttribute('ID_GEN_CTL_CLKE', 0x01)
                    self._dIDGEN.writeAttribute('DATA_GEN_DATA', 0x00)
                    self._dIDGEN.writeAttribute('ID_GEN_CTL_TRIGGERID', _CNT0_ID)
                    #self._dIDGEN.writeAttribute('TS_ID_ID_OUT', _IDGEN_ID)
                    
                    
                # 7. Configure trigger delay WAIT_TIME unit is 1024 nano seconds.
                # trigger delay unit is milliseconds, so to calculate the number of WAIT_TIME steps:
                self.logMessage("startAcq(): (7/14) Configure trigger delay ", self.INFO)                            
                delay_value = int(self._trigdelay * (1E-3/(1024*1E-9)))
                self._dIDGEN.writeAttribute('WAIT_TIME', delay_value)  
                self._dIDGEN.writeAttribute('TS_ID_ID_OUT', _IDGEN_ID)

                # 8. Configure memory trigger 
                self.logMessage("startAcq(): (8/14) Configure Memory Trigger", self.INFO)
                self._dMEM.writeAttribute('CTL_TRIGID',mem_trig)
                self._dMEM.writeAttribute('CTL_IDMASK',maskval)
                self._dMEM.writeAttribute('CTL_ID',_AVG_ID_1)

                # 9. Reset average after FIFO init
                self.logMessage("startAcq(): (9/14) Reset Average", self.INFO)
                self._dAVERAGE_1.writeAttribute('AVG_CTL_WB_RST', 0x01)
                self._dAVERAGE_2.writeAttribute('AVG_CTL_WB_RST', 0x01)
                self._dAVERAGE_3.writeAttribute('AVG_CTL_WB_RST', 0x01)
                self._dAVERAGE_4.writeAttribute('AVG_CTL_WB_RST', 0x01)
                    
                # 10. Start acquisition by enabling memory save data
                self.logMessage("startAcq(): (10/14) Start memory Saving", self.INFO)
                self._dMEM.clearMemoryBuffer()
                self._dMEM.writeAttribute('CTL_ONTRIGGER', 0x01)
                self._dMEM.writeAttribute('CTL_RST', 0x01)
                self._dMEM.writeAttribute('CTL_SAVE', 0x01)

                # 11. Configure ADC to start acquisition
                self.logMessage("startAcq(): (11/14) Configures ADC", self.INFO)

                self._dADCCORE.writeAttribute('ID_CH1_ID', _ADC_CH_ID_1)
                self._dADCCORE.writeAttribute('ID_CH2_ID', _ADC_CH_ID_2)
                self._dADCCORE.writeAttribute('ID_CH3_ID', _ADC_CH_ID_3)
                self._dADCCORE.writeAttribute('ID_CH4_ID', _ADC_CH_ID_4)

                # 12. Reset Digital IO module
                self.logMessage("startAcq(): (12/14) Reset DigitalIO", self.INFO)
                self._dDIGITALIO.writeAttribute('DIO_STP_RST', 0x1)
                
                # 13. Starts Harmony Acquisition Thread.
                self.logMessage("startAcq() (13/14) Start acquisition thread",self.INFO)
                self._acq_thread = AcquisitionThread(self)
                self._acq_thread.setAcquiringFlag(False)
                self._acq_thread.setDaemon(True)
                self._acq_thread.start()
                
                # C/M to avoid first data acquisition
                time.sleep(0.1)
                self._dMEM.clearMemoryBuffer()
                self.clearDataBuffers()
                            
                self.setState("STATE_RUNNING")                                        
                self.logMessage("startAcq(): (14/14) Acquisition Started", self.INFO)

                if command is not None and "swtrig" in command.lower():
                    self.setSWTrigger(True)
            except Exception, e:
                self.logMessage("startAcq():Acquisition not started due to %s"%str(e), self.ERROR)
                self.setState("STATE_FAULT")            
        else:
            self.logMessage("startAcq():Not possible start acquisition in current state %s"%str(self.getState()), self.ERROR)
            return False
        
        return True        
        
    @handleError
    def stopAcq(self, value=False):
        self.logMessage("stopAcq()", self.INFO)
        try:
            # Stops data saving in memoryCHND:CURRENT
            self._dMEM.writeAttribute('CTL_SAVE', 0x00)

            # Stops count triggers
            self._dDIGITALIO.writeAttribute('CNT0_STP_DIS', 0x00)
            self._dDIGITALIO.writeAttribute('CNT2_STP_DIS', 0x00)
            
            if self._acq_type == 'TIME_ABOVE_FIFO_RANGE':
                # Diseble partial acquisition counter
                self._dDIGITALIO.writeAttribute('DIS_STP_DIS1_M', 0x03)
                self._dDIGITALIO.writeAttribute('DIS_STP_WD1', 0x00)
            
            self._dADCCORE.writeAttribute('ID_CH1_ID',0x00)
            self._dADCCORE.writeAttribute('ID_CH2_ID',0x00)
            self._dADCCORE.writeAttribute('ID_CH3_ID',0x00)
            self._dADCCORE.writeAttribute('ID_CH4_ID',0x00)
            self.logMessage("stopAcq() Memory saving stopped",self.INFO)

            if str(value).upper() != "STOP_FROM_THREAD":
                if self._acq_thread is not None:
                    self._acq_thread.end()                    
                        
                    while not self._acq_thread.getProcessEnded():
                        self.logMessage("stopAcq(): Waiting process to die", self.INFO)
                        time.sleep(0.5)
                    
            self._acq_thread = None
            self.setState("STATE_ON")            

            self.logMessage("stopAcq() Acquisition Thread stopped", self.INFO)
        except Exception, e:
            self.logMessage("stopAcq():Acquisition not stopped due to %s"%str(e), self.ERROR)
            self.setState("STATE_FAULT")

    @handleError
    def getNData(self):
        val = self._dDIGITALIO.readAttribute('CNT0_V_CNT_V')
        self.logMessage("getNData() Size of the triggers received during the acquisition %s"%str(val), self.DEBUG)
        return val
    
    @handleError
    def setSWTrigger(self, value):
        st = self.getState()
        if st == "STATE_RUNNING" and self._trigmode == "SOFTWARE" and self._acq_thread is not None:
            if not self._acq_thread.getAcquiringFlag():
                self.logMessage("setSWTrigger() Force acquisition", self.INFO)
                self._dIDGEN.writeAttribute('ID_GEN_CTL_MTRIG', 0x01)
                self._acq_thread.setAcquiringFlag(True)
            else:
                self.logMessage("setSWTrigger():Not possible to set SW trigger still acquiring previous", self.ERROR)
                return False
        else:
            self.logMessage("setSWTrigger():Not possible to set SW trigger in %s with trigger %s"%(str(st),str(self._trigmode)), self.ERROR)
            return False
    
    @handleError
    def getMeas(self, params=None):
        ret_val = []
        params = str(params).split(",")
        try:
            idx = eval(params[0])
        except:
            idx = None
        try:
            ndata = eval(params[1])
        except:
            ndata = None
        for i in range(0,4):
            ret_val.append(['CHAN0'+str(i+1),self.getCurrent(i, params=idx, ndata=ndata)])
        
        self.logMessage("getMeas() Returns the values read in Memory", self.DEBUG)
        
        return '[%s]' % ', '.join(map(str, ret_val))
    
    @handleError
    def getGeneralBuffer(self):
        ret_val = self._general_buffer
        
        txt = ["[%s, %s, %s]"%(hex(a[0]), hex(a[1]), hex(a[2])) for a in ret_val]
        self.logMessage("getGeneralBuffer(): data=[%s] "%(', '.join(map(str, txt)) ), self.DEBUG)        
        return '[%s]' % ', '.join(map(str, ret_val))

    @handleError
    def getSCPIInstantVoltage(self, value):
        return self.getInstantVoltage(self, value-1)
    
    @handleError
    def getInstantVoltage(self, value):
        ch_name = ['ADC_CH1','ADC_CH2','ADC_CH3','ADC_CH4']
        curr = self._dADCCORE.getInstantVoltage(ch_name[value])
        self.logMessage("getInstantVoltage(): Channel=%s Current=%s"%(value,str(curr)), self.DEBUG)
        return curr

    @handleError
    def getSCPIInstantCurrent(self, value):
        return self.getInstantCurrent(value-1)

    @handleError
    def getInstantCurrent(self, value):
        volt_val = self.getInstantVoltage(value)
        curr = self.convertVoltToCurr(value , volt_val)
        self.logMessage("getInstantCurrent(): Channel=%s Current=%s"%(value,str(curr)), self.DEBUG)

        return curr

    def convertVoltToCurr(self, channel, volt):
        # Current value returned in Amps
        tigain_table = {'10k':  10e3,
                        '1m':   1e6,
                        '100m': 100e6,
                        '1g':   1e9,
                        '10g':  10e9,
                       }
        
        vgain_table = {'1': 1,
                        '10': 10,
                        '50': 50,
                        '100': 100,
                        'sat': 1000,
                       }
        
        tigain_val = float(tigain_table[self._dSPI.caGetTIGain(channel).lower()])
        vgain_val = float(vgain_table[self._dSPI.caGetVGain(channel).lower()])
        
        # Maximum scale is fixed to +/-10V
        curr = (volt / ( tigain_val * vgain_val ) )
        
        # Calculated value in Amps.
        # Always return value in miliAmps
        curr = curr*1000
        
        return curr

    
    @handleError
    def getFWVersion(self):
        ver = self._dFPGA.getFWVersion()
        self.logMessage("getFWVersion(): FW version %s"%ver, self.DEBUG)
        return ver
    
    def getFWVersionDate(self):
        date = self._dFPGA.getFWVersionDate()
        self.logMessage("getFWVersion(): FW version date %s"%date, self.DEBUG)
        return date
    
    @handleError
    def getTriggerState(self):
        ret_val = []
        ret_val.append(['MODE',self._trigmode])
        ret_val.append(['POLARITY',self._trigpol])
        ret_val.append(['DELAY',self._trigdelay])
        ret_val.append(['INPUT',self._triginput])        

        self.logMessage("getTriggerState(): data=[%s] "%', '.join(map(str, ret_val)), self.DEBUG)
        return '[%s]' % ', '.join(map(str, ret_val))

    @handleError
    def getSCPICurrent(self, channel, params = None):
        return self.getCurrent(channel-1, params)

    @handleError
    def getCurrent(self, channel, params = None, ndata=None):
        self.logMessage("getCurrent(): Channel=%d reading form fast bus"%channel, self.DEBUG)

        ret_val = []
        chdata = []
        if params is not None:
            if ndata is not None:
                end_idx = (int(params)+1) + int(ndata)
                if end_idx > len(self._ch_readdata[channel]):
                    end_idx = len(self._ch_readdata[channel])
                chdata = self._ch_readdata[channel][int(params)+1:end_idx]
            else:
                chdata = self._ch_readdata[channel][int(params)+1:]
        else:
            chdata = self._ch_readdata[channel]
        for el in chdata:
            ret_val.append(el[1])
        
        self.logMessage("getCurrent(): Channel=%d with data=[%s] "%(channel,', '.join(map(str, ret_val)) ), self.DEBUG)
        return '[%s]' % ', '.join(map(str, ret_val))

    @handleError
    def getTriggerData(self):
        self.logMessage("getCurrent(): Reading trigger acquisition data data=[%s] "%(', '.join(map(str, self._trigger_data)) ), self.DEBUG)
        return '[%s]' % ', '.join(map(str, self._trigger_data))

    @handleError    
    def getValidTriggers(self):
        ret_value = self._validtriggers if self._validtriggers is not None else 0
        self.logMessage("getValidTriggers(): Valid Triggers = %s "%str(ret_value), self.DEBUG)
        return ret_value


    @handleError
    def getCurrentWithTS(self, channel, params = None, ndata=None):
        self.logMessage("getCurrent(): Channel=%d reading form fast bus"%channel, self.DEBUG)

        chdata = []
        if params is not None:
            if ndata is not None:
                end_idx = (int(params)+1) + int(ndata)
                if end_idx > len(self._ch_readdata[channel]):
                    end_idx = len(self._ch_readdata[channel])
                chdata = self._ch_readdata[channel][int(params)+1:end_idx]
            else:
                chdata = self._ch_readdata[channel][int(params)+1:]
        else:
            chdata = self._ch_readdata[channel]

        self.logMessage("getCurrent(): Channel=%d with data=[%s] "%(channel,', '.join(map(str, chdata)) ), self.DEBUG)
        return '[%s]' % ', '.join(map(str, chdata))


    @handleError
    def getSCPIAverageCurrent(self, channel):
        return self.getAverageCurrent(channel-1)

    @handleError
    def getAverageCurrent(self, channel):
        self.logMessage("getAverageCurrent(): Channel=%d "%channel, self.DEBUG)
        # Read channel data fisrt
        
        curr_list = []
        for el in self._ch_readdata[channel]:
            curr_list.append(el[1])
        
        avg = 0
        datalen = len(curr_list)
        if datalen != 0:
            for dt in curr_list:
                avg += dt
                
            avg = avg/datalen
        
        self.logMessage("getAverageCurrent(): Channel=%d AverageCurrent=%s"%(channel, str(avg)), self.DEBUG)
        return avg
    
    def getGPIOName(self, channel):
        channel -= 1 
        name =  _TRIGINPUTS[channel]
        return name
    
    def getGPIOConfig(self, channel):
        channel -= 1 
        gpio_input = _TRIGINPUTS[channel]
        tmp_val = self._dDIGITALIO.readAttribute('DIO_STP_IO')
        mask = 0x01<<channel
        ret_val = _GPIO_TYPE[bool((tmp_val & mask)>>channel)]        
        
        self.logMessage("getGPIOConfig(): %s set as %s "%(gpio_input, ret_val), self.DEBUG)
        return ret_val
        
    
    def setGPIOConfig(self, channel, value, pol = 0):
        channel -= 1 
        gpio_input = _TRIGINPUTS[channel]
        st = self.getState()
        if channel == self._triginput and st == "STATE_RUNNING":
            self.logMessage("setGPIOConfig(): Not possible to change %s input config while state is %s"%(gpio_input, st), self.INFO)
            return

        value = int(value) & 0x1
        
        # If D_IO or DIFF_IO as OUTPUT, then configure SPI first
        if value != 0x1:
            self.logMessage("setGPIOConfig(): Port set as Output. Configure SPI", self.INFO)
            if gpio_input>='DIO_1' and gpio_input<='DIO_4':
                # DIO inputs from 1 to 4
                dio_input = channel+1
                self._dSPI.feSetDIODirection(dio_input, value)
            else:
                # DIFF inputs from 1 to9
                diff_input = channel-_TRIGINPUTS.index('DIO_4')
                self._dSPI.feSetGPIODirection(diff_input, value)

        self.logMessage("setGPIOConfig(): Configure DigitalI/O", self.INFO)
        tmp_val = self._dDIGITALIO.readAttribute('DIO_STP_IO')
        if value == 0x1:
            mask = 0x01<<channel
            tmp_val = tmp_val | mask
        else:
            mask = 0xffff - (0x01<<channel)
            tmp_val = tmp_val & mask
        self._dDIGITALIO.writeAttribute('DIO_STP_IO', tmp_val)

        polvalue = int(pol) & 0x1
        tmp_val = self._dDIGITALIO.readAttribute('DIO_STP_IOP')
        if polvalue == 0x1:
            mask = 0x01<<channel
            tmp_val = tmp_val | mask
        else:
            mask = 0xffff - (0x01<<channel)
            tmp_val = tmp_val & mask
        self._dDIGITALIO.writeAttribute('DIO_STP_IOP', tmp_val)
        
        tmp_val = self._dDIGITALIO.readAttribute('DIO_V_D_MASK')
        # Do not chane polarity
        if value == 0x1:
            mask = 0xffff - (0x01<<channel)
            tmp_val = tmp_val & mask            
        else:
            mask = 0x01<<channel
            tmp_val = tmp_val | mask
        self._dDIGITALIO.writeAttribute('DIO_V_D_MASK', tmp_val)
        
        # If D_IO or DIFF_IO as INPUT, then configure SPI last
        if value == 0x1:
            self.logMessage("setGPIOConfig(): Port set as Input. Configure SPI", self.INFO)
            if gpio_input>='DIO_1' and gpio_input<='DIO_4':
                # DIO inputs from 1 to 4
                dio_input = channel+1
                self._dSPI.feSetDIODirection(dio_input, value)
            else:
                # DIFF inputs from 1 to9
                diff_input = channel-_TRIGINPUTS.index('DIO_4')
                self._dSPI.feSetGPIODirection(diff_input, value)

        self.logMessage("setGPIOConfig(): %s set as %s"%(gpio_input, _GPIO_TYPE[value]), self.INFO)
        
        self.saveUserData(item='gpioconfig', idx=channel+1, data=value)             
    
    def getGPIOValue(self, channel):
        channel -= 1 
        gpio_input = _TRIGINPUTS[channel]
        
        tmp_val = self._dDIGITALIO.readAttribute('DIO_V_DIO_V')
        mask = 0x01<<channel
        ret_val = bool((tmp_val & mask)>>channel)
        
        self.logMessage("getGPIOValue(): %s = %s "%(gpio_input, ret_val), self.DEBUG)
        return ret_val
    
    def setGPIOValue(self, channel, value):
        if self.getGPIOConfig(channel) != 'OUTPUT':
            self.logMessage("setGPIOValue(): Error!! Channel %s set as INPUT"%str(channel), self.INFO)
            return 

        channel -= 1 
        gpio_input = _TRIGINPUTS[channel]
        
        value = (int(value) & 0x1)
        
        tmp_val = self._dDIGITALIO.readAttribute('DIO_V_DIO_V')
        if value == 0x1:
            mask = 0x01<<channel
            tmp_val = tmp_val | mask
        else:
            mask = 0xffff - (0x01<<channel)
            tmp_val = tmp_val & mask
        self._dDIGITALIO.writeAttribute('DIO_V_DIO_V', tmp_val)
        
        self.logMessage("setGPIOValue(): %s set to %s "%(gpio_input, value), self.INFO)

        self.saveUserData(item='gpiovalue', idx=channel+1, data=value)             

    def getSupplyPort(self, channel):
        val = self._dSPI.feGetSupplyPort(channel)
        self.logMessage("getSupplyPort() channel=%s value=%s"%(channel,val), self.DEBUG)
        return val
        
    def setSupplyPort(self, channel, value):
        self.logMessage("setSupplyPort() channel=%s value=%s"%(channel, str(value)), self.INFO)
        self._dSPI.feSetSupplyPort(channel, int(value))    

        self.saveUserData(item='supplyport', idx=channel, data=value)             

    @handleError
    def caCBTemp(self):
        val = self._dSPI.caCBReadTemp()
        self.logMessage("caFeTemp() value=%f"%(val), self.DEBUG)
        return val
    
    @handleError
    def caFETemp(self):
        val = self._dSPI.feReadTemp()
        self.logMessage("caFeTemp() value=%f"%(val), self.DEBUG)
        return val
    
    @handleError
    def caSetInit(self, channel):
        self.logMessage("caSetInit() channel=%s "%channel, self.INFO)
        self._dSPI.caInit(channel-1)
        return

    @handleError
    def caGetInit(self, channel):
        val = self._dSPI.caGetInit(channel-1)
        self.logMessage("caGetInit() channel=%s value=%d"%(channel,val), self.DEBUG)
        return val
    
    @handleError
    def caReadTemp(self, channel):
        val = self._dSPI.caReadTemp(channel-1)
        self.logMessage("caTemp() channel=%s value=%f"%(channel,val), self.DEBUG)
        return val
    
    @handleError
    def caGetFilter(self, channel):
        val = self._dSPI.caGetFilter(channel-1)
        self.logMessage("getFilter() channel=%s value=%s"%(channel,val), self.DEBUG)
        return val
        
    @handleError
    def caSetFilter(self, channel, param):
        self.logMessage("setFilter() channel=%s value=%s"%(channel, str(param)), self.INFO)
        self._dSPI.caSetFilter(channel-1, param)

        self.saveUserData(item='cafilter', idx=channel, data=param)             
        
    @handleError
    def caGetPostFilter(self, channel):
        val = self._dSPI.caGetPostFilter(channel-1)
        self.logMessage("getPostFilter() channel=%s value=%s"%(channel,val), self.DEBUG)
        return val
    
    @handleError
    def caSetPostFilter(self, channel, param):
        self.logMessage("setPostFilter() channel=%s "%channel, self.INFO)
        self._dSPI.caSetPostFilter(channel-1, param)

        self.saveUserData(item='capostfilter', idx=channel, data=param)             
    
    @handleError
    def caGetPreFilter(self, channel):
        val = self._dSPI.caGetPreFilter(channel-1)
        self.logMessage("getPreFilter() channel=%s value=%s"%(channel,val), self.DEBUG)
        return val
    
    @handleError
    def caSetPreFilter(self, channel, param):
        self.logMessage("setPreFilter() channel=%s "%channel, self.INFO)
        self._dSPI.caSetPreFilter(channel-1, param)

        self.saveUserData(item='caprefilter', idx=channel, data=param)             

    @handleError
    def caGetInversion(self, channel):
        val = self._dSPI.caGetInv(channel-1)
        self.logMessage("getInversion() channel=%s value=%s"%(channel,val), self.DEBUG)
        return val
    
    @handleError
    def caSetInversion(self, channel, param):
        self.logMessage("SCPI::%s::setInversion()"%channel, self.INFO)
        self._dSPI.caSetInv(channel-1, int(param))

        self.saveUserData(item='cainversion', idx=channel, data=param)             

    @handleError
    def caGetRange(self, channel):
        if self._caRange_autoTh[channel-1] is not None:
            val = "AUTO"
        else:
            val = self.caGetRangeSet(channel)
        self.logMessage("SCPI::%s::getRange() value=%s"%(channel,val), self.DEBUG)
        return val
    
    @handleError
    def caGetRangeSet(self, channel):
        val = self._dSPI.caGetRange(channel-1)
        self.logMessage("SCPI::%s::getRange() value=%s"%(channel,val), self.DEBUG)
        return val
    
    @handleError
    def caSetRange(self, channel, param):
        self.logMessage("setRange() channel=%s value=%s"%(channel, str(param)), self.INFO)
        if param.upper() == "AUTO":
            if self._caRange_autoTh[channel-1] is None:
                self._caRange_autoTh[channel-1] = caRangeAutoThread(self, channel)
                self._caRange_autoTh[channel-1].setInitialRange(self._dSPI.caGetRange(channel-1))
                try:
                    maxlim = self._caRange_satlimits[channel-1][0]
                    minlim = self._caRange_satlimits[channel-1][1]
                except:
                    maxlim = _AUTO_RANGE_HIGHER_LIM
                    minlim = _AUTO_RANGE_LOWER_LIM
                self._caRange_autoTh[channel-1].setSaturationLimits(maxlim,minlim)
                self._caRange_autoTh[channel-1].setDaemon(True)                
                self._caRange_autoTh[channel-1].start()
        else:        
            if self._caRange_autoTh[channel-1] is not None:
                self._caRange_autoTh[channel-1].end()
                while not self._caRange_autoTh[channel-1].getProcessEnded():
                    time.sleep(0.1)
                self._caRange_autoTh[channel-1] = None
                
            self._dSPI.caSetRange(channel-1, param)
            
        self.saveUserData(item='carange',idx=channel, data=param)

    @handleError
    def caGetVGain(self, channel):
        val = self._dSPI.caGetVGain(channel-1)
        self.logMessage("getVGain() channel=%s value=%s"%(channel,val), self.DEBUG)
        return val
    
    @handleError
    def caSetVGain(self, channel, param):
        if self.caGetRange(channel) != "AUTO":
            self.logMessage("setVGain() channel=%s "%channel, self.INFO)
            self._dSPI.caSetVGain(channel-1, param)
        else:
            self.logMessage("setVGain() Not possible to change VGain when range is in AUTO inchannel=%s "%channel, self.ERROR)

        self.saveUserData(item='cavgain', idx=channel, data=param)             

    @handleError
    def caGetTIGain(self, channel):
        val = self._dSPI.caGetTIGain(channel-1)
        self.logMessage("getTIGain() channel=%s value=%s"%(channel,val), self.DEBUG)
        return val
    
    @handleError
    def caSetTIGain(self, channel, param):
        if self.caGetRange(channel) != "AUTO":
            self.logMessage("setTIGain() channel=%s "%channel, self.INFO)
            self._dSPI.caSetTIGain(channel-1, param)
        else:
            self.logMessage("setVGain() Not possible to change VGain when range is in AUTO inchannel=%s "%channel, self.ERROR)
        
        self.saveUserData(item='catigain', idx=channel, data=param)             
        
    @handleError
    def caGetOffset(self, channel):
        val = self._dSPI.caGetOffset(channel-1)
        self.logMessage("caGetOffset() channel=%s value=%s"%(channel,str(val)), self.DEBUG)
        return val
    
    @handleError
    def caSetOffset(self, channel, param):
        self.logMessage("caSetOffset() channel=%s "%channel, self.INFO)
        self._dSPI.caSetOffset(channel-1, param)        

        self.saveUserData(item='caoffset', idx=channel, data=param)             
        
    def caSetSaturationMax(self, channel, param):
        value =float(param)
        if value >=0 and value <= 100:
            self.logMessage("caSetSaturationMax() channel=%s saturation max.=%s"%(str(channel),str(value)), self.INFO)
            self._caRange_satlimits[channel-1][0] = value
            if self._caRange_autoTh[channel-1] is not None:
                maxlim = self._caRange_satlimits[channel-1][0]
                minlim = self._caRange_satlimits[channel-1][1]
                self._caRange_autoTh[channel-1].setSaturationLimits(maxlim,minlim)            
        else:
            self.logMessage("caSetSaturationMax() Satruration value %s not allowed for channel %s"%(str(param),str(channel)), self.ERROR)

        self.saveUserData(item='casaturationmax', idx=channel, data=param)             

    def caGetSaturationMax(self, channel):
        value = 0
        try:
            value = round(float(self._caRange_satlimits[channel-1][0]),2)
            self.logMessage("caGetSaturationMax() channel=%s saturation max.=%s"%(str(channel),str(value)), self.DEBUG)
        except Exception, e:
            self.logMessage("caGetSaturationMax() channel=%s failed due to %s"%(str(channel),str(e)), self.ERROR)
        return value

    def caSetSaturationMin(self, channel, param):
        value =float(param)
        if value >=0 and value <= 100:
            self.logMessage("caSetSaturationMin() channel=%s saturation min.=%s"%(str(channel),str(value)), self.INFO)
            self._caRange_satlimits[channel-1][1] = value
            if self._caRange_autoTh[channel-1] is not None:
                maxlim = self._caRange_satlimits[channel-1][0]
                minlim = self._caRange_satlimits[channel-1][1]
                self._caRange_autoTh[channel-1].setSaturationLimits(maxlim,minlim)            
        else:
            self.logMessage("caSetSaturationMin() Satruration value %s not allowed for channel %s"%(str(param),str(channel)), self.ERROR)

        self.saveUserData(item='casaturationmin', idx=channel, data=param)             

    def caGetSaturationMin(self, channel):
        value = 0
        try:
            value = round(float(self._caRange_satlimits[channel-1][1]),2)
            self.logMessage("caGetSaturationMin() channel=%s saturation min.=%s"%(str(channel),str(value)), self.DEBUG)
        except Exception, e:
            self.logMessage("caGetSaturationMin() channel=%s failed due to %s"%(str(channel),str(e)), self.ERROR)
        return value

    @handleError
    def setVAnalog(self, channel, value):
        try:
            dac_gain = self.getDACGain()
            dac_value = None
            value = float(value)
            if dac_gain == 0:
                if value >= 0 and value <= 10:
                    dac_value = int(65535 * (1 - (value/10.)))
                else:
                    self.logMessage("setVAnalog() channel=%s Incorrect voltage value (0,10)V input=%s"%(str(channel),str(value)), self.ERROR)
                    return
            else:
                if value >= -10 and value <= 10:
                    dac_value = int(65535/20. * (10 - value))
                else:
                    self.logMessage("setVAnalog() channel=%s Incorrect voltage value (-10,10)V input=%s"%(str(channel),str(value)), self.ERROR)
                    return
                
            if dac_value is not None:
                self._dDAC.setDAC(channel-1, dac_value)
                self.logMessage("setVAnalog() Channel=%s Voltage=%s DAC Value=%s"%(str(channel),str(value),str(dac_value)), self.INFO)

            self.saveUserData(item='vanalog', idx=channel, data=value)             
        except Exception, e:
            self.logMessage("setVAnalog() channel=%s failed due to %s"%(str(channel),str(e)), self.ERROR)
        
    
    @handleError
    def getVAnalog(self, channel):
        ret_value = None
        try:
            dac_gain = self.getDACGain()
            dac_value = self._dDAC.getDAC(channel-1)
            
            if dac_gain == 0:
                ret_value = round(10 * (1 - (dac_value/65535.)),1)
            else:
                ret_value = round(10 - ((20/65535.) * dac_value),1)
            self.logMessage("getVAnalog() Channel=%s Voltage=%s"%(str(channel),str(ret_value)), self.DEBUG)
        except Exception, e:
            self.logMessage("getVAnalog() channel=%s failed due to %s"%(str(channel),str(e)), self.ERROR)        
        
        return ret_value
    
    @handleError
    def setDACGain(self, value):
        self.logMessage("setDACGain() Gain Set=%s "%str(value), self.INFO)
        self._dSPI.feSetDACGain((int(value)&0x01))
        self.saveUserData(item='dacgain', data=value)             
    
    @handleError
    def getDACGain(self):
        val = self._dSPI.feGetDACGain()
        self.logMessage("getDACGain() Gain=%s"%str(val), self.DEBUG)
        return val
    
    def setAOutFn(self, channel, args):
        if self.isAcquiring():
            self.logMessage("setAOutFn() Set function not allowed when acquiring", self.ERROR)
            return
        
        args = str(args).split(",")
        amplitude = self.getVAnalog(channel)
        mode = 0
        frequency = 1
        periodic = True
        matrix = []
        
        for i in range(0, len(args)):
            val = args[i]
            if i == 0:
                mode = int(val)
            elif i == 1:
                amplitude = float(val)
            elif i == 2:
                frequency = float(val)
            elif i == 3:
                periodic = int(val)
            else:
                matrix.append(float(val))
        
        self.logMessage("setAOutFn() Start fn generation output on AOut%s, mode=%s, amplitude=%s, frequency=%s, periodic=%s "%(str(mode), str(channel),str(amplitude), str(frequency),bool(periodic)), self.INFO)

        channel_params = {0: [self._dFIFO_1, _FIFO_ID_1, 'ID_1'],
                        1: [self._dFIFO_2, _FIFO_ID_2, 'ID_2'],
                        2: [self._dFIFO_3, _FIFO_ID_3, 'ID_3'],
                        3: [self._dFIFO_4, _FIFO_ID_4, 'ID_4'],
                        }
        try:
            FIFO_dev = channel_params[channel-1][0]
            FIFO_id = channel_params[channel-1][1]
            DAC_chan = channel_params[channel-1][2]
        except:
            self.logMessage("setAOutFn() Incorrect channel number %s"%str(channel), self.ERROR)
            return

        if mode == 0:
            self._dDAC.writeAttribute(DAC_chan, 0x00)
            self._dIDGEN.writeAttribute('ID_GEN_CTL_ETI', 0x00)
            self.logMessage("setAOutFn() fn generation stopped", self.INFO)            
            
            self.setVAnalog(channel, amplitude)
        else:
            def convertMatrix(dac_gain=0, amplitude=10.0, matrix=[]):
                tmp_matrix = []
                for value in matrix:
                    tmp_value = 0
                    
                    if (dac_gain == 0):
                        value = (value * (amplitude/2)) + (amplitude/2)
                        if (value >= 0 and value <= 10):
                            tmp_value = int(65535 * (1 - (value/10.)))
                    else:
                        value = (value * amplitude)
                        if (value >= -10 and value <= 10):
                            tmp_value = int(65535/20. * (10 - value))
                    tmp_value = (tmp_value<<16) & 0xFFFF0000
                    
                    tmp_matrix.append(tmp_value)
                    
                return tmp_matrix
            
            if mode == 1:
                # SIN 
                points = 40
                matrix = [math.sin(2*math.pi*i/(points)) for i in range(0,points)]
            elif mode == 2: 
                # Pulse
                matrix = [1, -1]
            else:
                # User function
                if len(matrix) == 0:
                    self.logMessage("setAOutFn() User matrix data not provided", self.ERROR)
                    return

            # 1- Fill the FIFO with the ndata_points - 1
            matrix = convertMatrix(self.getDACGain(),amplitude, matrix)
            fifo_data = matrix[:-1]
            last_data = matrix[-1]

            FIFO_dev.writeAttribute('MEM_CTL_ID_OUT', 0x00)
            FIFO_dev.writeAttribute('FIFO_SIZE_SIZE', len(fifo_data)-1)
            FIFO_dev.writeAttribute('MEM_CTL_ID_IN', _TEMPORAL_ID)
            
            self._dIDGEN.writeAttribute('WAIT_TIME', 0x00)  
            self._dIDGEN.writeAttribute('TS_ID_ID_OUT', _TEMPORAL_ID)
            self._dIDGEN.writeAttribute('ID_GEN_CTL_DSRC', 0x00)            
            
            for i in range(0, len(fifo_data)):
                self._dIDGEN.writeAttribute('DATA_GEN_DATA', int(fifo_data[i]))
                self._dIDGEN.writeAttribute('TS_ID_TIMESTAMP', i)

                self._dIDGEN.writeAttribute('ID_GEN_CTL_MTRIG', 0x01)

            self._dIDGEN.writeAttribute('TS_ID_ID_OUT', 0x00)
            
            # 2- Configure FIFO out
            FIFO_dev.writeAttribute('MEM_CTL_ID_OUT', FIFO_id)
            FIFO_dev.writeAttribute('MEM_CTL_ID_IN', _IDGEN_ID)
            
            # 3- Confiure DAC out
            self._dDAC.writeAttribute('CFG_WCH', channel)
            self._dDAC.writeAttribute('CFG_WVALUE', last_data)            
            self._dDAC.writeAttribute('CFG_WR',0x01)                        
            self._dDAC.writeAttribute(DAC_chan,FIFO_id)
            self._dDAC.writeAttribute('CFG_RST',0x01)
            
            # 4- Configure IDGEN
            self._dIDGEN.writeAttribute('DATA_GEN_DATA', last_data)
            self._dIDGEN.writeAttribute('TS_ID_ID_OUT', _IDGEN_ID)
            self._dIDGEN.writeAttribute('ID_GEN_CTL_TRIGGERID', FIFO_id)
            
            if periodic != 0:
                self._dIDGEN.writeAttribute('ID_GEN_CTL_DSRC', 0x01)
            else:
                self._dIDGEN.writeAttribute('ID_GEN_CTL_DSRC', 0x00)
                
            wait_time = int(1/(frequency*1024.*len(matrix)*1E-9))
            self._dIDGEN.writeAttribute('WAIT_TIME', wait_time)
            self._dIDGEN.writeAttribute('ID_GEN_CTL_RST', 0x01)
            
            # 5- Start
            self._dIDGEN.writeAttribute('ID_GEN_CTL_ETI', 0x01)
            self._dIDGEN.writeAttribute('ID_GEN_CTL_MTRIG', 0x01)
            
            self.logMessage("setAOutFn() fn generation started on AOut %s with wait_time=%s"%(str(channel),str(wait_time)), self.INFO)            
            
    @handleError
    def fpgaGetDeviceList(self):
        self.logMessage("fpgaGetDeviceList()", self.DEBUG)
        ret_val = self._dFPGA.getDevices()
        if ret_val is not None:
            return '[%s]' % ', '.join(map(str, ret_val))

    @handleError
    def fpgaReadRegister(self):
        value = None
        try:
#            device = param.split(",")[0]
#            num = param.split(",")[1]
#            attribute = param.split(",")[2]
            value = self._dFPGA.readFPGARegister(self.device, self.num, self.attribute)
            self.logMessage("fpgaReadRegister() Device:%s number:%s register:%s value=%s"%(self.device, self.num, self.attribute, str(value)), self.DEBUG)
        except Exception, e:
            self.logMessage("fpgaReadRegister() Failed due to %s"%str(e), self.ERROR)
        return value

    @handleError
    def fpgaWriteRegister(self, param):
        self.logMessage("fpgaWriteRegister() %s"%param, self.INFO)
        try:
            self.device = param.split(",")[0]
            self.num = param.split(",")[1]
            self.attribute = param.split(",")[2]
            value = int(param.split(",")[3])
            self._dFPGA.writeFPGARegister(self.device, self.num, self.attribute, value)
        except Exception, e:
            self.logMessage("fpgaWriteRegister() Failed due to %s"%str(e), self.ERROR)
        
    def saveUserData(self, item=None, idx=None, data=None):
        try:
            self._MEMMW.saveUserData(item, idx, data)             
        except:
            pass
        