#!/usr/bin/python

## @package webserver.py 
#    Module to start and control web server
#
#    Author = "Manolo Broseta"
#    Copyright = "Copyright 2016, ALBA"
#    Version = "1.0"
#    Email = "mbroseta@cells.es"
#    Status = "Development"

__author__ = "Manolo Broseta"
__copyright__ = "Copyright 2016, ALBA"
__license__ = "GPLv3 or later"
__version__ = "1.0"
__email__ = "mbroseta@cells.es"
__status__ = "Development"

from alin.base import getConfigData
from alin.base import AlinLog
from alin.base import version

from datetime import datetime
import json
import logging
from os import curdir, sep
import socket 
import thread
import threading
import time
from tornado.options import options, parse_command_line
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.websocket import WebSocketHandler
from tornado.escape import json_encode, json_decode

_CONFIG_MASK = "WEBSERVER_"

_WEB_REFRESH_TIME = 1
_PORT_NUMBER = 8888
_FPGA_DATA = False
_FPGA_DATA_REFRESH_PERIOD = 1

class WebServer():
    def __init__(self, debug=False):
        self._log = AlinLog(debug=True, loggerName='WEBSRV')
        
        # Get default configuration from config file
        self._debug = debug
        self.configure()
        
        self._applications = None
        
        self._webthread = None
        self._jsonThread = None
        self._jsonFPGADataThread = None

    def configure(self):
        # Get default configuration from config file
        configDict = getConfigData(_CONFIG_MASK)
        
        self._debug = bool(configDict["DEBUG_"]) if "DEBUG_" in configDict.keys() else self._debug
        self._debuglevel = int(configDict["DEBUGLEVEL_"]) if "DEBUGLEVEL_" in configDict.keys() else 40
        self._webrefreshtime = float(configDict["REFRESH_TIME_"]) if "REFRESH_TIME_" in configDict.keys() else _WEB_REFRESH_TIME
        self._webport = int(configDict["PORT_"]) if "PORT_" in configDict.keys() else _PORT_NUMBER
        self._fpga_data = bool(configDict["FPGA_DATA_"]) if "FPGA_DATA_" in configDict.keys() else _FPGA_DATA
        self._fpga_period = float(configDict["FPGA_DATA_REFRESH_PERIOD_"]) if "FPGA_DATA_REFRESH_PERIOD_" in configDict.keys() else _FPGA_DATA_REFRESH_PERIOD
        
        # Logging
        self._log.logLevel(self._debuglevel)
        self._log.logEnable(self._debug)
        
        self._log.logMessage("configure() %s configured"%_CONFIG_MASK, self._log.INFO)

    def reconfigure(self):
        self._log.logMessage("reconfigure(): reconfiguring applications and associted devices", self._log.INFO)
                
        # reconfigure applications
        self.configure()
        
    def shareApplications(self, applications):
        self._log.logMessage("shareApplications(): Getting needed applications layers", self._log.INFO)
        self._applications = applications
        
    def start(self):
        self._log.logMessage("start()....",self._log.INFO)        
        self.server = None
        try:
            self._jsonThread = JsonThread(self._log)
            self._jsonThread.setDataRefreshTime(self._webrefreshtime)
            self._jsonThread.setapplications(self._applications)
            self._jsonThread.setDaemon(True)
            self._jsonThread.start()
            self._log.logMessage("Main data JSON file thread Started....",self._log.INFO)
            
            self._jsonFPGADataThread = JsonFPGAData(self._log)
            self._jsonFPGADataThread.setFPGADataEnable(self._fpga_data)
            self._jsonFPGADataThread.setRefreshPeriod(self._fpga_period)
            self._jsonFPGADataThread.setapplications(self._applications)
            self._jsonFPGADataThread.setDaemon(True)
            self._jsonFPGADataThread.start()            
            self._log.logMessage("FPGA data file thread Started....",self._log.INFO)
            
            thread.start_new_thread(self.startThread,())
        except Exception, e:
            print str(e)
    
    def stop(self):
        self._log.logMessage("WebServerThread() Server Stopped....",self._log.INFO)
        
        if self._webthread is not None:
            self._webthread = None
        
        if self._jsonThread is not None:
           self._jsonThread.end()
                
        while not self._jsonThread.getProcessEnded():
            self._log.logMessage("Waiting thread to die", self._log.INFO)
            time.sleep(0.5)
        self._log.logMessage("JSON file generation Stopped....",self._log.INFO)
        
        if self._jsonFPGADataThread is not None:
           self._jsonFPGADataThread.end()
                
        while not self._jsonFPGADataThread.getProcessEnded():
            self._log.logMessage("Waiting thread to die", self._log.INFO)
            time.sleep(0.5)
        self._log.logMessage("FPGA Data file generation Stopped....",self._log.INFO)        

    def startThread(self):
        try:
            #static_path= os.path.join(local_path, 'static')
            handlers = [(r"/", MainHandler),
                        (r"/electrometer/*", ElectrometerSocketHandler, {"parent" : self, "log":self._log, "data":self._jsonThread}),
                        (r"/fpga", FpgaDataHandler, {"log":self._log}),
                        (r"/(.*)",DefaultHandler),
                        ]
            
            settings = {
                'default_handler_class': DefaultHandler,
                'template_path':  "/var/www/templates",
                'static_path': "/var/www/static",
                'debug': True
            }
            
            ElectrometerSocketHandler._log = self._log
            handler_list = self._log.getHandlers()
            for handler in handler_list:
                logging.getLogger('tornado.application').addHandler(handler)
                logging.getLogger('tornado.access').addHandler(handler)
            
            application = Application(handlers, **settings)
            application.listen(self._webport)

            self._log.logMessage("Starting server...", self._log.INFO)
            
            try:
                import tornado.ioloop
                self._webthread = thread.start_new_thread(tornado.ioloop.IOLoop.current().start())
                self._log.logMessage("Finished...", self._log.INFO)
            except KeyboardInterrupt:
                self._log.logMessage("^C received, shutting down the web server", self._log.INFO)
        except Exception, e:
            self._log.logMessage("Failed to start WebServer due to %s"%str(e), self._log.ERROR)
            
