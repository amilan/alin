## @package main.py 
#    Main control module the display thread
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

from alin.drivers.display import Display
from alin.base import AlinLog


class DisplayUIClass(threading.Thread):
    def __init__(self, parent=None, debug=None):
        threading.Thread.__init__(self)
        
        self._parent = parent
        
        self._waitSemaphore = False
        self._endProcess = False
        self._processEnded = False
        self._started = False
        self._display_control = True
        
        self._display = None
        self._dev_list = self._parent.getDeviceList()
        if self._dev_list is not None and self._dev_list != []:
            for dev in self._dev_list:
                if dev['name'] == 'DISPLAY': 
                    self._display = dev['pointer']

    def setSemaphore(self,val):
        self._waitSemaphore = val
        
    def end(self):
        if self._display is not None:
             self._display.stopDisplay()
        self._endProcess = True
        
    def getProcessEnded(self):
        return self._processEnded

    def getDisplayStarted(self):
        return self._display_control
    
    def startDisplay(self):
        if self._display is not None:
            self._waitSemaphore = False
            self._endProcess = False
            self._processEnded = False
            self._display_control = True
        
            self._display.start()

    def stopDisplay(self):
        if self._display is not None:
             self._display.stopDisplay()
        self._display_control = False


    def run(self): 
        if self._display is not None:
            self._started = True
            while not (self._endProcess):
                if self._display_control:
                    #process touch display
                    self._display.processData()
                    
                    # Refresh screen parameters
                    self._display.logoRefreshControl()
                
                time.sleep(1)
        
        self._processEnded = True
        self._started = False
