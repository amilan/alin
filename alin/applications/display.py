# Panel programme
#
# Created: March 2015
#      by: Manolo Broseta at ALBA Computing Division
#


from alin.base import AlinLog
from alin.base import getConfigData
from alin.base import version

from alin.drivers.edip128 import EDIP128
from alin.drivers.image_res import *

from alin.applications.harmony import Harmony

import math
import os
import scpi
import socket
import sys
import threading
import time

from uuid import getnode as get_mac

_CONFIG_MASK = "DISPLAY_"

_DC1_BYTE = 0x11
_DC2_BYTE = 0x12

_DATA_LEN = 32

_ACTION_NEXT = "next"
_ACTION_PREVIOUS = "previous"
_ACTION_I1 ="I1"
_ACTION_I2 ="I2"
_ACTION_I3 ="I3"
_ACTION_I4 ="I4"
_ACTION_RANGE = "range"
_ACTION_FILTER = "filter"
_ACTION_OP1 = "OP1"
_ACTION_OP2 = "OP2"
_ACTION_OP3 = "OP3"
_ACTION_OP4 = "OP4"
_ACTION_OP5 = "OP5"
_ACTION_OP6 = "OP6"
_ACTION_OP7 = "OP7"
_ACTION_OP8 = "OP8"
_ACTION_OP9 = "OP9"

_PREVIOUS_X_INIT    = 1
_PREVIOUS_Y_INIT    = 54
_PREVIOUS_X_END     = 63
_PREVIOUS_Y_END     = 64

_NEXT_X_INIT        = 66
_NEXT_Y_INIT        = 54
_NEXT_X_END         = 126
_NEXT_Y_END         = 64

