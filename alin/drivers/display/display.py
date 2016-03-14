# Panel programme
#
# Created: March 2015
#      by: Manolo Broseta at ALBA Computing Division
#

import time, sys, select, math
from displaydrv import *
from image_res import *

from alin.base import AlinLog
from alin.drivers.harmony import Harmony

from distutils.sysconfig import get_python_lib

__CONFIG_FILE__ = "Config"
__CONFIG_MASK__ = "DISPLAY_"

class Display(AlinLog):
    DC1_BYTE = 0x11
    DC2_BYTE = 0x12
    
    ACK_VALUE = 0x06
    NACK_VALUE = 0x15
    
    DATA_LEN = 32
    
    def __init__(self, debug=False):
        AlinLog.__init__(self, debug=False, loggerName='Display')

        self._debug = debug
        self._debuglevel = None
        # Get default configuration from config file
        self.getConfigData()
        self.drv = DisplayDriver()
        self.panel_brightness = 0
        self.panel_illumination = False

        self.drv.SetProtocol(32,10)

        self.device = Harmony(debug=self._debug)

        self.ch_address = { "ch1": {'add':'ADC_CH1', 'pos':(5,17)},
                            "ch2": {'add':'ADC_CH2', 'pos':(5,29)},
                            "ch3": {'add':'ADC_CH3', 'pos':(5,41)},
                            "ch4": {'add':'ADC_CH4', 'pos':(5,53)},
                            "ch5": {'add':'ADC_CH5', 'pos':(70,17)},
                            "ch6": {'add':'ADC_CH6', 'pos':(70,29)},
                            "ch7": {'add':'ADC_CH7', 'pos':(70,41)},
                            "ch8": {'add':'ADC_CH8', 'pos':(70,53)}
                            }

        self.setLogLevel(self._debuglevel)
        self.logEnable(self._debug)
        
        #self.start()
    
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
                     
        except Exception, e:
            self.logMessage("%s::getConfigData():: Not possible to get config file due to:"%__CONFIG_MASK__,self.ERROR)
            self.logMessage(str(e),self.ERROR)
            
    def setLogLevel(self, level):
        self._debuglevel = level
        self.logLevel(self._debuglevel)
        
        self.drv.setLogLevel(self._debuglevel)
        self.device.setLogLevel(self._debuglevel)
            
    def start(self):
        self.logMessage("start():", self.INFO)
        # Enable ADC 
        self.logoDisplay()
        self.logMessage("start(): Display Started!!", self.INFO)
    
    def stop(self):
        self.drv.ClearScreen()
        self.drv.SendData('#TC 0')
        self.drv.PanelSettings(bright=70)        
        
        self.drv.DrawImage(40,0,Face_image)
        
        self.drv.SendData('#ZB 1')
        self.drv.SendData('#ZL 0,20,BYE\n')
        self.drv.SendData('#ZL 10,30,BYE\n')
        self.drv.SendData('#ZL 90,20,BYE\n')
        self.drv.SendData('#ZL 100,30,BYE\n')
        
        time.sleep(2)
        self.drv.SendData('#PD 0,0')        
        self.drv.ClearScreen()

        
    def processData(self):
        arg = self.drv.GetData()
        if arg is not None and len(arg)>0:
            if arg[0] == self.DC1_BYTE:
                data_len = arg[1]
                if data_len>0:
                    if self._debug:
                        txt = "I2C_READ_DATA= "
                        for el in arg[2:data_len]:
                            txt += hex(el)+", "
                        self.logMessage(txt, self.DEBUG)
                    
                    if data_len>self.DATA_LEN: data_len=self.DATA_LEN
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
                                        pass
                                    self.logMessage("Press X=%s Y=%s"%(str(x),str(y)), self.INFO)
                                    self.printPressed(x, y)
                                elif ord(data[2]) == 0x00 or ord(data[2]) == 0x02:
                                    #self.PrintReleased()
                                    pass
                        except:
                            pass
        
        if not self.displayed_logo:
            self.drv.SendData('#ZF 2')
            self.drv.SendData('#ZB 0')
            self.drv.SendData('#ZZ 1,2')
            self.drv.SendData('#ZL 5,0, ALBA-EM\sADC\sChannels\n')    
            self.drv.SendData('#ZF 1')
            self.drv.SendData('#ZZ 1,2')
            for idx, el in self.ch_address.iteritems():
                value = self.device.getInstantCurrent(el['add'])
                text_val = str(value)
                text = idx+":\s"+text_val[:8]+"\n"
                x = el['pos'][0]
                y = el['pos'][1]
                text = "#ZL "+str(x)+","+str(y)+","+text
                self.drv.SendData(text)
                            
        
    def printPressed(self, x=0,y=0):
        self.logMessage("PrintPressed X=%s Y=%s"%(str(x),str(y)), self.INFO)
        self.logoSet(False)
        
    def panelSet(self, bright=100, illumination=True):
        self.logMessage("Panel_set Bright=%s Illumination=%s"%(str(bright),illumination), self.INFO)
        self.panel_brightness = bright
        self.panel_illumination = illumination
        self.drv.PanelSettings(self.panel_brightness, self.panel_illumination)        
        
    def logoDisplay(self):
        self.drv.ClearScreen()
        # Change display orientation
        self.drv.SendData('#DO 2')
        # Delete cursor
        self.drv.SendData('#TC 0')
        # Set Panel brightness and illumination
        self.panelSet(bright= 100)
        # Draw Alba Logo
        self.drv.DrawImage(0,0,Alba_logo)
        # Set tocuh screen area
        self.drv.SendData('#AH 0,0,127,64')
        self.drv.SendData('#AA 0')
        self.drv.SendData('#AA 1')
        
        self.wellcome_disp_counter = 0
        self.displayed_logo = True
        self.brightness_counter = 0
        self._screen_saver_dis = False

    def logoSet(self,status=True):
        if status and not self.displayed_logo:
            self.logoDisplay()
            self.displayed_logo = True
        elif not status:
            self.panelSet(bright=100)
            self.brightness_counter = 0
            self._screen_saver_dis = False
            if self.displayed_logo:
                self.drv.ClearScreen()
                #self.drv.SendData("#YS 2") # Buzzer                                
                self.displayed_logo = False
                
        else:
            # do nothing if:
            # - request to display Logo, but Logo already in screen
            pass
        
    def logoRefreshControl(self):
        self.wellcome_disp_counter += 1
        if self.wellcome_disp_counter > 120:
            self.wellcome_disp_counter = 0
            self.logoSet(True)
            
        if not self._screen_saver_dis:
            self.brightness_counter += 1
            if self.brightness_counter > 60 and self.panel_brightness > 100:
                self.panelSet(bright=50)
            elif self.brightness_counter > 90 and self.panel_brightness > 20:
                self.panelSet(bright=20)
            elif self.brightness_counter > 180 and self.panel_illumination:
                self.panelSet(bright=10)
                self._screen_saver_dis = True
            
        
if __name__ == "__main__":
    
    
    import sys, select
    
    args = ' '.join(sys.argv[1:])
    
    Work = Display(debug=True)
    if args != '0':
        while 1:
            Work.processData()            
            time.sleep(1)
            Work.logoRefreshControl()
    else:
        Work.stopDisplay()
    sys.exit()

    
        
    
