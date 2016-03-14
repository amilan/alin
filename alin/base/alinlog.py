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
		
			self._handler = logging.handlers.RotatingFileHandler(self.__logging_file, maxBytes=10000000, backupCount=5)
			self._handler.setLevel(logging.NOTSET)
		
			formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
			self._handler.setFormatter(formatter)
			self._devlogger.addHandler(self._handler)
		else:
			self._handler = self._devlogger.handlers[0]
		
	## logEnable(dbg=False)
	#  This function enables the debug information through screen (To log file is always enabled)
	#  @param dbg (not mandatory) enables/disables the log oputput. By default is disabled
	def logEnable(self,dbg=False):
		self._debug = dbg
		self.logMessage("logEnable()::Debug level set to %s"%self._debug, self.INFO)
		
	## logState()
	#  This function returns the log enabled/disabled status
	#  @return Debug state
	def logState(self):
		return self._debug
	
	## logLevel(level)
	#  This function sets a debug level
	#  @param level debug level to be set
	def logLevel(self,level):
		self._debuglevel = level
		self._devlogger.setLevel(level)
		if self._handler is not None:
			self._handler.setLevel(level)
		
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
		prt_msg = self._loggerName+" - "+msg
		if level == self.CRITICAL:
			self._devlogger.critical(msg)
			prt_msg = "CRITICAL -"+prt_msg
		elif level == self.ERROR:
			self._devlogger.error(msg)
			prt_msg = "ERROR -"+prt_msg
		elif level == self.WARNING:
			self._devlogger.warn(msg)
			prt_msg = "WARNING -"+prt_msg
		elif level == self.INFO:
			self._devlogger.info(msg)
			prt_msg = "INFO -"+prt_msg
		else:
			self._devlogger.debug(msg)
			prt_msg = "DEBUG -"+prt_msg
		
		if self._debug and level >= self._debuglevel:
			print str(datetime.now()),prt_msg
