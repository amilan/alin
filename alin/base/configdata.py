## @package Config.py 
#    File containing the driver module that controls the Configuration file
#
#    Author = "Manuel Broseta"
#    Copyright = "Copyright 2015, ALBA"
#    Version = "1.0"
#    Email = "mbroseta@cells.es"
#    Status = "Development"
#    History:
#              10/05/2016 - file created by Manolo Broseta

from distutils.sysconfig import get_python_lib

_CONFIG_FILE = "Config"

def getConfigData(mask=None):
	# Get config File
	config_folder = get_python_lib()+"/alin/config/"
	config_file = config_folder+_CONFIG_FILE
	
	try:
		with open(config_file, 'r') as f:
			lines = f.readlines()
			f.close()
		
		ret_value = {}
		comp = [ln.split(mask)[1].replace(" ","").replace("\t","").replace("\n","") for ln in lines if ln.startswith(mask)]
		if comp != []:
			for cm in comp:
				ret_value[cm.split("=")[0]] = cm.split("=")[1]
	except Exception, e:
		print str(e)
		return None
	
	return ret_value
