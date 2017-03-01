'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

__author__ = "Manolo Broseta Sebastia"
__copyright__ = "Copyright 2015, ALBA"
__license__ = "GPLv3 or later"
__version__ = "1.0"
__status__ = "Development"


import os, errno, re, sys, struct
import random as rd
import struct, site

class SimulatedSpec():
    """A Class that creates SPEC objects. This includes basic controls
    and methods in order to handle a PCIe attached SPEC board.
    Access to a valid libspec.so is mandatory for a proper operation.
    NOTE: user write/access permission to the SPEC dev is mandatory.

    Attributes:
        bus, dev     bus and device for the requested SPEC device.
                     If one (or both) parameters are < 0,
                     takes first available card.
        libc         Path to a valid libspec.so shared library.
                     If empty, it points to /usr/lib/libspec.so
    """

    def __init__(self, bus=-1, dev=-1, libc='/usr/lib/libspec.so'):
        print('Simulated SPEC object has been created')
        self.py_folder = site.getsitepackages()[0]
        f = open(self.py_folder+"/alin/sim_spec_data",'r')
        self.spec_data = []
        for el in f:
            try:
                aux = [int(a) for a in el.split(",")]
                self.spec_data.append(aux)
            except:
                pass
        f.close()        
        self.ADC_running = False

    def __del__(self):
        # Nothing to do
        pass

    def specLoadBitstream(self, bitstream):
        '''Load a new bitstream into the SPEC throughout GN4124 interface.
         bitstream is the path to the .bin bitstream that must be loaded.
        '''
        
        if os.path.isfile(bitstream):
            print('the bitstream has been successfully loaded')
            return True
        else:
            print('cannot find the bitstream!!!')
            return False

    # 32 bit register operations in the Wishbone addressing space

    def UpdateFile(self):
        f = open(self.py_folder+"/alin/sim_spec_data",'w')
        for el in self.spec_data:
            f.write(",".join(str(i) for i in el)+"\n")
        f.close()

    def UpdateData(self, address):
        sim_add = address/16
        f = open(self.py_folder+"/alin/sim_spec_data",'r')    
        el = [l for l in f.readlines()]
        val = el[sim_add]
        try:
            aux = [int(a) for a in val.split(",")]
            self.spec_data[sim_add] = aux
        except:
            pass
        f.close()

    def specWriteL(self, address, data):
        if (address <= 0x3fff) and (address>=0x0):
            sim_add = address/16
            sim_add_off = address%16

            d1 = (data&0xff000000)>>24
            d2 = (data&0x00ff0000)>>16
            d3 = (data&0x0000ff00)>>8
            d4 = (data&0x000000ff)


            self.spec_data[sim_add][sim_add_off+1] = d1
            self.spec_data[sim_add][sim_add_off+2] = d2
            self.spec_data[sim_add][sim_add_off+3] = d3
            self.spec_data[sim_add][sim_add_off+4] = d4
            
            self.UpdateFile()

    def specReadL(self, address, hexformat=True):
	    data = 0
	    if (address <= 0x3fff) and (address>=0x0):
		    sim_add = address/16
		    sim_add_off = address%16
		    self.UpdateData(address)
		
		    b1 = ((self.spec_data[sim_add][sim_add_off+1]<<24)&0xff000000)
		    b2 = ((self.spec_data[sim_add][sim_add_off+2]<<16)&0x00ff0000)
		    b3 = ((self.spec_data[sim_add][sim_add_off+3]<<8)&0x0000ff00)
		    b4 = (self.spec_data[sim_add][sim_add_off+4]&0x000000ff)

		    data = b1+b2+b3+b4

		    if ((address >= 0x3108) and (address <= 0x3128)) and (self.spec_data[(0x3100/16)][4] & 0x01):
		        if rd.getrandbits(1):
		            data = rd.random()*-1
		        else:
		            data = rd.random()*1
		        
		        data = int(self.float_hex4(data),16)
        
	    if hexformat:
		    return hex(data)
	    return data


    # bitwise register operations in the Wishbone addressing space 

    def specTestBit(self, address, offset):
        '''Test the bit placed at offset in the register at address.
        returns a nonzero result, 2**offset, if the bit is 1'''
        register = self.specReadL(address, hexformat=False)
        mask = 1 << offset
        return(register & mask)

     
    def specSetBit(self, address, offset):
        '''Set to 1 the bit placed at offset in the register at address'''
        register = self.specReadL(address, hexformat=False)
        mask = 1 << offset
        self.specWriteL(address, register | mask)


    def specClearBit(self, address, offset):
        '''Clear to 0 the bit placed at offset in the register at address'''
        register = self.specReadL(address, hexformat=False)
        mask = ~(1 << offset)
        self.specWriteL(address, register & mask)


    def specToggleBit(self, address, offset):
        '''Toggle/invert the bit placed at offset in the register at address'''
        register = self.specReadL(address, hexformat=False)
        mask = 1 << offset
        self.specWriteL(address, register ^ mask)
        
    def float_hex4(self,f):
        return ''.join(('%2.2x'%ord(c)) for c in struct.pack('f', f))









