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

from alin.base import AlinDevice
from alin.base import AlinLog
from alin.base import AlinSDB
from alin.base import getConfigData
from alin.base import version

from alin.applications.diagnostics import Diagnostics
from alin.applications.display import Display
from alin.applications.harmony import Harmony
from alin.applications.mem import MemoryMW
from alin.applications.psb import Psb
from alin.applications.scpiapp import ScpiApp
from alin.applications.webserver import WebServer

import os
import select
import sys

_CONFIG_MASK = "MAIN_"

class AlinMainClass():
    def __init__(self):
        # Logging
        self._log = AlinLog(debug=True, loggerName='MAIN   ')
        
        # Get default configuration from config file
        configDict = getConfigData(_CONFIG_MASK)
        self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else debug
        self._debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 40
        
        self.mainflag = True
        self.mainprocess_ended = False
        
        self.main_version = version.version()
        
        # Print Welcome Message
        self.setLogMessage("", self._log.INFO)
        self.setLogMessage("**************************************", self._log.INFO)
        self.setLogMessage("*                                    *", self._log.INFO)
        self.setLogMessage("*    ALIN MAIN SOFTWARE V %s     *"%self.main_version, self._log.INFO)
        self.setLogMessage("*   Wellcome and enjoy the sesion!   *", self._log.INFO)
        self.setLogMessage("*                                    *", self._log.INFO)
        self.setLogMessage("**************************************", self._log.INFO)
        self.setLogMessage("", self._log.INFO)
        
        self.setLogDebugLevel(self._debuglevel)
        self._log.logEnable(self._debug)

        # Initializes and Start Applications
        self.startApplications()
        
        self.setLogMessage("__init__() Initialized ", self._log.INFO)
        
    def __del__(self):
        self.mainflag = False
        while not self.mainprocess_ended:
            self.setLogMessage("Waiting Main process to fininsh", self._log.INFO)

        # Ends applications
        self.EndApplications()
        
        self.setLogMessage("*** Bye bye cocodrile!!! ***", self._log.INFO)
        self.setLogMessage("***********************************************************", self._log.INFO)


    def setLogDebugLevel(self, debuglevel):
        if debuglevel is not None and self._log is not None:
            if debuglevel == 10:
                # 0 = DEBUG
                dbg = self._log.DEBUG
            elif debuglevel == 20:
                # 0 = DEBUG
                dbg = self._log.INFO
            elif debuglevel == 30:
                # 0 = DEBUG
                dbg = self._log.WARNING
            elif debuglevel == 40:
                # 0 = DEBUG
                dbg = self._log.ERROR
            elif debuglevel == 50:
                # 0 = DEBUG
                dbg = self._log.CRITICAL
            else:
                # default
                dbg = self._log.INFO
            
            self._log.logLevel(dbg)
    
    def setLogMessage(self, msg, debuglevel):
        if self._log is not None: 
            self._log.logMessage(msg, debuglevel)
            
    def startApplications(self):
        self._applications = {'PSB':         {'class':Psb,'pointer':None},
                             'DISPLAY':     {'class':Display,'pointer':None},
                             'HARMONY':     {'class':Harmony, 'pointer':None},
                             'DIAGNOSTICS': {'class':Diagnostics, 'pointer':None},
                             'MEMORY_APP':  {'class':MemoryMW, 'pointer':None},
                             'SCPI_APP':    {'class':ScpiApp,'pointer':None},
                             'WEBSERVER':   {'class':WebServer, 'pointer':None},
                             }
        
        powerup_order = ['PSB','HARMONY','DIAGNOSTICS', 'MEMORY_APP', 'DISPLAY', 'SCPI_APP', 'WEBSERVER']

        for key in powerup_order:
            el = self._applications[key]
            try:
                dev_pointer = el['class'](debug=self._debug)
                self._applications[key]['pointer'] = dev_pointer
                
                self.setLogMessage("InitializeApplications() %s Object created%s"%(key,dev_pointer), self._log.INFO)
            except Exception, e:
                self.setLogMessage("Failed to create Applications %s device due to: %s"%(key,str(e)), self._log.ERROR)
                self._applications[key]['pointer'] = None
                
        for key in powerup_order:
            el = self._applications[key]
            try:
                el['pointer'].shareApplications(self._applications)
                el['pointer'].start()
                
                self.setLogMessage("InitializeApplications() shared middleware table and start %s"%key, self._log.INFO)
            except Exception, e:
                self.setLogMessage("Failed to share Applications %s device due to: %s"%(key,str(e)), self._log.WARNING)
    
    def stopApplications(self):
        for key, el in self._applications.iteritems():
            try:
                el['pointer'].stop()
                self.setLogMessage("EndApplications() Applications ended %s"%key, self._log.INFO)
            except Exception, e:
                self.setLogMessage("Failed to end Applications %s device due to: %s"%(key,str(e)), self._log.ERROR)
    
    def start(self):
        self._end_type = 'NORMAL'
        try:
            while (self.mainflag):
                pass
        except KeyboardInterrupt:
            self.mainflag = False
        
        # Ends Applications
        self.stopApplications()

        self.setLogMessage("*** Bye bye cocodrile!!! ***", self._log.INFO)
        self.setLogMessage("***********************************************************", self._log.INFO)

        self.mainprocess_ended = True
        if self._end_type == 'REBOOT':
            # Reboot system
            os.system('/sbin/shutdown -f -r now')
        elif self._end_type == 'SHUTDOWN':
            os.system('/sbin/shutdown -f now')
        else:
            pass
        sys.exit(-1)

    def end(self, type='NORMAL'):
        self.mainflag = False
        
        self._end_type = type

if __name__ == "__main__":
    Work = AlinMainClass()
    sys.exit(Work.start())