class DefaultHandler(RequestHandler):
    def get(self, url):
        if "index.html" in url.lower():
            self.render("index.html")
        elif "config.html" in url.lower():
            self.render("config.html")     
        elif "diags.html" in url.lower():
            self.render("diags.html")     
        elif "inout.html" in url.lower():
            self.render("inout.html")     
        elif "fpga.html" in url.lower():
            self.render("fpga.html")
        elif "usermanual.html" in url.lower():
            self.render("usermanual.html")
        else:
            self.render("error.html")  
    
    def write_error(self, status_code, **kwargs): 
        self.render("error.html")              

class MainHandler(RequestHandler):
    def get(self):
        self.render("index.html")
    
class ConfigHandler(RequestHandler):
    def get(self):
        self.render("config.html")     
        
class DiagsHandler(RequestHandler):
    def get(self):
        self.render("diags.html")             

class InOutHandler(RequestHandler):
    def get(self):
        self.render("inout.html")             
        
class FpgaHandler(RequestHandler):
    def get(self):
        self.render("fpga.html")     

class FpgaDataHandler(WebSocketHandler):    
    fpga_waiters = set()
    
    def initialize(self, log):
        self._log = log

    def open(self):       
        self.fpga_waiters.add(self)
        client = self.request.remote_ip
        self._log.logMessage("Socket open for FPGA Data with client " + str(client),self._log.INFO)
        self._log.logMessage("FPGA Data waiters list lenght %s"%len(self.fpga_waiters),self._log.INFO)        

    def on_close(self):
        client = self.request.remote_ip
        self.fpga_waiters.remove(self)
        self._log.logMessage("Socket for FPGA Data closed client " + str(client),self._log.INFO)
        self._log.logMessage("FPGA waiters list lenght %s"%len(self.fpga_waiters),self._log.INFO)
        
