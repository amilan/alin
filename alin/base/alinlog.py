## @package alinlog.py 
#	File used to log information form alin project
#
#	Author = "Manolo Broseta"
#	Copyright = "Copyright 2016, ALBA"
#	Version = "1.1"
#	Email = "mbroseta@cells.es"
#	Status = "Development"
#	History:
#   30/03/2015 - file created
#	20/10/2015 - Several modifications done
#	             Doxygen detailed info added
__author__ = "Manolo Broseta"
__copyright__ = "Copyright 2016, ALBA"
__license__ = "GPLv3 or later"
__version__ = "1.1"
__email__ = "mbroseta@cells.es"
__status__ = "Development"


import logging
import logging.handlers

from distutils.sysconfig import get_python_lib

import os
from datetime import datetime

_LOG_TO_FILE = True

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

COLORS = {
	'WARNING'  : MAGENTA,
	'INFO'     : GREEN,
	'DEBUG'    : CYAN,
	'CRITICAL' : YELLOW,
	'ERROR'    : RED,
	'RED'      : RED,
	'GREEN'    : GREEN,
	'YELLOW'   : YELLOW,
	'BLUE'     : BLUE,
	'MAGENTA'  : MAGENTA,
	'CYAN'     : CYAN,
	'WHITE'    : WHITE,
}

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[0;%dm"
COLOR_BOLD = "\033[1;%dm"

class ColorFormatter(logging.Formatter):

	def __init__(self, *args, **kwargs):
		# can't do super(...) here because Formatter is an old school class
		logging.Formatter.__init__(self, *args, **kwargs)

	def format(self, record):
		levelname = record.levelname
		color     = COLOR_SEQ % (30 + COLORS[levelname])
		color_bold= COLOR_BOLD % (30 + COLORS[levelname])
		message   = logging.Formatter.format(self, record)
		message   = message.replace("$RESET", RESET_SEQ)\
						.replace("$COLOR_BOLD",  color_bold)\
						.replace("$COLOR", color)
		for k,v in COLORS.items():
			message = message.replace("$" + k,    COLOR_SEQ % (v+30))\
							.replace("$BG" + k,  COLOR_SEQ % (v+40))\
							.replace("$BG-" + k, COLOR_SEQ % (v+40))
		#print "MANOLO ", message + RESET_SEQ						
		return message + RESET_SEQ

## alinLog class
#
# Main class to read create the log folder and file
class AlinLog():
	## Logging levels
	#
	NOTSET		= 	logging.NOTSET
	DEBUG		= 	logging.DEBUG
	INFO		= 	logging.INFO
	WARNING		= 	logging.WARNING
	ERROR		= 	logging.ERROR
	CRITICAL	= 	logging.CRITICAL
	
	## The constructor.
	#  @debug (not mandatory) Option to enable/disbale the debug
	#  @loggerName (not mandatory) ModuleName to log information 
	def __init__(self, debug=False, loggerName=None):
		self._debug = debug
		self._debuglevel = 0
		
		self._log_to_file = _LOG_TO_FILE
		
		if loggerName is not None:
			self._loggerName = loggerName
		else:
			self._loggerName = 'Alin'
		
		#self.__logging_folder = os.path.abspath(os.path.dirname(__file__))+"/logs/"
		self.__logging_folder = get_python_lib()+"/alin/logs/"
		self.__logging_file = self.__logging_folder+"alin.log"
		
		if not os.path.exists(self.__logging_folder):
			os.makedirs(self.__logging_folder)
			
		
		self._devlogger = logging.getLogger(self._loggerName)
		self._handler = None
		if not len(self._devlogger.handlers):
			self._devlogger.setLevel(logging.DEBUG)
		
			self._handler = logging.handlers.RotatingFileHandler(self.__logging_file, maxBytes=5000000, backupCount=0)
			self._handler.setLevel(logging.INFO)

			formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
			self._handler.setFormatter(formatter)
			self._devlogger.addHandler(self._handler)
			
			self._screenhandler = logging.StreamHandler()
			self._screenhandler.setLevel(logging.INFO)

			formatter = ColorFormatter('%(asctime)s - $COLOR_BOLD%(levelname)s - %(name)s$RESET - $COLOR%(message)s$RESET')
			self._screenhandler.setFormatter(formatter)
			self._devlogger.addHandler(self._screenhandler)
			
		else:
			self._handler = self._devlogger.handlers[0]
			self._screenhandler = self._devlogger.handlers[1]
		
	def getHandlers(self):
		ret_value =  []
		ret_value.append(self._handler)
		ret_value.append(self._screenhandler)
		return ret_value
	
	## logEnable(dbg=False)
	#  This function enables the debug information through screen (To log file is always enabled)
	#  @param dbg (not mandatory) enables/disables the log oputput. By default is disabled
	def logEnable(self,dbg=False):
		if type(dbg) is not bool:
			raise AssertionError("The parameter must be a boolean")
		self._debug = dbg
		self.logMessage("logEnable()::Log set to %s"%self._debug, self.INFO)
	
	## logState()
	#  This function returns the log enabled/disabled status
	#  @return Debug state
	def logState(self):
		return self._debug
	
	## logLevel(level)
	#  This function sets a debug level
	#  @param level debug level to be set
	def logLevel(self,level):
		try:
			self.__debuglevel = int(level)
		except:
			raise AssertionError("The loglevel must be an integer")		
		self._debuglevel = level
		self._devlogger.setLevel(level)
		if self._handler is not None:
			self._handler.setLevel(level)
		if self._screenhandler is not None:
			self._screenhandler.setLevel(level)
		
	## logGetLevel()
	#  This function returns the log level set
	#  @return Debug level set
	def logGetLevel(self):
		return self._debuglevel
	
	## logMessage(msg, level) 
	#  Private function that prints a log message to log file and to screen (if enabled)
	#  @param msg Message to print
	#  @param level Message debug level
	def logMessage(self, msg, level):
		if level == self.CRITICAL:
			if self._log_to_file:
				self._devlogger.critical(msg)
		elif level == self.ERROR:
			if self._log_to_file:
				self._devlogger.error(msg)
		elif level == self.WARNING:
			if self._log_to_file:
				self._devlogger.warn(msg)
		elif level == self.INFO:
			if self._log_to_file:			
				self._devlogger.info(msg)
		else:
			if self._log_to_file:
				self._devlogger.debug(msg)

