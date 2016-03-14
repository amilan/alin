 ## @package channel.py 
#    This module defines the list of functions that can be called in a channel
#
#    Author = "Manolo Broseta"
#    Copyright = "Copyright 2016, ALBA"
#    Version = "1.0"
#    Email = "mbroseta@cells.es"
#    Status = "Development"
#    History:
#    27/01/2016 - file created

__author__ = "Manolo Broseta"
__copyright__ = "Copyright 2016, ALBA"
__license__ = "GPLv3 or later"
__version__ = "1.0"
__email__ = "mbroseta@cells.es"
__status__ = "Development"

from alin.drivers.spi import SpiCtrl
from alin.drivers.harmony import Harmony
from alin.base import AlinLog

class ChannelClass():
    __CHANNELS_LIST = [{'name':'CHNA', 'chvalue':0, 'adc_name':'ADC_CH1'},
                       {'name':'CHNB', 'chvalue':1, 'adc_name':'ADC_CH2'},
                       {'name':'CHNC', 'chvalue':2, 'adc_name':'ADC_CH3'},
                       {'name':'CHND', 'chvalue':3, 'adc_name':'ADC_CH4'},
                       ]
    
    def __init__(self, parent=None):
        self._parent = parent
        
        self._funct_list = [[]]*len(self.__CHANNELS_LIST)
        
        for idx, channel in enumerate(self.__CHANNELS_LIST):
            name = channel['name']
            ch_val = channel['chvalue']
            adcName = channel['adc_name']
                        
            chCL = ChannelSpecificClass(self._parent, name=name, value=ch_val, adcName=adcName)
            self._funct_list[idx] = chCL.getSCPIFunctionList()

    def getNumChannels(self):
        return len(self.__CHANNELS_LIST)
    
    def getChannelName(self, channel):
        return self.__CHANNELS_LIST[channel]['name']

    def getSCPIFunctionList(self, channel):
        return self._funct_list[channel]
    