class ElectrometerSocketHandler(WebSocketHandler):
    waiters = set()
    
    def initialize(self, parent, log, data):
        self._log = log
        self._data = data
        self._webport = parent._webport
        self._scpi = parent._applications['SCPI_APP']['pointer']
    
    def open(self):       
        self.waiters.add(self)
        client = self.request.remote_ip
        self._log.logMessage("Socket open with client " + str(client),self._log.INFO)
        self._log.logMessage("Main data waiters list lenght %s"%len(self.waiters),self._log.INFO)        
        
        json_data = self._data.getJSONData()
        self.write_message(json_data)
        self._log.logMessage("Main data contents refresh in client " + str(client),self._log.INFO)


    def on_close(self):
        client = self.request.remote_ip
        self.waiters.remove(self)
        self._log.logMessage("Socket closed client " + str(client),self._log.INFO)
        self._log.logMessage("Main waiters list lenght %s"%len(self.waiters),self._log.INFO)

    def on_message(self, jsondata):
        client = self.request.remote_ip
        try:
            command = json.loads(jsondata)["command"]

            response = "IP Client:" + client + " COMMAND: " + command 
            self._log.logMessage(response, self._log.INFO)
            try:
                self._scpi.inputCommand(str(client)+":"+str(self._webport),str(command))
            except Exception, e:
                response = "IP Client:" + client + " ERROR!!: Invalid Command: " + commad + " due to: " + str(e)
                self._log.logMessage(response, self._log.ERROR)
        except Exception, e:
            response = "IP Client:" + client + " ERROR!!: Invalid Command!! " +str(e)
            self._log.logMessage(response, self._log.ERROR)