class Display(AlinLog):
    def __init__(self, debug=False):
        AlinLog.__init__(self, debug=False, loggerName='DISPLAY')

        # Get default configuration from config file
        self._debug = debug        
        self.configure()

        self._dDISP = EDIP128()
        self._dDISP.SetProtocol(32,10)
        self._dDISP.GetData()
        self._HRMY = None
        self._DIAGS = None

        self.panel_brightness = 0
        self.panel_illumination = False
        
        self._menus = {"LOGO": {'function': self.showLogo,
                                'actions': {_ACTION_PREVIOUS:"SCREEN_7",
                                            _ACTION_NEXT:"MAIN_SCREEN",
                                           }
                                },
                        "MAIN_SCREEN": {'function': self.showMainScreen,
                                     'actions': {_ACTION_PREVIOUS:"SYSTEM_SETTINGS",
                                                 _ACTION_NEXT:"STATUS",
                                                 _ACTION_I1:"CHANNEL_SETTINGS",
                                                 _ACTION_I2:"CHANNEL_SETTINGS",
                                                 _ACTION_I3:"CHANNEL_SETTINGS",
                                                 _ACTION_I4:"CHANNEL_SETTINGS",
                                                 }
                                    },
                        "CHANNEL_SETTINGS": {'function': self.showChannelSettingsScreen,
                                     'actions': {_ACTION_PREVIOUS:"MAIN_SCREEN",
                                                 _ACTION_RANGE:"CHANGE_RANGE",
                                                 _ACTION_FILTER:"CHANGE_FILTER",
                                                 }
                                    },
                        "CHANGE_RANGE": {'function': self.showChangeRangeScreen,
                                     'actions': {_ACTION_PREVIOUS:"CHANNEL_SETTINGS",
                                                _ACTION_OP1:"CHANGE_RANGE",
                                                _ACTION_OP2:"CHANGE_RANGE",
                                                _ACTION_OP3:"CHANGE_RANGE",
                                                _ACTION_OP4:"CHANGE_RANGE",
                                                _ACTION_OP5:"CHANGE_RANGE",
                                                _ACTION_OP6:"CHANGE_RANGE",
                                                _ACTION_OP7:"CHANGE_RANGE",
                                                _ACTION_OP8:"CHANGE_RANGE",
                                                _ACTION_OP9:"CHANGE_RANGE",
                                                 }
                                    },
                        "CHANGE_FILTER": {'function': self.showChangeFilterScreen,
                                     'actions': {_ACTION_PREVIOUS:"CHANNEL_SETTINGS",
                                                _ACTION_OP1:"CHANGE_FILTER",
                                                _ACTION_OP2:"CHANGE_FILTER",
                                                _ACTION_OP3:"CHANGE_FILTER",
                                                _ACTION_OP5:"CHANGE_FILTER",
                                                _ACTION_OP6:"CHANGE_FILTER",
                                                 }
                                    },
                        "SYSTEM_SETTINGS": {'function': self.showSystemSettingsScreen,
                                     'actions': {_ACTION_PREVIOUS:"STATUS",
                                                 _ACTION_NEXT:"MAIN_SCREEN",
                                                 }
                                    },
                        "STATUS": {'function': self.showStatusScreen,
                                     'actions': {_ACTION_PREVIOUS:"MAIN_SCREEN",
                                                 _ACTION_NEXT:"SYSTEM_SETTINGS",
                                                 }
                                    },                        
                        "TEST_CALIBRATION": {'function': self.showTestCalibrationScreen,
                                     'actions': {_ACTION_PREVIOUS:"MAIN_SCREEN",
                                                 _ACTION_NEXT:"MAIN_SCREEN",
                                                 }
                                    },                                                
                        }
                        
        # Define the action window for the navigations keya as [xinitpos, yinitpos, xfinalpos, yfinalpos]
        self._action_window = {_ACTION_PREVIOUS: [_PREVIOUS_X_INIT, _PREVIOUS_Y_INIT, _PREVIOUS_X_END, _PREVIOUS_Y_END],
                               _ACTION_NEXT:[_NEXT_X_INIT, _NEXT_Y_INIT, _NEXT_X_END, _NEXT_Y_END],
                               _ACTION_I1:[1, 8, 63, 28],
                               _ACTION_I2:[66, 8, 126, 28],
                               _ACTION_I3:[1, 30, 63, 50],
                               _ACTION_I4:[66, 30, 126, 50],
                               _ACTION_RANGE:[1, 25, 63, 45],
                               _ACTION_FILTER:[66, 25, 126, 45],
                               _ACTION_OP1: [5,22,44,31],
                               _ACTION_OP2: [45,22,84,31],
                               _ACTION_OP3: [80,22,123,31],
                               _ACTION_OP4: [5,32,44,41],
                               _ACTION_OP5: [45,32,84,41],
                               _ACTION_OP6: [85,32,123,41],
                               _ACTION_OP7: [5,42,49,51],
                               _ACTION_OP8: [45,42,84,51],
                               _ACTION_OP9: [85,42,123,51],
                               }

        self._current_menu = "MAIN_SCREEN"
        self._previous_menu = "MAIN_SCREEN"
        self.displayed_logo = False
        
        self._nav_key_pressed = False
        self._back_key = False
        self._channel_sel = _ACTION_I1
        
        self._host = 'None'
        self._ipadd = 'None'
        self._ver = 'None'
        self._fw_ver = 'None'
        self._mac = 'None'
        
        self._hvbias = None
        self._VAnalog = [0 for i in range (0,4)]
        self._ch_data = {'1':{}, '2':{}, '3':{}, '4':{}}
        self._dio_data = {'DIO_1':{'pos':[40,8],'num':'1'},
                          'DIO_2':{'pos':[60,8],'num':'2'},
                          'DIO_3':{'pos':[80,8],'num':'3'},
                          'DIO_4':{'pos':[100,8],'num':'4'}
                          }
        
        #self.start()
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
        self._dDISP.configure()

        self.logMessage("reconfigure(): Done!!", self.INFO)
            
    def start(self):
        self.logMessage("start():", self.INFO)
        
        self._dDISP.ClearScreen()
        self.panelSetBrigtnessIllumination()        
        self.setMenu("LOGO")
        
        try:
            self._dispThread = DisplayThread(self)
            self._dispThread.setDaemon(True)
            self._dispThread.start()
            self.logMessage("start(): Display Started!!", self.INFO)
        except Exception, e:
            self.logMessage("start(): Display not started due to %s"%str(e), self.INFO)        
    
    def stop(self):
        self._dDISP.ClearScreen()
        self._dDISP.SendData('#TC 0')
        self._dDISP.SendData('#ZV 3')
        self._dDISP.SendData('#ZZ 1,2')
        self._dDISP.PanelSettings(bright=70)        
        
        #self._dDISP.DrawImage(40,0,Face_image)

        #self._dDISP.SendData('#ZB 1')
        #self._dDISP.SendData('#ZL 0,20,BYE\n')
        #self._dDISP.SendData('#ZL 10,30,BYE\n')
        #self._dDISP.SendData('#ZL 90,20,BYE\n')
        #self._dDISP.SendData('#ZL 100,30,BYE\n')
        
        self._dDISP.DrawImage(0,0,Alba_logo)
        
        time.sleep(2)
        self._dDISP.SendData('#PD 0,0')        
        self._dDISP.ClearScreen()
        
        if self._dispThread is not None:
            self._dispThread.end()
        
        while not self._dispThread.getProcessEnded():
            self.logMessage("stop(): Waiting process to die", self.INFO)
            time.sleep(0.5)

        self.logMessage("stop(): Display Stopped!!", self.INFO)

    def shareApplications(self, applications):
        self.logMessage("shareApplications(): Getting needed applications layers for the display", self.INFO)

        self._HRMY = applications['HARMONY']['pointer']
        self._DIAGS = applications['DIAGNOSTICS']['pointer']
        self._SCPI = applications['SCPI_APP']['pointer']

    def setMenu(self, menu):
        self._previous_menu = self._current_menu
        if menu in self._menus.keys():
            self._current_menu = menu
            if self._current_menu != self._previous_menu:
                self.logMessage("setMenu(): Display menu current=%s previous=%s"%(self._current_menu,self._previous_menu), self.INFO)
            self._menus[menu]['function']()

    def getMenu(self):
        return self._current_menu
        
    def processData(self):
        ret_value = None
        
        arg = self._dDISP.GetData()
        if arg is not None and len(arg)>0:
            if arg[0] == _DC1_BYTE:
                data_len = arg[1]
                if data_len>0:
                    if self._debug:
                        txt = "I2C_READ_DATA= "
                        for el in arg[2:data_len]:
                            txt += hex(el)+", "
                        self.logMessage(txt, self.DEBUG)
                    
                    if data_len>_DATA_LEN: data_len=_DATA_LEN
                    r_data = [chr(el) for el in arg[2:data_len]]
                    r_data = ''.join(r_data)
                    r_data = r_data.split('\x1b')
                    for data in r_data:
                        try:
                            if data[0] == 'H':
                                if ord(data[2]) == 0x01:
                                    x=0
                                    try:
                                        x = ord(data[3])
                                    except:
                                        pass
                                    y=0
                                    try:
                                        y = ord(data[4])
                                    except:
                                        passmiddleware
                                    self.logMessage("Pressed X=%s Y=%s"%(str(x),str(y)), self.INFO)
                                    ret_value = (x, y)
                                elif ord(data[2]) == 0x00 or ord(data[2]) == 0x02:
                                    #self.PrintReleased()
                                    pass
                        except:
                            pass
        
        return ret_value
        
    def panelSetBrigtnessIllumination(self, bright=100, illumination=True):
        self.logMessage("Panel_set Bright=%s Illumination=%s"%(str(bright),illumination), self.INFO)
        self.panel_brightness = bright
        self.panel_illumination = illumination
        self._dDISP.PanelSettings(self.panel_brightness, self.panel_illumination)
        
        
    def showLogo(self):
        if not self.displayed_logo:
            self.logMessage("showLogo()", self.INFO)
            
            self._dDISP.ClearScreen()
            # Change display orientation
            self._dDISP.SendData('#DO 2')
            # Delete cursor
            self._dDISP.SendData('#TC 0')
            
            # Draw Alba Logo
            self._dDISP.DrawImage(0,0,EM_Logo)
            # Set tocuh screen area
            self._dDISP.SendData('#AH 0,0,127,64')
            self._dDISP.SendData('#AA 0')
            self._dDISP.SendData('#AA 1')

            self.brightness_counter = 0
            
            self.displayed_logo = True
        else:
            # do nothing if:
            # - request to display Logo, but Logo already in screen 
            pass        
        
    def showMainScreen(self):
        self.displayed_logo = False
        first_time_display = False
        if self._previous_menu != self._current_menu:
            self.logMessage("showMainScreen()", self.INFO)
            
            first_time_display = True
            
            self._dDISP.ClearScreen()
            self._nav_key_pressed = True
            self._back_key = False
            self.showNavigationKeys()
            
            self._dDISP. SendData(u'#RM 1,9,63,17,1')
            self.writeLine(msg='I', x_pos=25, y_pos=10, font=2, flash=0, link=5)
            self._dDISP. SendData(u'#RM 65,9,126,17,1')
            self.writeLine(msg='I', x_pos=90, y_pos=10, font=2, flash=0, link=5)
            self.writeLine(msg='"1"', x_pos=31, y_pos=12, font=1, flash=0, link=5)
            self.writeLine(msg='"2"', x_pos=96, y_pos=12, font=1, flash=0, link=5)
            self._dDISP. SendData(u'#RM 1,31,63,39,1')
            self.writeLine(msg='I', x_pos=25, y_pos=32, font=2, flash=0, link=5)
            self._dDISP. SendData(u'#RM 65,31,126,39,1')
            self.writeLine(msg='I', x_pos=91, y_pos=32, font=2, flash=0, link=5)
            self.writeLine(msg='"3"', x_pos=31, y_pos=34, font=1, flash=0, link=5)
            self.writeLine(msg='"4"', x_pos=96, y_pos=34, font=1, flash=0, link=5)

        self.refreshWarningArea()

        _CH_ADDRESS = [(5,20), (70, 20), (5,42), (70,42)]

        for idx, el in enumerate(_CH_ADDRESS):
            x = el[0]
            y = el[1]
            
            try:
                # Display current Value
                value = self._HRMY.getInstantCurrent(idx)
                rangset = self._HRMY.caGetRangeSet(idx+1)
                
                # Refresh range channel data            
                refresh_data = False
                if 'current' not in self._ch_data[str(idx+1)].keys() or self._ch_data[str(idx+1)]['current'] != value or first_time_display:        
                    self._ch_data[str(idx+1)]['current'] = value
                    refresh_data = True
                    
                if refresh_data:
                    # Clear current first
                    self.writeLine(msg="         ", x_pos=x, y_pos=y, font=2, flash=0, link=4)
                    text = self.convertCurrToStringMain(rangset, value)
                    text = '{:>9}'.format(text)
                    self.writeLine(msg=text, x_pos=x, y_pos=y, font=2, flash=0, link=1)
            except:
                passmiddleware
            
    def showChannelSettingsScreen(self):
        channel = self._channel_sel
        self.displayed_logo = False
        first_time_display = False
        if self._previous_menu != self._current_menu:
            self.logMessage("showChannelSettingsScreen()", self.INFO)

            first_time_display = True
            self._dDISP.ClearScreen()
            self._nav_key_pressed = True
            self._back_key = True
            self.showNavigationKeys()

            self.writeLine(msg='I', x_pos=20, y_pos=14, font=2, flash=0, link=1)
            self.writeLine(msg=str(channel+1)+'"\n"', x_pos=26, y_pos=16, font=1, flash=0, link=1)
            self.writeLine(msg='=', x_pos=32, y_pos=14, font=2, flash=0, link=1)
            self._dDISP. SendData(u'#RM 15,26,53,35,1')
            self._dDISP. SendData(u'#RR 15,35,53,46,1')
            self.writeLine(msg='Range', x_pos=20, y_pos=27, font=2, flash=0, link=5)
            self._dDISP. SendData(u'#RM 71,26,113,35,1')
            self._dDISP. SendData(u'#RR 71,35,113,46,1')
            self.writeLine(msg='Filter', x_pos=75, y_pos=27, font=2, flash=0, link=5)

        self.refreshWarningArea()

        value = self._HRMY.getInstantCurrent(channel)
        rang = self._HRMY.caGetRange(channel+1)
        rangset = self._HRMY.caGetRangeSet(channel+1)
        filt = self._HRMY.caGetFilter(channel+1)

        # Refresh range channel data            
        if 'range' not in self._ch_data[str(channel+1)].keys() or self._ch_data[str(channel+1)]['range'] != rang or first_time_display:
            self._ch_data[str(channel+1)]['range'] = rang
            self.writeLine(msg='     ', x_pos=20, y_pos=37, font=2, flash=0, link=4)
            text = '{:>5}'.format(rang)
            self.writeLine(msg=text, x_pos=20, y_pos=37, font=2, flash=0, link=1)
            
        # Refresh filter channel data            
        if 'filter' not in self._ch_data[str(channel+1)].keys() or self._ch_data[str(channel+1)]['filter'] != filt or first_time_display:
            self._ch_data[str(channel+1)]['filter'] = filt
            self.writeLine(msg='      ', x_pos=75, y_pos=37, font=2, flash=0, link=4)
            text = '{:>6}'.format(filt) 
            self.writeLine(msg=text, x_pos=75, y_pos=37, font=2, flash=0, link=1)

        # Refresh current data
        if 'current' not in self._ch_data[str(channel+1)].keys() or self._ch_data[str(channel+1)]['current'] != value or first_time_display:        
            self._ch_data[str(channel+1)]['current'] = value            
            self.writeLine(msg='           ', x_pos=42, y_pos=14, font=2, flash=0, link=4)
            text = self.convertCurrToStringMain(rangset, value, digits=6)
            text = '{:>11}'.format(text)            
            self.writeLine(msg=text, x_pos=42, y_pos=14, font=2, flash=0, link=1)
                
    def showChangeRangeScreen(self):
        channel = self._channel_sel
        first_time_display = False
        self.displayed_logo = False        
        if self._previous_menu != self._current_menu:
            self.logMessage("showChangeRangeScreen()", self.INFO)            

            first_time_display = True
            self._dDISP.ClearScreen()
            self._nav_key_pressed = True
            self._back_key = True
            self.showNavigationKeys()

            self.writeLine(msg='I', x_pos=8, y_pos=14, font=2, flash=0, link=1)
            self.writeLine(msg=str(channel+1)+'"\n"', x_pos=14, y_pos=16, font=1, flash=0, link=1)
            self.writeLine(msg='=', x_pos=20, y_pos=14, font=2, flash=0, link=1)
            self._dDISP. SendData(u'#RM 90,13,119,21,1')
            self.writeLine(msg='Range', x_pos=91, y_pos=14, font=2, flash=0, link=5)

            self._dDISP.SendData(u'#RT 3,22,120,52,1')

        self.refreshWarningArea()

        value = self._HRMY.getInstantCurrent(channel)
        rang = self._HRMY.caGetRange(channel+1)
        rangset = self._HRMY.caGetRangeSet(channel+1)

        if 'range' not in self._ch_data[str(channel+1)].keys() or self._ch_data[str(channel+1)]['range'] != rang or first_time_display:        
            self._ch_data[str(channel+1)]['range'] = rang
            # Draw Range table
            rang_table = [['100pA', 5, 24 ],
                        ['1nA', 45,24  ],
                        ['10nA', 85, 24  ],
                        ['100nA', 5, 34  ],
                        ['1uA', 45, 34  ],
                        ['10uA', 85, 34  ],
                        ['100uA', 5, 44  ],
                        ['1mA', 45, 44  ],
                        ['AUTO', 85, 44  ],
                        ]
                
            for el in rang_table:
                self.writeLine(msg="     ", x_pos=el[1], y_pos=el[2], font=2, flash=0, link=4)
                text = '{:>5}'.format(el[0])
                try:
                    if rang.lower() == el[0].lower():
                        self.writeLine(msg=text, x_pos=el[1], y_pos=el[2], font=2, flash=0, link=5)
                    else:
                        self.writeLine(msg=text, x_pos=el[1], y_pos=el[2], font=2, flash=0, link=1)
                except:
                    self.writeLine(msg=text, x_pos=el[1], y_pos=el[2], font=2, flash=0, link=1)        
                
        # Refresh current data
        if 'current' not in self._ch_data[str(channel+1)].keys() or self._ch_data[str(channel+1)]['current'] != value or first_time_display:   
            self._ch_data[str(channel+1)]['current'] == value
            self.writeLine(msg='         ', x_pos=30, y_pos=14, font=2, flash=0, link=4)
            text = self.convertCurrToStringMain(rangset, value, digits=4)
            text = '{:>9}'.format(text)
            self.writeLine(msg=text, x_pos=30, y_pos=14, font=2, flash=0, link=1)                
        
    def showChangeFilterScreen(self):
        channel = self._channel_sel
        first_time_display = False
        self.displayed_logo = False        
        if self._previous_menu != self._current_menu:
            self.logMessage("showChangeRangeScreen()", self.INFO)            

            first_time_display = True
            self._dDISP.ClearScreen()
            self._nav_key_pressed = True
            self._back_key = True
            self.showNavigationKeys()

            self.writeLine(msg='I', x_pos=8, y_pos=14, font=2, flash=0, link=1)
            self.writeLine(msg=str(channel+1)+'"\n"', x_pos=14, y_pos=16, font=1, flash=0, link=1)
            self.writeLine(msg='=', x_pos=20, y_pos=14, font=2, flash=0, link=1)
            self._dDISP. SendData(u'#RM 87,13,122,21,1')
            self.writeLine(msg='Filter', x_pos=88, y_pos=14, font=2, flash=0, link=5)

            self._dDISP.SendData(u'#RT 2,22,123,42,1')

        self.refreshWarningArea()

        value = self._HRMY.getInstantCurrent(channel)
        rangset = self._HRMY.caGetRangeSet(channel+1)        
        filt = self._HRMY.caGetFilter(channel+1)

        if 'filter' not in self._ch_data[str(channel+1)].keys() or self._ch_data[str(channel+1)]['filter'] != filt or first_time_display:
            self._ch_data[str(channel+1)]['filter'] = filt
            # Draw filter table
            filt_table = [['3200Hz', 5, 24 ],
                        ['100Hz', 45, 24  ],
                        ['10Hz', 85, 24  ],
                        ['1Hz', 45, 34  ],
                        ['0.5Hz', 85, 34  ],
                        ]
            
            for el in filt_table:
                self.writeLine(msg="      ", x_pos=el[1], y_pos=el[2], font=2, flash=0, link=4)
                text = '{:>6}'.format(el[0])
                try:
                    if filt.lower() == el[0].lower():
                        self.writeLine(msg=text, x_pos=el[1], y_pos=el[2], font=2, flash=0, link=5)
                    else:
                        self.writeLine(msg=text, x_pos=el[1], y_pos=el[2], font=2, flash=0, link=1)
                except:
                    self.writeLine(msg=text, x_pos=el[1], y_pos=el[2], font=2, flash=0, link=1)

        # Refresh current data
        if 'current' not in self._ch_data[str(channel+1)].keys() or self._ch_data[str(channel+1)]['current'] != value or first_time_display:        
            self._ch_data[str(channel+1)]['current'] = value
            self.writeLine(msg='         ', x_pos=30, y_pos=14, font=2, flash=0, link=4)
            text = self.convertCurrToStringMain(rangset, value, digits=4)
            text = '{:>9}'.format(text)
            self.writeLine(msg=text, x_pos=30, y_pos=14, font=2, flash=0, link=1)
            
    def showSystemSettingsScreen(self):
        self.displayed_logo = False
        first_time_display = False
        if self._previous_menu != self._current_menu:
            self.logMessage("showSystemSettingsScreen()", self.INFO)            

            first_time_display = True
            self._dDISP.ClearScreen()
            self._nav_key_pressed = True
            self._back_key = False
            self.showNavigationKeys()
            
        self.refreshWarningArea()
        try:
            host = socket.gethostname()
        except:
            host = 'None'

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 0))
            ipadd = s.getsockname()[0]
        except:
            ipadd = 'None'

        ver = version.version()
        
        fw_ver = self._HRMY.getFWVersion()
        
        mac = format(get_mac(), 'x')
        mac_format = ':'.join([mac[i:i+2] for i,j in enumerate(mac) if not (i%2)])

        if self._mac != mac_format or first_time_display:
            self._mac = mac_format
            self.writeLine(msg='                     ', x_pos=1, y_pos=7, font=2, flash=0, link=4)
            self.writeLine(msg='Mac:'+ mac_format, x_pos=1, y_pos=7, font=2, flash=0, link=1)
            
        if self._host != host or first_time_display:
            self._host = host
            self.writeLine(msg='                     ', x_pos=1, y_pos=16, font=2, flash=0, link=4)
            self.writeLine(msg='Host:   '+ host, x_pos=1, y_pos=16, font=2, flash=0, link=1)            
            
        if self._ipadd != ipadd or first_time_display:
            self._ipadd = ipadd
            self.writeLine(msg='                     ', x_pos=1, y_pos=25, font=2, flash=0, link=4)
            self.writeLine(msg='Ip:     '+ ipadd, x_pos=1, y_pos=25, font=2, flash=0, link=1)            

        if self._ver != ver or first_time_display:
            self._ver = ver
            self.writeLine(msg='                     ', x_pos=1, y_pos=35, font=2, flash=0, link=4)
            self.writeLine(msg='SW_Ver: '+ ver, x_pos=1, y_pos=35, font=2, flash=0, link=1)            

        if self._fw_ver != fw_ver or first_time_display:
            self._fw_ver = fw_ver
            self.writeLine(msg='                     ', x_pos=1, y_pos=44, font=2, flash=0, link=4)
            self.writeLine(msg='GW_Ver: '+ fw_ver, x_pos=1, y_pos=44, font=2, flash=0, link=1)            
            
    def showStatusScreen(self):
        self.displayed_logo = False
        first_time_display = False
        if self._previous_menu != self._current_menu:
            self.logMessage("showSystemSettingsScreen()", self.INFO)            

            first_time_display = True
            self._dDISP.ClearScreen()
            self._nav_key_pressed = True
            self._back_key = False
            self.writeLine(msg='HV_BIAS= ', x_pos=1, y_pos=18, font=2, flash=0, link=1)
            self.writeLine(msg='A1=', x_pos=1, y_pos=30, font=2, flash=0, link=1)
            self.writeLine(msg='A3=', x_pos=1, y_pos=40, font=2, flash=0, link=1)
            self.writeLine(msg='A2=', x_pos=65, y_pos=30, font=2, flash=0, link=1)
            self.writeLine(msg='A4=', x_pos=65, y_pos=40, font=2, flash=0, link=1)
            self.showNavigationKeys()
            
        self.refreshWarningArea()
        
        hvbias = self._DIAGS.getFVAverageVoltage()

        
        self.writeLine(msg=' TR ', x_pos=1, y_pos=8, font=1, flash=0, link=5)
        
        for el in self._dio_data.keys():
            dio_num = self._dio_data[el]['num']
            
            cfg = self._HRMY.getGPIOConfig(int(dio_num))
            val = self._HRMY.getGPIOValue(int(dio_num))
            
            x_pos= self._dio_data[el]['pos'][0]
            y_pos= self._dio_data[el]['pos'][1]
            
            refresh_data = False
            if 'config' not in self._dio_data[el].keys() or self._dio_data[el]['config'] != cfg or first_time_display:        
                self._dio_data[el]['config'] = cfg
                refresh_data = True
            
            if 'value' not in self._dio_data[el].keys() or self._dio_data[el]['value'] != val or first_time_display:        
                self._dio_data[el]['value'] = val
                refresh_data = True
                
            if refresh_data:
                text = " DO" if cfg.lower() == 'output' else " DI"
                text = text + dio_num + " "
                link = 5 if val else 1
                self.writeLine(msg='     ', x_pos=x_pos, y_pos=y_pos, font=1, flash=0, link=4)
                self.writeLine(msg=text, x_pos=x_pos, y_pos=y_pos, font=1, flash=0, link=link)
                
        # Refresh HV bias voltage data
        if self._hvbias != hvbias or first_time_display:        
            self._hvbias = hvbias
            self.writeLine(msg='         ', x_pos=54, y_pos=18, font=2, flash=0, link=4)
            text = str(round(self._hvbias, 1)) + " V"
            if self._hvbias >= 0:
                text = "+" + '{:0>6}'.format(str(round(self._hvbias, 1))) + " V"
            else:
                text = "-" + '{:0>6}'.format(str(round(abs(self._hvbias), 1))) + " V"
            text = '{:>9}'.format(text)
            self.writeLine(msg=text, x_pos=54, y_pos=18, font=2, flash=0, link=1) 

        xpos = [22,86,22,86]
        ypos = [30,30,40,40]
        for i in range(1,5):
            VAnal = self._HRMY.getVAnalog(i)
            if self._VAnalog[i-1] != VAnal or first_time_display:        
                self._VAnalog[i-1] = VAnal
                self.writeLine(msg='      ', x_pos=xpos[i-1], y_pos=ypos[i-1], font=2, flash=0, link=4)
                if self._VAnalog[i-1] >= 0:
                    text = "+" +'{:0>4}'.format(str(round(self._VAnalog[i-1], 1))) + "V"
                else:
                    text = "-" + '{:0>4}'.format(str(round(abs(self._VAnalog[i-1]), 1))) + "V"
                text = '{:>6}'.format(text)
                self.writeLine(msg=text, x_pos=xpos[i-1], y_pos=ypos[i-1], font=2, flash=0, link=1) 
            

    def showTestCalibrationScreen(self):
        if self._previous_menu != self._current_menu:
            self.logMessage("showTestCalibrationScreen()", self.INFO)            

    def refreshWarningArea(self):
        # This will be moved to refreshScreen1Data
        try:
            msg = ' AUTO'
            anyinauto = False
            for idx in range (1,5):
                if self._HRMY.caGetRange(idx).upper() == "AUTO":
                    anyinauto = True
                    msg = msg + str(idx)
                else:
                    msg = msg +" "
            msg = msg + " "
            if anyinauto:
                self._dDISP.SendData(u'#RL 20,0,60,6')
                self.writeLine(msg=msg, x_pos=20, y_pos=0, font=1, flash=0, link=1)
            else:
                self._dDISP.SendData(u'#RL 20,0,60,6')
        except:
             self._dDISP.SendData(u'#RL 20,0,60,6')

            
        try:
            if self._HRMY.getState() in ["STATE_ACQUIRING", "STATE_RUNNING"]:
                self.writeLine(msg=' ACQ ', x_pos=70, y_pos=0, font=1, flash=1, link=5)
            else:
                # Delete ACQ
                self._dDISP.SendData(u'#RL 70,0,90,6')
        except:
             self._dDISP.SendData(u'#RL 70,0,90,6')
             
        try:
            if self._DIAGS.getHVStatus() == True:
                self.writeLine(msg=' HV ', x_pos=100, y_pos=0, font=1, flash=1, link=5)
            else:
                # Delete HV
                self._dDISP.SendData(u'#RL 100,0,120,6')
        except:
            self._dDISP.SendData(u'#RL 100,0,120,6')
        
    def showNavigationKeys(self):
        if self._nav_key_pressed:
            self._nav_key_pressed = False
            
            # Draw Navigation Line
            self._dDISP.SendData('#GD 0,52,128,52')
            
            #Clear Navagition keys area
            msg = "#RL "+str(_PREVIOUS_X_INIT)+","+str(_PREVIOUS_Y_INIT)+","+str(_NEXT_X_END)+","+str(_NEXT_Y_END)
            self._dDISP.SendData(msg)
            
            if self._back_key:
                self.writeLine(msg=u'\u0004 Back ', x_pos=10, y_pos=55, font=0, flash=0, link=1)
                
                # Draw navigation keys buttons
                msg = '#RI '+str(_PREVIOUS_X_INIT)+','+str(_PREVIOUS_Y_INIT)+','+str(_PREVIOUS_X_END)+','+str(_PREVIOUS_Y_END)
                self._dDISP.SendData(msg)        
            else:
                self.writeLine(msg=u'\u0004 Prev ', x_pos=10, y_pos=55, font=0, flash=0, link=1)
                self.writeLine(msg=u'Next \u0003', x_pos=72, y_pos=55, font=0, flash=0, link=1)

                # Draw navigation keys buttons
                msg = '#RI '+str(_PREVIOUS_X_INIT)+','+str(_PREVIOUS_Y_INIT)+','+str(_PREVIOUS_X_END)+','+str(_PREVIOUS_Y_END)
                self._dDISP.SendData(msg)
                msg = '#RI '+str(_NEXT_X_INIT)+','+str(_NEXT_Y_INIT)+','+str(_NEXT_X_END)+','+str(_NEXT_Y_END)
                self._dDISP.SendData(msg)        
        
    def showKeyPressed(self, key):
        self.logMessage("showKeyPressed() key pressed: %s"%key, self.INFO)
        
        self._nav_key_pressed = True        
        if key == _ACTION_PREVIOUS:
            msg = "#RL "+str(_PREVIOUS_X_INIT)+","+str(_PREVIOUS_Y_INIT)+","+str(_PREVIOUS_X_END)+","+str(_PREVIOUS_Y_END)
            self._dDISP.SendData(msg)
            if self._back_key:
                self.writeLine(msg=u'\u0004 Back ', x_pos=10, y_pos=55, font=0, flash=0, link=1)
            else:
                self.writeLine(msg=u'\u0004 Prev ', x_pos=10, y_pos=55, font=0, flash=0, link=1)
        elif key == _ACTION_NEXT:
            msg = "#RL "+str(_NEXT_X_INIT)+","+str(_NEXT_Y_INIT)+","+str(_NEXT_X_END)+","+str(_NEXT_Y_END)
            self._dDISP.SendData(msg)
            self.writeLine(msg=u'Next \u0003', x_pos=72, y_pos=55, font=0, flash=0, link=1)
        elif key in [_ACTION_OP1, _ACTION_OP2, _ACTION_OP3, _ACTION_OP4, _ACTION_OP5, _ACTION_OP6, _ACTION_OP7, _ACTION_OP8, _ACTION_OP9]:
            if self._current_menu == "CHANGE_RANGE":
                self.setChannelRange(key)
            elif self._current_menu == "CHANGE_FILTER":                
                self.setChannelFilter(key)
        else:
            chn = {_ACTION_I1:0, _ACTION_I2:1, _ACTION_I3:2, _ACTION_I4:3}
            if key in chn.keys():
                self._channel_sel = int(chn[key])
            
            # Draw navigation keys buttons
            x_init = self._action_window[key][0]
            y_init = self._action_window[key][1]
            x_end = self._action_window[key][2]
            y_end = self._action_window[key][3]
            msg = u'#RI '+str(x_init)+','+str(y_init)+','+str(x_end)+','+str(y_end)
            self._dDISP.SendData(msg)        
            
    def setChannelRange(self, key):
        rang_val = {_ACTION_OP1:'100pA',
                    _ACTION_OP2:'1nA',
                    _ACTION_OP3:'10nA',
                    _ACTION_OP4:'100nA',
                    _ACTION_OP5:'1uA',
                    _ACTION_OP6:'10uA',
                    _ACTION_OP7:'100uA',
                    _ACTION_OP8:'1mA',
                    _ACTION_OP9:'AUTO',
                    }
        try:
            #self._HRMY.caSetRange(self._channel_sel+1, rang_val[key])

            command = "CHAN0"+str(self._channel_sel+1)+":CABO:RANGE " + rang_val[key]
            self._SCPI.inputCommand('LOCAL',str(command))
        except Exception, e:
            self.logMessage("setChannelRange(): Error setting range to channel %s due to %s"%(str(self._channel_sel+1),str(e)), self.ERROR)                
        
    def setChannelFilter(self, key):    
        filt_val = {_ACTION_OP1:'3200Hz',
                    _ACTION_OP2:'100Hz',
                    _ACTION_OP3:'10Hz',
                    _ACTION_OP5:'1Hz',
                    _ACTION_OP6:'0.5Hz',
                    }
        try:
            #self._HRMY.caSetFilter(self._channel_sel+1, filt_val[key])

            command = "CHAN0"+str(self._channel_sel+1)+":CABO:FILT " + filt_val[key]
            self._SCPI.inputCommand('LOCAL',str(command))
        except Exception, e:
            self.logMessage("setChannelRange(): Error setting filter to channel %s due to %s"%(str(self._channel_sel+1),str(e)), self.ERROR)                

    def convertCurrToStringMain(self, rang, value, digits=4):
        rep = { "1mA" : [0, 1e-3, " uA", 1999 ], # 1mA is represented as 1XXX uA
                    "100uA" : [1, 1e-3, " uA", 199.9 ], # 100uA is represented as 1XX.X uA
                    "10uA" : [2, 1e-3, " uA", 19.99], # 10uA is represented as 1X.XX uA
                    "1uA" : [0, 1e-6, " nA", 1999], # 1uA is represented as 1XXX nA 
                    "100nA" : [1, 1e-6, " nA", 199.9], # 100nA is represented as 1XX.X nA
                    "10nA" : [2, 1e-6, " nA" , 19.99], # 10nA is represented as 1X.XX uA
                    "1nA" : [0, 1e-9, " pA", 1999], # 100uaA is represented as 1XXX uA
                    "100pA" : [1, 1e-9, " pA", 199.9 ], # 100uaA is represented as 1XX.X uA 
            }
    
        num = float(value)
        text = ""
        
        round_to = rep[rang][0]
        if digits != 4:
            round_to += 2

        try:
            num = num / rep[rang][1]
            if ((num >= -abs(rep[rang][3])) and (num <= abs(rep[rang][3]))):
                aux = "%."+str(round_to)+"f"
                if round_to == 0:
                    aux2 = '{:0>'+str(digits)+'}'
                    aux2 = aux2.format(aux%abs(num)) + "."
                else:
                    aux2 = '{:0>'+str(digits+1)+'}'
                    aux2 = aux2.format(aux%abs(num))
                if num >= 0:                    
                    text = "+" + aux2 + rep[rang][2]
                else:
                    text = "-" + aux2 + rep[rang][2]
            else:
                text += "%.2e"%num + rep[rang][2];
        except Exception, e:
            self.logMessage("convertCurrenttoString(): Error calculating currnet!! %s"%str(e), self.ERROR)
    
        return text
                
    def writeLine(self, msg='', x_pos=0, y_pos=0, font=2, flash=0, link=1):
        # Write font type
        aux_val = '#ZF '+str(font)
        self._dDISP.SendData(aux_val)
        # Write zoom factor 1:1
        aux_val = '#ZZ 1,1'
        self._dDISP.SendData(aux_val)
        # Write flash atribute: 0=No Flash; 1=On/Off; 2=flash inverse; 3=Off/On
        aux_val = '#ZB '+str(flash)
        self._dDISP.SendData(aux_val)
        # Write link mode: 1=set; 2=delete; 3=inverse; 4=replace; 5=inverse replace
        aux_val = '#ZV '+str(link)
        self._dDISP.SendData(aux_val)
        # Write text message
        aux_val = u'#ZL '+str(x_pos)+","+str(y_pos)+","+msg+'\n'
        self._dDISP.SendData(aux_val)
                