class ChannelSpecificClass():
    def __init__(self, parent=None, name='', value =None, adcName=''):
        self._parent = parent
        
        self._ch_name = name
        self._ch_value = value
        self._ch_adc_name = adcName

        self._ch_hmny_device = None
        self._ch_spi_device = None
                
        self._dev_list = self._parent.getDeviceList()
        if self._dev_list is not None and self._dev_list != []:
            for dev in self._dev_list:
                if dev['name'] == 'HARMONY': 
                    self._ch_hmny_device = dev['pointer']
                elif dev['name'] == 'SPI':
                    self._ch_spi_device = dev['pointer']
        
        self._log = self._parent.getLogDevice()

        self._funct_list = [{'command':'name', 
                             'component':None,
                             'fread':self.getName,
                             'fwrite':None,
                             'default':False,
                             },
                            {'command':'chvalue',
                             'component':None,
                             'fread':self.getChValue,
                             'fwrite':None,
                             'default':False,
                             },
                            {'command':'inscurrent',
                             'component':None,
                             'fread':self.getInstantCurrent,
                             'fwrite':None,
                             'default':True,
                             },
                            {'command':'avgcurrent',
                             'component':None,
                             'fread':self.getAverageCurrent,
                             'fwrite':None,
                             'default':False,
                             },
                            {'command':'current',
                             'component':None,
                             'fread':self.getCurrent,
                             'fwrite':None,
                             'default':False,
                             },
                            {'command':'tgrange',
                             'component':None,
                             'fread':self.getHrmyRange,
                             'fwrite':self.setHrmyRange,
                             'default':False,
                             },                            
                            {'command':'tgrun',
                             'component':None,
                             'fread':self.getSWTrigger,
                             'fwrite':self.setSWTrigger,
                             'default':False,
                             },                            
                            {'command':'tgtime',
                             'component':None,
                             'fread':self.getTriggerTime,
                             'fwrite':self.setTriggerTime,
                             'default':False,
                             },
                            {'command':'temp',
                             'component':'cabo',
                             'fread':self.caTemp,
                             'fwrite':None,
                             'default':False,
                             },
                            {'command':'init',
                             'component':'cabo',
                             'fread':self.caGetInit,
                             'fwrite':self.caSetInit,
                             'default':False,
                             },
                            {'command':'filter',
                             'component':'cabo',
                             'fread':self.getFilter,
                             'fwrite':self.setFilter,
                             'default':False,
                             },
                            {'command':'postfilter',
                             'component':'cabo',
                             'fread':self.getPostFilter,
                             'fwrite':self.setPostFilter,
                             'default':False,
                             },
                            {'command':'prefilter',
                             'component':'cabo',
                             'fread':self.getPreFilter,
                             'fwrite':self.setPreFilter,
                             'default':False,
                             },
                            {'command':'inversion',
                             'component':'cabo',
                             'fread':self.getInversion,
                             'fwrite':self.setInversion,
                             'default':False,
                             },
                            {'command':'range',
                             'component':'cabo',
                             'fread':self.getRange,
                             'fwrite':self.setRange,
                             'default':False,
                             },
                            {'command':'vgain',
                             'component':'cabo',
                             'fread':self.getVGain,
                             'fwrite':self.setVGain,
                             'default':False,
                             },
                            {'command':'tigain',
                             'component':'cabo',
                             'fread':self.getTIGain,
                             'fwrite':self.setTIGain,
                             'default':False,
                             },
                            ] 
        
                
    def getSCPIFunctionList(self):
        return self._funct_list
                
    def getName(self):
        self._log.logMessage("SCPI::%s::getName()"%self._ch_name, self._log.INFO)
        return self._ch_name
    
    def getChValue(self):
        self._log.logMessage("SCPI::%s::getChValue(): %s"%(self._ch_name,str(self._ch_value)), self._log.INFO)
        return self._ch_value
    
    def getInstantCurrent(self):
        self._log.logMessage("SCPI::%s::getInstantCurrent()"%self._ch_name, self._log.INFO)
        try:
            val = self._ch_hmny_device.getInstantCurrent(self._ch_adc_name)
            self._log.logMessage("SCPI::%s::getInstantCurrent() value=%s"%(self._ch_name,str(val)), self._log.INFO)
        except Exception, e:
            self._log.logMessage("SCPI::%s::getInstantCurrent() ERROR FOUND!! %s"%(self._ch_name,str(e)), self._log.ERROR)
            return 
        return val

    def getCurrent(self):
        self._log.logMessage("SCPI::%s::getCurrent()"%self._ch_name, self._log.INFO)
        try:
            val = self._ch_hmny_device.getCurrent(self._ch_value)
            self._log.logMessage("SCPI::%s::getCurrent() done"%(self._ch_name), self._log.INFO)
        except Exception, e:
            self._log.logMessage("SCPI::%s::getCurrent() ERROR FOUND!! %s"%(self._ch_name,str(e)), self._log.ERROR)
            return 
        return val

    def getAverageCurrent(self):
        self._log.logMessage("SCPI::%s::getAverageCurrent()"%self._ch_name, self._log.INFO)
        try:
            val = self._ch_hmny_device.getAverageCurrent(self._ch_value)
            self._log.logMessage("SCPI::%s::getAverageCurrent() value=%f"%(self._ch_name,val), self._log.INFO)
        except Exception, e:
            self._log.logMessage("SCPI::%s::getAverageCurrent() ERROR FOUND!! %s"%(self._ch_name,str(e)), self._log.ERROR)
            return 
        return val
    
    def setHrmyRange(self, param):
        self._log.logMessage("SCPI::%s::setHrmyRange()"%self._ch_name, self._log.INFO)
        self._ch_hmny_device.setRange(self._ch_value, param)
    
    def getHrmyRange(self):
        self._log.logMessage("SCPI::%s::getHrmyRange()"%self._ch_name, self._log.INFO)
        try:
            val = self._ch_hmny_device.getRange(self._ch_value)
            self._log.logMessage("SCPI::%s::getHrmyRange() value=%d"%(self._ch_name,val), self._log.INFO)
        except Exception, e:
            self._log.logMessage("SCPI::%s::getHrmyRange() ERROR FOUND!! %s"%(self._ch_name,str(e)), self._log.ERROR)
            return 
        return val        
    
    def setTriggerTime(self, param):
        self._log.logMessage("SCPI::%s::setTriggerTime()"%self._ch_name, self._log.INFO)
        self._ch_hmny_device.setTriggerTime(self._ch_value, param)
    
    def getTriggerTime(self):
        self._log.logMessage("SCPI::%s::getTriggerTime()"%self._ch_name, self._log.INFO)
        try:
            val = self._ch_hmny_device.getTriggerTime(self._ch_value)
            self._log.logMessage("SCPI::%s::getTriggerTime() value=%d"%(self._ch_name,val), self._log.INFO)
        except Exception, e:
            self._log.logMessage("SCPI::%s::getTriggerTime() ERROR FOUND!! %s"%(self._ch_name,str(e)), self._log.ERROR)
            return 
        return val        

    def setSWTrigger(self, param):
        self._log.logMessage("SCPI::%s::setSWTrigger() to RUN"%self._ch_name, self._log.INFO)
        self._ch_hmny_device.startSWTrigger(self._ch_value)
        
    def getSWTrigger(self):
        val = self._ch_hmny_device.getSWTrigger(self._ch_value)
        self._log.logMessage("SCPI::%s::getSWTrigger() value=%d"%(self._ch_name,val), self._log.INFO)
        return val
    
    def caSetInit(self, param):
        self._log.logMessage("SCPI::%s::caInit()"%self._ch_name, self._log.INFO)
        self._ch_spi_device.caInit(self._ch_value)
        return

    def caGetInit(self):
        self._log.logMessage("SCPI::%s::caGetInit()"%self._ch_name, self._log.INFO)
        try:
            val = self._ch_spi_device.caGetInit(self._ch_value)
            self._log.logMessage("SCPI::%s::caGetInit() value=%d"%(self._ch_name,val), self._log.INFO)
        except Exception, e:
            self._log.logMessage("SCPI::%s::caGetInit() ERROR FOUND!! %s"%(self._ch_name,str(e)), self._log.ERROR)
            return 
        return val
    
    def caTemp(self):
        self._log.logMessage("SCPI::%s::caTemp()"%self._ch_name, self._log.INFO)
        try:
            val = self._ch_spi_device.caReadTemp(self._ch_value)
            self._log.logMessage("SCPI::%s::caTemp() value=%f"%(self._ch_name,val), self._log.INFO)
        except Exception, e:
            self._log.logMessage("SCPI::%s::caTemp() ERROR FOUND!! %s"%(self._ch_name,str(e)), self._log.ERROR)
            return
        return val
        
    
    def getFilter(self):
        self._log.logMessage("SCPI::%s::getFilter()"%self._ch_name, self._log.INFO)
        try:
            val = self._ch_spi_device.caGetFilter(self._ch_value)
            self._log.logMessage("SCPI::%s::getFilter() value=%s"%(self._ch_name,val), self._log.INFO)
        except Exception, e:
            self._log.logMessage("SCPI::%s::getFilter() ERROR FOUND!! %s"%(self._ch_name,str(e)), self._log.ERROR)
            return 
        return val
        
    def setFilter(self, param):
        self._log.logMessage("SCPI::%s::setFilter()"%self._ch_name, self._log.INFO)
        self._ch_spi_device.caSetFilter(self._ch_value, param)
        
    def getPostFilter(self):
        self._log.logMessage("SCPI::%s::getPostFilter()"%self._ch_name, self._log.INFO)
        try:
            val = self._ch_spi_device.caGetPostFilter(self._ch_value)
            self._log.logMessage("SCPI::%s::getPostFilter() value=%s"%(self._ch_name,val), self._log.INFO)
        except Exception, e:
            self._log.logMessage("SCPI::%s::getPostFilter() ERROR FOUND!! %s"%(self._ch_name,str(e)), self._log.ERROR)
            return 
        return val
    
    def setPostFilter(self, param):
        self._log.logMessage("SCPI::%s::setPostFilter()"%self._ch_name, self._log.INFO)
        self._ch_spi_device.caSetPostFilter(self._ch_value, param)
    
    def getPreFilter(self):
        self._log.logMessage("SCPI::%s::getPreFilter()"%self._ch_name, self._log.INFO)
        try:
            val = self._ch_spi_device.caGetPreFilter(self._ch_value)
            self._log.logMessage("SCPI::%s::getPreFilter() value=%s"%(self._ch_name,val), self._log.INFO)
        except Exception, e:
            self._log.logMessage("SCPI::%s::getPreFilter() ERROR FOUND!! %s"%(self._ch_name,str(e)), self._log.ERROR)
            return 
        return val
    
    def setPreFilter(self, param):
        self._log.logMessage("SCPI::%s::setPreFilter()"%self._ch_name, self._log.INFO)
        self._ch_spi_device.caSetPreFilter(self._ch_value, param)

    def getInversion(self):
        self._log.logMessage("SCPI::%s::getInversion()"%self._ch_name, self._log.INFO)
        try:
            val = self._ch_spi_device.caGetInv(self._ch_value)
            self._log.logMessage("SCPI::%s::getInversion() value=%s"%(self._ch_name,val), self._log.INFO)
        except Exception, e:
            self._log.logMessage("SCPI::%s::getInversion() ERROR FOUND!! %s"%(self._ch_name,str(e)), self._log.ERROR)
            return 
        return val
    
    def setInversion(self, param):
        self._log.logMessage("SCPI::%s::setInversion()"%self._ch_name, self._log.INFO)
        self._ch_spi_device.caSetInv(self._ch_value, int(param))

    def getRange(self):
        self._log.logMessage("SCPI::%s::getRange()"%self._ch_name, self._log.INFO)
        try:
            val = self._ch_spi_device.caGetRange(self._ch_value)
            self._log.logMessage("SCPI::%s::getRange() value=%s"%(self._ch_name,val), self._log.INFO)
        except Exception, e:
            self._log.logMessage("SCPI::%s::getRange() ERROR FOUND!! %s"%(self._ch_name,str(e)), self._log.ERROR)
            return 
        return val
    
    def setRange(self, param):
        self._log.logMessage("SCPI::%s::setRange()"%self._ch_name, self._log.INFO)
        self._ch_spi_device.caSetRange(self._ch_value, param)

    def getVGain(self):
        self._log.logMessage("SCPI::%s::getVGain()"%self._ch_name, self._log.INFO)
        try:
            val = self._ch_spi_device.caGetVGain(self._ch_value)
            self._log.logMessage("SCPI::%s::getVGain() value=%s"%(self._ch_name,val), self._log.INFO)
        except Exception, e:
            self._log.logMessage("SCPI::%s::getVGain() ERROR FOUND!! %s"%(self._ch_name,str(e)), self._log.ERROR)
            return 
        return val
    
    def setVGain(self, param):
        self._log.logMessage("SCPI::%s::setVGain()"%self._ch_name, self._log.INFO)
        self._ch_spi_device.caSetVGain(self._ch_value, param)

    def getTIGain(self):
        self._log.logMessage("SCPI::%s::getTIGain()"%self._ch_name, self._log.INFO)
        try:
            val = self._ch_spi_device.caGetTIGain(self._ch_value)
            self._log.logMessage("SCPI::%s::getTIGain() value=%s"%(self._ch_name,val), self._log.INFO)
        except Exception, e:
            self._log.logMessage("SCPI::%s::getTIGain() ERROR FOUND!! %s"%(self._ch_name,str(e)), self._log.ERROR)
            return 
        return val
    
    def setTIGain(self, param):
        self._log.logMessage("SCPI::%s::setTIGain()"%self._ch_name, self._log.INFO)
        self._ch_spi_device.caSetTIGain(self._ch_value, param)


 