class JsonThread(threading.Thread):
    def __init__(self, log = None):
        threading.Thread.__init__(self)
        
        # Init local variables
        self._log = log
        self._dDIAGS = None
        self._PSB = None
        self._HARMONY = None
        self._endProcess = False
        self._processEnded = False
        self._report_msg_dsp = True
        self.json_data = None
        self._data_refresh_time = 1
        self._data_dict = {}
                
    def end(self):
        self._endProcess = True
                
    def getProcessEnded(self):
        return self._processEnded
    
    def setapplications(self, applications):
        self._dDIAGS = applications['DIAGNOSTICS']['pointer']
        self._PSB = applications['PSB']['pointer']
        self._HARMONY = applications['HARMONY']['pointer']
        self._SCPI = applications['SCPI_APP']['pointer']
      
    def setDataRefreshTime(self, value):
        self._data_refresh_time = value
        
    def getJSONData(self):
        return json.dumps(self._data_dict, indent=4, skipkeys=True, sort_keys=True)

    def run(self): 
        count = 0
        
        # array of data to be refresed on wed: "dataname":(callback function, parameters)
        array_data = {"mac":            (self._SCPI.getMacAddress, None),
                        "identification": (self._SCPI.getIdetification, None),
                        "version":        (version.version, None),
                        "fwversion":      (self._HARMONY.getFWVersion, None),
                        "fwversiondate":  (self._HARMONY.getFWVersionDate, None),
                        "cafetemp":       (self._HARMONY.caFETemp, None),
                        "cacbtemp":       (self._HARMONY.caCBTemp, None),
                        "acq_trig_mode":  (self._HARMONY.getTrigMode, None),
                        "acq_trig_pol":   (self._HARMONY.getTrigPol, None),
                        "acq_trig_delay": (self._HARMONY.getTrigDelay, None),
                        "acq_trig_input": (self._HARMONY.getTrigInput, None),
                        "acq_time":       (self._HARMONY.getAcqTime, None),
                        "acq_range":      (self._HARMONY.getRange, None),
                        'acq_ntriggers':  (self._HARMONY.getAcqNTriggers, None),
                        "acq_filter":     (self._HARMONY.getFilter, None),
                        "acq_state":      (self._HARMONY.getState, None),
                        "acq_ndata":      (self._HARMONY.getNData, None),
                        "acq_chan01":     (self._HARMONY.getCurrent, 0),
                        "acq_chan02":     (self._HARMONY.getCurrent, 1),
                        "acq_chan03":     (self._HARMONY.getCurrent, 2),
                        "acq_chan04":     (self._HARMONY.getCurrent, 3),
                        "ioport_1_name":  (self._HARMONY.getGPIOName, 1),
                        "ioport_2_name":  (self._HARMONY.getGPIOName, 2),
                        "ioport_3_name":  (self._HARMONY.getGPIOName, 3),
                        "ioport_4_name":  (self._HARMONY.getGPIOName, 4),
                        "ioport_5_name":  (self._HARMONY.getGPIOName, 5),
                        "ioport_6_name":  (self._HARMONY.getGPIOName, 6),
                        "ioport_7_name":  (self._HARMONY.getGPIOName, 7),
                        "ioport_8_name":  (self._HARMONY.getGPIOName, 8),
                        "ioport_9_name":  (self._HARMONY.getGPIOName, 9),
                        "ioport_10_name": (self._HARMONY.getGPIOName, 10),
                        "ioport_11_name": (self._HARMONY.getGPIOName, 11),
                        "ioport_12_name": (self._HARMONY.getGPIOName, 12),
                        "ioport_13_name": (self._HARMONY.getGPIOName, 13),
                        "ioport_1_config":(self._HARMONY.getGPIOConfig, 1),
                        "ioport_2_config":(self._HARMONY.getGPIOConfig, 2),
                        "ioport_3_config":(self._HARMONY.getGPIOConfig, 3),
                        "ioport_4_config":(self._HARMONY.getGPIOConfig, 4),
                        "ioport_5_config":(self._HARMONY.getGPIOConfig, 5),
                        "ioport_6_config":(self._HARMONY.getGPIOConfig, 6),
                        "ioport_7_config":(self._HARMONY.getGPIOConfig, 7),
                        "ioport_8_config":(self._HARMONY.getGPIOConfig, 8),
                        "ioport_9_config":(self._HARMONY.getGPIOConfig, 9),
                        "ioport_10_config":(self._HARMONY.getGPIOConfig, 10),
                        "ioport_11_config":(self._HARMONY.getGPIOConfig, 11),
                        "ioport_12_config":(self._HARMONY.getGPIOConfig, 12),
                        "ioport_13_config":(self._HARMONY.getGPIOConfig, 13),
                        "ioport_1_value": (self._HARMONY.getGPIOValue, 1),
                        "ioport_2_value": (self._HARMONY.getGPIOValue, 2),
                        "ioport_3_value": (self._HARMONY.getGPIOValue, 3),
                        "ioport_4_value": (self._HARMONY.getGPIOValue, 4),
                        "ioport_5_value": (self._HARMONY.getGPIOValue, 5),
                        "ioport_6_value": (self._HARMONY.getGPIOValue, 6),
                        "ioport_7_value": (self._HARMONY.getGPIOValue, 7),
                        "ioport_8_value": (self._HARMONY.getGPIOValue, 8),
                        "ioport_9_value": (self._HARMONY.getGPIOValue, 9),
                        "ioport_10_value":(self._HARMONY.getGPIOValue, 10),
                        "ioport_11_value":(self._HARMONY.getGPIOValue, 11),
                        "ioport_12_value":(self._HARMONY.getGPIOValue, 12),
                        "ioport_13_value":(self._HARMONY.getGPIOValue, 13),
                        "supplyport_1":   (self._HARMONY.getSupplyPort, 1),
                        "supplyport_2":   (self._HARMONY.getSupplyPort, 2),
                        "supplyport_3":   (self._HARMONY.getSupplyPort, 3),
                        "supplyport_4":   (self._HARMONY.getSupplyPort, 4),
                        "chn1_insvoltage":(self._HARMONY.getInstantVoltage, 0),
                        "chn2_insvoltage":(self._HARMONY.getInstantVoltage, 1),
                        "chn3_insvoltage":(self._HARMONY.getInstantVoltage, 2),
                        "chn4_insvoltage":(self._HARMONY.getInstantVoltage, 3),
                        "chn1_inscurrent":(self._HARMONY.getInstantCurrent, 0),
                        "chn2_inscurrent":(self._HARMONY.getInstantCurrent, 1),
                        "chn3_inscurrent":(self._HARMONY.getInstantCurrent, 2),
                        "chn4_inscurrent":(self._HARMONY.getInstantCurrent, 3),
                        "chn1_avgcurrent":(self._HARMONY.getAverageCurrent, 0),
                        "chn2_avgcurrent":(self._HARMONY.getAverageCurrent, 1),
                        "chn3_avgcurrent":(self._HARMONY.getAverageCurrent, 2),
                        "chn4_avgcurrent":(self._HARMONY.getAverageCurrent, 3),
                        "chn1_catemp":    (self._HARMONY.caReadTemp, 1),
                        "chn2_catemp":    (self._HARMONY.caReadTemp, 2),
                        "chn3_catemp":    (self._HARMONY.caReadTemp, 3),
                        "chn4_catemp":    (self._HARMONY.caReadTemp, 4),
                        "chn1_cafilter":  (self._HARMONY.caGetFilter, 1),
                        "chn2_cafilter":  (self._HARMONY.caGetFilter, 2),
                        "chn3_cafilter":  (self._HARMONY.caGetFilter, 3),
                        "chn4_cafilter":  (self._HARMONY.caGetFilter, 4),
                        "chn1_capostfilter": (self._HARMONY.caGetPostFilter, 1),
                        "chn2_capostfilter": (self._HARMONY.caGetPostFilter, 2),
                        "chn3_capostfilter": (self._HARMONY.caGetPostFilter, 3),
                        "chn4_capostfilter": (self._HARMONY.caGetPostFilter, 4),
                        "chn1_caprefilter": (self._HARMONY.caGetPreFilter, 1),
                        "chn2_caprefilter": (self._HARMONY.caGetPreFilter, 2),
                        "chn3_caprefilter": (self._HARMONY.caGetPreFilter, 3),
                        "chn4_caprefilter": (self._HARMONY.caGetPreFilter, 4),
                        "chn1_carange":   (self._HARMONY.caGetRange, 1),
                        "chn2_carange":   (self._HARMONY.caGetRange, 2),
                        "chn3_carange":   (self._HARMONY.caGetRange, 3),
                        "chn4_carange":   (self._HARMONY.caGetRange, 4),
                        "chn1_carangeset":   (self._HARMONY.caGetRangeSet, 1),
                        "chn2_carangeset":   (self._HARMONY.caGetRangeSet, 2),
                        "chn3_carangeset":   (self._HARMONY.caGetRangeSet, 3),
                        "chn4_carangeset":   (self._HARMONY.caGetRangeSet, 4),                        
                        "chn1_carange_value": (self._HARMONY.caGetRangeSet, 1),
                        "chn2_carange_value": (self._HARMONY.caGetRangeSet, 2),
                        "chn3_carange_value": (self._HARMONY.caGetRangeSet, 3),
                        "chn4_carange_value": (self._HARMONY.caGetRangeSet, 4),
                        "chn1_carange_unit":  (self._HARMONY.caGetRangeSet, 1),
                        "chn2_carange_unit": (self._HARMONY.caGetRangeSet, 2),
                        "chn3_carange_unit": (self._HARMONY.caGetRangeSet, 3),
                        "chn4_carange_unit": (self._HARMONY.caGetRangeSet, 4),
                        "chn1_catigain":  (self._HARMONY.caGetTIGain, 1),
                        "chn2_catigain":  (self._HARMONY.caGetTIGain, 2),
                        "chn3_catigain":  (self._HARMONY.caGetTIGain, 3),
                        "chn4_catigain":  (self._HARMONY.caGetTIGain, 4),
                        "chn1_cavgain":   (self._HARMONY.caGetVGain, 1),
                        "chn2_cavgain":   (self._HARMONY.caGetVGain, 2),
                        "chn3_cavgain":   (self._HARMONY.caGetVGain, 3),
                        "chn4_cavgain":   (self._HARMONY.caGetVGain, 4),
                        "chn1_cainv":     (self._HARMONY.caGetInversion, 1),
                        "chn2_cainv":     (self._HARMONY.caGetInversion, 2),
                        "chn3_cainv":     (self._HARMONY.caGetInversion, 3),
                        "chn4_cainv":     (self._HARMONY.caGetInversion, 4),
                        "chn1_satmax":    (self._HARMONY.caGetSaturationMax, 1),
                        "chn2_satmax":    (self._HARMONY.caGetSaturationMax, 2),
                        "chn3_satmax":    (self._HARMONY.caGetSaturationMax, 3),
                        "chn4_satmax":    (self._HARMONY.caGetSaturationMax, 4),                        
                        "chn1_satmin":    (self._HARMONY.caGetSaturationMin, 1),
                        "chn2_satmin":    (self._HARMONY.caGetSaturationMin, 2),
                        "chn3_satmin":    (self._HARMONY.caGetSaturationMin, 3),
                        "chn4_satmin":    (self._HARMONY.caGetSaturationMin, 4),                        
                        "chn1_offset":    (self._HARMONY.caGetOffset, 1),
                        "chn2_offset":    (self._HARMONY.caGetOffset, 2),
                        "chn3_offset":    (self._HARMONY.caGetOffset, 3),
                        "chn4_offset":    (self._HARMONY.caGetOffset, 4),
                        "chn1_aout":      (self._HARMONY.getVAnalog, 1),
                        "chn2_aout":      (self._HARMONY.getVAnalog, 2),
                        "chn3_aout":      (self._HARMONY.getVAnalog, 3),
                        "chn4_aout":      (self._HARMONY.getVAnalog, 4),
                        "dac_gain":       (self._HARMONY.getDACGain, None),
                        "psb_viso":       (self._PSB.getISO, None),
                        "psb_vcc":        (self._PSB.getVCC, None),
                        "psb_vs":         (self._PSB.getVS, None), 
                        "psb_vaux":       (self._PSB.getVAUX, None),
                        "fv_instant":     (self._dDIAGS.getFVInstantVoltage, None),
                        "fv_avg":         (self._dDIAGS.getFVAverageVoltage, None),
                        "fv_max":         (self._dDIAGS.getFVMaximumVoltage, None),
                        "fv_min":         (self._dDIAGS.getFVMinimumVoltage, None),
                        "fv_led":         (self._dDIAGS.getFVLED, None),
                        "fv_relay":       (self._dDIAGS.getFVRelay, None),
                        "fv_maxlim":      (self._dDIAGS.getFVMaximumLimit, None),
                        "fv_minlim":      (self._dDIAGS.getFVMinimumLimit, None),
                    }
        
        while not (self._endProcess):
            
            timestamp = time.time()
            
            if len(ElectrometerSocketHandler.waiters)>= 1:
                if self._report_msg_dsp:
                    self._log.logMessage("WebServer() JSON data generation Started....",self._log.INFO)
                    self._report_msg_dsp = False

                diagstemp_loglevel = self._dDIAGS.logGetLevel()
                if diagstemp_loglevel != 40: self._dDIAGS.logLevel(40)
                psbtemp_loglevel = self._PSB.logGetLevel()
                if psbtemp_loglevel != 40: self._PSB.logLevel(40)
                hrmy_loglevel = self._HARMONY.logGetLevel()
                if hrmy_loglevel != 40: self._HARMONY.logLevel(40)
                
                
                data_to_send = {}
                try:
                    for key in array_data.keys():
                        func = array_data[key][0]
                        param = array_data[key][1]
                        if param is not None:
                            if key in ["acq_chan01","acq_chan02","acq_chan03","acq_chan04"]:
                                tmp = eval(func(param))
                            else:
                                tmp = str(func(param))
                        else:
                            try:
                                tmp = str(func())
                            except:
                                tmp = str(func)
    
                        if key == "acq_state":
                            if tmp=="STATE_ACQUIRING":
                                tmp = 'ACQUIRING' 
                            elif tmp=="STATE_RUNNING":
                                tmp = 'RUNNING' 
                            else:
                                tmp = 'ON'
                        elif key in ["chn1_carange_value", "chn2_carange_value", "chn3_carange_value", "chn4_carange_value"]:
                            tmp = tmp[:-2]
                        elif key in ["chn1_carange_unit", "chn2_carange_unit", "chn3_carange_unit", "chn4_carange_unit"]:
                            tmp = tmp[-2:]
                        elif key in ["chn1_cainv","chn2_cainv","chn3_cainv","chn4_cainv", "psb_viso", "psb_vcc", "psb_vs", "psb_vaux", "fv_relay"]:
                            tmp = 'On' if tmp=="1" else "Off"
                        elif key in  ["ioport_1_value","ioport_2_value","ioport_3_value","ioport_4_value",
                                      "ioport_5_value","ioport_6_value","ioport_7_value","ioport_8_value",
                                      "ioport_9_value","ioport_10_value","ioport_11_value","ioport_12_value",
                                      "ioport_13_value"]:
                            tmp = 'High' if tmp=="True" else "Low"
                    
                        always_refresh = ["chn1_insvoltage", "chn2_insvoltage", "chn3_insvoltage","chn4_insvoltage","chn1_inscurrent","chn2_inscurrent","chn3_inscurrent","chn4_inscurrent"]
                        if key in always_refresh:
                            self._data_dict[key] = tmp
                            data_to_send[key] = self._data_dict[key]
                        elif key not in self._data_dict.keys() or tmp != self._data_dict[key]:
                            self._data_dict[key] = tmp
                            data_to_send[key] = self._data_dict[key]
                    
                    mem_tmp_val = self._dDIAGS.getMemoryMLen()
                    lt = ["diags_mlen_0", "diags_mlen_1", "diags_mlen_2"]                    
                    for idx, el in enumerate(lt):
                        tmp = str(mem_tmp_val[idx])
                        if el not in self._data_dict.keys() or tmp != self._data_dict[el]:
                            self._data_dict[el] = tmp
                            data_to_send[el] = self._data_dict[el]

                    mem_tmp_val = self._dDIAGS.getMemoryActReq()
                    lt = ["diags_mactreq_0", "diags_mactreq_1", "diags_mactreq_2"]                    
                    for idx, el in enumerate(lt):
                        tmp = str(mem_tmp_val[idx])
                        if el not in self._data_dict.keys() or tmp != self._data_dict[el]:
                            self._data_dict[el] = tmp
                            data_to_send[el] = self._data_dict[el]

                    mem_tmp_val = self._dDIAGS.getMemorySgnAct()
                    lt = ["diags_msgnact_0", "diags_msgnact_1", "diags_msgnact_2"]                    
                    for idx, el in enumerate(lt):
                        tmp = str(mem_tmp_val[idx])
                        if el not in self._data_dict.keys() or tmp != self._data_dict[el]:
                            self._data_dict[el] = tmp
                            data_to_send[el] = self._data_dict[el]

                    mem_tmp_val = self._dDIAGS.getUploadMessages()
                    lt = ["diags_uploadmsg_0", "diags_uploadmsg_1", "diags_uploadmsg_2"]                    
                    for idx, el in enumerate(lt):
                        tmp = str(mem_tmp_val[idx])
                        if el not in self._data_dict.keys() or tmp != self._data_dict[el]:
                            self._data_dict[el] = tmp
                            data_to_send[el] = self._data_dict[el]

                    mem_tmp_val = self._dDIAGS.getDownloadMessages()
                    lt = ["diags_dwloadmsg_0", "diags_dwloadmsg_1", "diags_dwloadmsg_2"]                    
                    for idx, el in enumerate(lt):
                        tmp = str(mem_tmp_val[idx])
                        if el not in self._data_dict.keys() or tmp != self._data_dict[el]:
                            self._data_dict[el] = tmp
                            data_to_send[el] = self._data_dict[el]

                    current = self._dDIAGS.getDiagsCurrent()
                    if current != {}:
                        tmp = str(round(1000*current['VSENSE_I_ISO'],2))
                        if "diags_viso" not in self._data_dict.keys() or tmp != self._data_dict["diags_viso"]:
                            self._data_dict["diags_viso"] = tmp
                            data_to_send["diags_viso"] = self._data_dict["diags_viso"]
                        tmp = str(round(1000*current['VSENSE_I_VCC'],2))
                        if "diags_vcc" not in self._data_dict.keys() or tmp != self._data_dict["diags_vcc"]:
                            self._data_dict["diags_vcc"] = tmp
                            data_to_send["diags_vcc"] = self._data_dict["diags_vcc"]
                        tmp = str(round(1000*current['VSENSE_I_VS'],2))
                        if "diags_vs" not in self._data_dict.keys() or tmp != self._data_dict["diags_vs"]:
                            self._data_dict["diags_vs"] = tmp
                            data_to_send["diags_vs"] = self._data_dict["diags_vs"]
                        tmp = str(round(1000*current['VSENSE_I_AUX'],2))
                        if "diags_vaux" not in self._data_dict.keys() or tmp != self._data_dict["diags_vaux"]:
                            self._data_dict["diags_vaux"] = tmp
                            data_to_send["diags_vaux"] = self._data_dict["diags_vaux"]
                        tmp = str(round(1000*current['VSENSE_I_SPEC'],2))
                        if "diags_vspec" not in self._data_dict.keys() or tmp != self._data_dict["diags_vspec"]:
                            self._data_dict["diags_vspec"] = tmp
                            data_to_send["diags_vspec"] = self._data_dict["diags_vspec"]
                        tmp = str(round(current['VSENSE_12V'],3))
                        if "diags_12v" not in self._data_dict.keys() or tmp != self._data_dict["diags_12v"]:
                            self._data_dict["diags_12v"] = tmp
                            data_to_send["diags_12v"] = self._data_dict["diags_12v"]
                except Exception, e:
                    print str(e)
                
                if diagstemp_loglevel != 40: self._dDIAGS.logLevel(diagstemp_loglevel)
                if psbtemp_loglevel != 40: self._PSB.logLevel(psbtemp_loglevel)
                if hrmy_loglevel != 40: self._HARMONY.logLevel(hrmy_loglevel)

                self.json_data = json.dumps(data_to_send, indent=4, skipkeys=True, sort_keys=True)

                # To test
                #out_file = open("/var/www/static/data.json","w")
                #out_file.write(self.json_data)
                #out_file.close()
                
                for waiter in ElectrometerSocketHandler.waiters:
                    try:
                        waiter.write_message(self.json_data)
                    except:
                        self._log.logMessage("Error sending message to waiters....",self._log.ERROR)

                time.sleep(self._data_refresh_time*0.9 )
            else:
                if not self._report_msg_dsp:
                    self._log.logMessage("JSON data generation Stopped!!!....",self._log.INFO)
                    self._report_msg_dsp = True

        
        self._processEnded = True