class DisplayThread(threading.Thread):
    def __init__(self, parent=None, debug=None):
        threading.Thread.__init__(self)
         
        self._display = parent
        
        self._waitSemaphore = False
        self._endProcess = False
        self._processEnded = False
        
        self.refreshControlReset()

    def setSemaphore(self,val):
        self._waitSemaphore = val
        
    def end(self):
        #if self._display is not None:
        #     self._display.stop()
        self._endProcess = True
        
    def getProcessEnded(self):
        return self._processEnded
    
    def refreshControlReset(self):
        self.wellcome_disp_counter = 0
        self.brightness_counter = 0
        self._screen_saver_dis = False
        self._display.panelSetBrigtnessIllumination()
    
    def refreshControl(self):
        if not self._screen_saver_dis:
            self.brightness_counter += 1
            if self.brightness_counter > 180 and self._display.panel_illumination:
                self._display.panelSetBrigtnessIllumination(bright=10)
                self._display.setMenu('LOGO')
                self._screen_saver_dis = True
            elif self.brightness_counter > 120 and self._display.panel_brightness > 20:
                self._display.panelSetBrigtnessIllumination(bright=20)
            elif self.brightness_counter > 90 and self._display.panel_brightness >= 100:
                self._display.panelSetBrigtnessIllumination(bright=50)
                
    def getAction(self, x_press, y_press):
        current_menu = self._display.getMenu()
        retvalue = None
        if current_menu == 'LOGO':
            retvalue = 'next'
        else:
            for key,positions in self._display._action_window.iteritems():
                x_init = positions[0]
                y_init = positions[1]
                x_end = positions[2]
                y_end = positions[3]
                
                if ( x_press >= x_init and x_press <= x_end ) and (y_press>=y_init and y_press<= y_end):
                    retvalue = key
                    if key in self._display._menus[current_menu]['actions'].keys():
                        self._display.showKeyPressed(key)
                        break
                
        return retvalue


    def run(self): 
        ret_value = None
        if self._display is not None:
            while not (self._endProcess):
                #process touch display
                current_menu = self._display.getMenu()
                next_menu = current_menu
                
                ret_value = self._display.processData()
                if ret_value is not None:
                    action =  self.getAction(ret_value[0], ret_value[1])
                    if action is not None and action in self._display._menus[current_menu]['actions'].keys():
                        next_menu = self._display._menus[current_menu]['actions'][action]
                    # Any key pressed. Resets panel refresh
                    self.refreshControlReset()
                else:
                    if current_menu != 'LOGO':
                        self._display.showNavigationKeys()

                self._display.setMenu(next_menu)
                
                # Refresh screen control
                self.refreshControl()
                
                time.sleep(0.5)
  
        self._processEnded = True
    
        
    
