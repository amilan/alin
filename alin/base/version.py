## @package alin.py 
#    File that contains the project version
#
#    Author = "Manolo Broseta"
#    Copyright = "Copyright 2016, ALBA"
#    Version = "1.0"
#    Email = "mbroseta@cells.es"
#    Status = "Development"
#    History:
#    29/01/2019 - file created
__author__ = "Manolo Broseta"

__MAJOR_VERSION = 0
__MINOR_VERSION = 1
__BUILD_VERSION = 13

def version():
    return "%d.%d.%d"%(__MAJOR_VERSION,__MINOR_VERSION,__BUILD_VERSION)