class JsonFPGAData(threading.Thread):
    def __init__(self, log = None):
        threading.Thread.__init__(self)
        
        # Init local variables
        self._log = log
        self._FPGA = None
        self._refresh_period = 1
        self._fpga_data_enabled = False
        self._report_msg_dsp = True
        self._endProcess = False
        self._processEnded = False
                
    def end(self):
        self._endProcess = True
                
    def getProcessEnded(self):
        return self._processEnded
    
    def setapplications(self, applications):
        self._FPGA = applications['HARMONY']['pointer']._dFPGA
    
    def setFPGADataEnable(self, fpga_data):
        self._fpga_data_enabled = fpga_data
        
    def setRefreshPeriod(self, period):
        self._refresh_period = period
    
    def saveFPGAData(self):
        dev_list = [('WB-HRMY-CROSSBAR', 0), 
                    ('WB-HRMY-CROSSBAR', 1), 
                    ('WB-HRMY-CROSSBAR', 2), 
                    ('WB-FMC-FV-CONTROL', 0),
                    ('WB-HRMY-AVERAGE', 0), 
                    ('WB-HRMY-AVERAGE', 1), 
                    ('WB-HRMY-AVERAGE', 2), 
                    ('WB-HRMY-AVERAGE', 3), 
                    ('WB-HRMY-FIFO', 0), 
                    ('WB-HRMY-FIFO', 1), 
                    ('WB-HRMY-FIFO', 2), 
                    ('WB-HRMY-FIFO', 3),
                    ('WB-FMC-ADC-CORE', 0), 
                    ('WB-HRMY-MEMORY', 0), 
                    ('WB-HRMY-ID-GEN', 0), 
                    ('SPI', 0), 
                    ('WB-EM2-DIGITAL_IO', 0),
                    ('EM2_DAC', 0),
                    ]

        out_dict = {}
        dev_dict = []
        for dev in dev_list:
            d = self._FPGA.checkDevice (device=dev[0], num=dev[1])
            if dev[0] == 'WB-HRMY-MEMORY':
                att_list = d.getAttributesList()
                temp = {}
                for att in att_list:
                    if att != "V_DATA":
                        val = d.readAttribute(att)
                        temp[att] = val
            else:
                temp = d.getDeviceData()
            dev_dict.append([dev[0]+" "+str(dev[1]), temp])
            
        out_dict['Last update'] = {'DATE': time.strftime("%d/%m/%Y"), 'TIME': time.strftime("%H:%M:%S")}
        out_dict['Data'] = dev_dict

        return out_dict

    def run(self): 
        while not (self._endProcess):
            if len(FpgaDataHandler.fpga_waiters)>= 1:
                if self._report_msg_dsp:
                    self._log.logMessage("FPGA Data generation Started....",self._log.INFO)
                    self._report_msg_dsp = False

                jsonfpgadata = json.dumps(self.saveFPGAData(), indent=4, skipkeys=True, sort_keys=True)
                for waiter in FpgaDataHandler.fpga_waiters:
                    try:
                        waiter.write_message(jsonfpgadata)
                    except:
                        self._log.logMessage("Error sending message to waiters....",self._log.ERROR)
                
                time.sleep(self._refresh_period)
                
            else:
                if not self._report_msg_dsp:
                    self._log.logMessage("FPGA Data generation Stopped!!!....",self._log.INFO)
                    self._report_msg_dsp = True
        
        self._processEnded = True
