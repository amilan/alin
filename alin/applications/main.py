 ## @package main.py 
#    Main control module for the Electrometer
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

import scpi
import threading
import os, sys, time

from alin.drivers.display import Display, DisplayDriver
from alin.drivers.spi import SpiCtrl
from alin.drivers.harmony import Harmony

from alin.base import AlinLog, AlinSDB, AlinDevice

from channel import *
from general import *
from displayui import DisplayUIClass
from distutils.sysconfig import get_python_lib

__CONFIG_FILE__ = "Config"
__CONFIG_MASK__ = "MAIN_"

class AlinMainClass():
    DEFAULT_SCPI_PORT = 5025
    DEFAULT_SCPI_AUTOOPEN = True
    DEFAULT_SCPI_LOCAL = True
    
    def __init__(self):
        # Logging
        self._log = AlinLog(debug=True, loggerName='MAIN')
        
        self.mainflag = True
        self.mainprocess_ended = False
        
                # Print Welcome Message
        self.setLogMessage("**************************************", self._log.INFO)
        self.setLogMessage("*                                    *", self._log.INFO)
        self.setLogMessage("*    ALIN MAIN SOFTWARE V %s     *"%version.version(), self._log.INFO)
        self.setLogMessage("*   Wellcome and enjoy the sesion!   *", self._log.INFO)
        self.setLogMessage("*                                    *", self._log.INFO)
        self.setLogMessage("**************************************", self._log.INFO)

        self._debug = True
        self._debuglevel = 10
        self._scpiport = self.DEFAULT_SCPI_PORT
        self._scpiautoopen = self.DEFAULT_SCPI_AUTOOPEN
        self._scpilocal = self.DEFAULT_SCPI_LOCAL
        self._scpi_debug = self._debug
        # Get default configuration from config file
        self.getConfigData()
        
        self._device_list = [{'name':'DISPLAY',
                             'class':Display,
                             'pointer':None
                             },
                             {'name':'HARMONY',
                             'class':Harmony,
                             'pointer':None
                             },
                             {'name':'SPI',
                             'class':SpiCtrl,
                             'pointer':None
                             },
                             ]
        
        # Connect & start devices
        self.connectDevices()
        self.startDevices()

        self.setLogDebugLevel(self._debuglevel)
        self._log.logEnable(self._debug)
        
        # Creates Panel Thread & Start it
        self._display = DisplayUIClass(self, debug=self._debug)
        self._display.start()

        # Create communication SCPI
        self.startSCPI()
        
    def __del__(self):
        self.mainflag = False
        while not self.mainprocess_ended:
            self.setLogMessage("Waiting Main process to fininsh", self._log.INFO)

        self.setLogMessage("Stopping SCPI", self._log.INFO)
        self.stopSCPI()
        
        self._display.end()
        while not self._display.getProcessEnded():
            pass

        # Stop devices
        self.setLogMessage("Stopping devices", self._log.INFO)
        self.stopDevices()

        self.setLogMessage("*** Bye bye cocodrile!!! ***", self._log.INFO)


    def setLogDebugLevel(self, debuglevel):
        if debuglevel is not None and self._log is not None:
            if debuglevel == 0:
                # 0 = DEBUG
                dbg = self._log.DEBUG
            elif debuglevel == 1:
                # 0 = DEBUG
                dbg = self._log.INFO
            elif debuglevel == 2:
                # 0 = DEBUG
                dbg = self._log.WARNING
            elif debuglevel == 3:
                # 0 = DEBUG
                dbg = self._log.ERROR
            elif debuglevel == 4:
                # 0 = DEBUG
                dbg = self._log.CRITICAL
            else:
                # default
                dbg = self._log.INFO
            
            self._log.logLevel(dbg)
    
    def setLogMessage(self, msg, debuglevel):
        if self._log is not None: 
            self._log.logMessage(msg, debuglevel)
    
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
                            self._debuf = True if cm.split("=")[1].lower() == "true" else False
                            self._log.logMessage("%s::getConfigData(): DEBUG set to %s"%(__CONFIG_MASK__, self._debug),self._log.INFO)
                        except Exception, e:
                            self._log.logMessage("%s::getConfigData(): Can't get DEBUG flag %s"%(__CONFIG_MASK__, self._debug, str(e)),self._log.ERROR)
                    elif cm.startswith("DEBUGLEVEL_"):
                        try:
                            self._debuglevel = int(cm.split("=")[1])
                            self._log.logMessage("%s::getConfigData(): DEBUGLEVEL set to %s"%(__CONFIG_MASK__,self._debuglevel),self._log.INFO)
                        except Exception, e:
                            self._log.logMessage("%s::getConfigData(): Can't get DEBUGLEVEL flag %s"%(__CONFIG_MASK__, self._debug, str(e)),self._log.ERROR)
                    elif cm.startswith("SCPI_AUTOOPEN_"):
                        try:
                            self._scpiautoopen = True if cm.split("=")[1].lower() == "true" else False
                            self._log.logMessage("%s::getConfigData(): SCPI_AUTOOPEN_ set to %s"%(__CONFIG_MASK__,self._scpiautoopen),self._log.INFO)
                        except Exception, e:
                            self._log.logMessage("%s::getConfigData(): Can't get SCPI_AUTOOPEN_ flag %s"%(__CONFIG_MASK__, self._debug, str(e)),self._log.ERROR)
                    elif cm.startswith("SCPI_LOCAL_"):
                        try:
                            self._scpilocal = True if cm.split("=")[1].lower() == "true" else False
                            self._log.logMessage("%s::getConfigData(): SCPI_LOCAL_ set to %s"%(__CONFIG_MASK__,self._scpilocal),self._log.INFO)
                        except Exception, e:
                            self._log.logMessage("%s::getConfigData(): Can't get SCPI_LOCAL_ flag %s"%(__CONFIG_MASK__, self._debug, str(e)),self._log.ERROR)
                    elif cm.startswith("SCPI_PORT_"):
                        try:
                            self._scpiport = int(cm.split("=")[1])
                            self._log.logMessage("%s::getConfigData(): SCPI_PORT_ set to %d"%(__CONFIG_MASK__,self._scpiport),self._log.INFO)
                        except Exception, e:
                            self._log.logMessage("%s::getConfigData(): Can't get SCPI_PORT_ %s"%(__CONFIG_MASK__, self._debug, str(e)),self._log.ERROR)
                    elif cm.startswith("SCPI_DEBUG_"):
                        try:
                            self._scpi_debug = True if cm.split("=")[1].lower() == "true" else False
                            self._log.logMessage("%s::getConfigData(): SCPI_DEBUG_ set to %s"%(__CONFIG_MASK__,self._scpi_debug),self._log.INFO)
                        except Exception, e:
                            self._log.logMessage("%s::getConfigData(): Can't get SCPI_DEBUG_ %s"%(__CONFIG_MASK__, self._debug, str(e)),self._log.ERROR)
        
        except Exception, e:
            self._log.logMessage("%s::getConfigData():: Not possible to get config file due to:"%__CONFIG_MASK__,self._log.ERROR)
            self._log.logMessage(str(e),self._log.ERROR)
        
    def connectDevices(self):
        for idx,dev in enumerate(self._device_list):
            try:
                dev_pointer = dev['class'](debug=self._debug)
                self.setLogMessage("connectDevices() %s Object created %s"%(dev['name'],dev_pointer), self._log.DEBUG)
                self._device_list[idx]['pointer'] = dev_pointer
            except Exception, e:
                self.setLogMessage("Failed to create %s device due to: %s"%(dev['name'],str(e)), self._log.ERROR)
                self._device_list[idx]['pointer'] = None
    
    def startDevices(self):
        for dev in self._device_list:
            try:
                if dev['pointer'] != 'DISPLAY':
                    dev['pointer'].start()
                    self.setLogMessage("startDevices() Start device %s"%(dev['name']), self._log.DEBUG)
            except Exception, e:
                self.setLogMessage("Failed to start %s device due to: %s"%(dev['name'],str(e)), self._log.ERROR)
            
    def stopDevices(self):
        for dev in self._device_list:
            try:
                dev['pointer'].stop()
                self.setLogMessage("startDevices() Start device %s"%(dev['name']), self._log.DEBUG)
            except Exception, e:
                self.setLogMessage("Failed to start %s device due to: %s"%(dev['name'],str(e)), self._log.ERROR)
    
    def getDeviceList(self):
        return self._device_list
    
    def getDisplayUIClass(self):
        return self._display

    def getLogDevice(self):
        return self._log
    
    def startSCPI(self): 
        try:
            self._scpiObj = scpi.scpi(local=self._scpilocal, port=self._scpiport, autoOpen=self._scpiautoopen, debug=self._scpi_debug)
            self.setLogMessage("createSCPIObject() Object created %s"%self._scpiObj, self._log.DEBUG)

            # Create classes
            self._general = GeneralClass(self)
            self._channels = ChannelClass(self)
            
            # Build scpi command list
            self._help_cmd_list = ''
            
            
            self.createSCPISystemCommandList()
            self.createSCPISpecialsList()
            self.createSCPIFunctionList()
            
        except Exception, e:
            self.setLogMessage("FAILED TO Create scpi Obj due to: %s"%str(e), self._log.ERROR)
            self._scpiObj = None
    
    def stopSCPI(self): 
        if self._scpiObj is not None:
            self._scpiObj = None
        self.setLogMessage("destroyedSCPIObject %s"%self._scpiObj, self._log.DEBUG)
    
    def createSCPISystemCommandList(self):
        self.scpiAddSpecialCommand('rst',fwrite=self.resetCommand)
        self.scpiAddSpecialCommand('hlp',fread=self.helpCommand)
        self.scpiAddSpecialCommand('sht',fread=self.shutdownCommand)
    
    def createSCPISpecialsList(self):
        specialList = self._general.getSCPISpecialsList()
        
        if specialList is not None and specialList != []:
            for spEl in specialList:
                self.scpiAddSpecialCommand(spEl['command'],fread=spEl['fread'])
    
    def createSCPIFunctionList(self):
        generalList = self._general.getSCPIFunctionList()
        if generalList is not None and generalList != []:
            for spEl in generalList:
                
                if spEl['component'] is not None:
                    compName = spEl['component']
                    attrName = spEl['command']
                    cmd = '%s:%s'%(compName,attrName)
                else:
                    attrName = spEl['command']
                    cmd='%s'%attrName
                    
                self.scpiAddCommand(cmd=cmd, fread=spEl['fread'], fwrite=spEl['fwrite'])

        n_channels = self._channels.getNumChannels()
        if n_channels >0 and n_channels is not None:
            for channel in range(0,n_channels):
                
                baseCompName = self._channels.getChannelName(channel)
                channelList = self._channels.getSCPIFunctionList(channel)
                
                if channelList is not None and channelList != []:
                    for spEl in channelList:
                        if spEl['component'] is not None:
                            compName = spEl['component']
                            attrName = spEl['command']
                            cmd = '%s:%s:%s'%(baseCompName,compName,attrName)
                        else:
                            attrName = spEl['command']
                            cmd = '%s:%s'%(baseCompName,attrName)
                        
                        self.scpiAddCommand(cmd=cmd, fread=spEl['fread'], fwrite=spEl['fwrite'], default=spEl['default'])

                            
    def scpiAddCommand(self,cmd='',fread=None,fwrite=None,default=False):
        self._scpiObj.addCommand(cmd, readcb=fread, writecb=fwrite, default=default)
        self._help_cmd_list += cmd.upper()+"\n"
        self.setLogMessage("scpi general command ==> %s"%cmd.upper(), self._log.DEBUG)

    def scpiAddSpecialCommand(self,cmd='',fread=None,fwrite=None):
        self._scpiObj.addSpecialCommand(cmd, readcb=fread, writecb=fwrite)
        self._help_cmd_list += cmd.upper()+"\n"
        self.setLogMessage("scpi special command ==> %s"%cmd.upper(), self._log.DEBUG)

    def helpCommand(self):
        self.setLogMessage("SCPI - helpCommand()", self._log.DEBUG)
        # Only to test problems
        print self._scpiObj.commands        
        return self._help_cmd_list
    
    def resetCommand(self):
        self.setLogMessage("RESET_COMMAND ==>", self._log.INFO)
        self._display.end()
        while not self._display.getProcessEnded():
            pass

        # Stop devices
        self.stopDevices()
        
        self.setLogMessage("RESET_COMMAND ==> Panel process ended", self._log.INFO)
        self.setLogMessage("RESET_COMMAND ==> Rebooting System...............bye, bye!!", self._log.INFO)
        self.setLogMessage("***********************************************************", self._log.INFO)

        # restart system
        os.system('reboot -f -t 0')

    def shutdownCommand(self):
        self.setLogMessage("SHUTDOWN_COMMAND ==>", self._log.INFO)
        self._display.end()
        while not self._display.getProcessEnded():
            pass
        
        # Stop devices
        self.stopDevices()
        
        self.setLogMessage("SHUTDOWN_COMMAND ==> Panel process ended", self._log.INFO)
        self.setLogMessage("SHUTDOWN_COMMAND ==> Shuting System...............bye, bye!!", self._log.INFO)
        self.setLogMessage("***********************************************************", self._log.INFO)

        # restart system
        os.system('shutdown -f -t o')

    
    def start(self):
        while (self.mainflag):
            pass
        
        self.mainprocess_ended = True

if __name__ == "__main__":
    Work = AlinMainClass()
    sys.exit(Work.start())