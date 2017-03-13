#!/usr/bin/env python
import os
import subprocess

from alin.base import version

from setuptools import setup
from setuptools.command.install import install

from distutils.sysconfig import get_python_lib
import site

class alin_install(install):
	def run(self):
		install.run(self)

        # This portion of the code has not the expected result. The environment variable created is not kept for always.
        # it is just created on the python sessions where this is launched.
        # TODO: improve this in the future.
        py_folder = get_python_lib()
        #py_folder = site.getsitepackages()[0]

        alin_folder = py_folder+"/alin"
        alin_log_folder = alin_folder+"/logs"   
        alin_devs_folder = alin_folder+"/deviceslib"

        if not os.path.exists(alin_log_folder):
            os.makedirs(alin_log_folder)       
        os.chmod(alin_log_folder, 0777) 

        if not os.path.exists(alin_devs_folder):
            os.makedirs(alin_devs_folder)		
        os.chmod(alin_devs_folder, 0777) 
		
        res = os.environ.get('ALINPATH', 'Not Set')
        if res == 'Not Set':

            #os.environ['ALINPATH'] = alin_folder

            # Generate environment profile for ALINPAT
            #profile_folder = '/etc/profile.d/'
            profile_name = "alin.sh"
            #with open(profile_folder+profile_name,"w") as f:
	        #    f.write("export ALINPATH="+alin_folder)

            subprocess.call(profile_name, shell=True)

        # Generate documentation
        if os.path.isfile("alin_docconfig"):
            #os.system("doxygen alin_docconfig")

            # Move generated doc folder to its porper location together witht the python module
            #os.system("cp -rf doc/man/man10 /usr/share/man/")
            #os.system("mandb")

            #cmd = "cp -rf doc/ "+alin_folder+"/doc"
            #os.system(cmd)
            pass

        print "\nInstallation completed!!!\n\n*** PLEASE restart session to apply changes ***\n"


def main():
	uname_folder = os.uname()[2]
	system_folder = '/lib/modules/'+uname_folder+'/extra'
	#py_folder = site.getsitepackages()[0]
	#py_folder = get_python_lib()
	py_folder = '/usr/lib/python2.7/site-packages'
	
	datafiles=[('/lib/firmware/fmc', ['resources/binaries/spec-init.bin','resources/binaries/spec-init-100T.bin']),
				('/etc/profile.d/', ['scripts/alin.sh']),
				(py_folder+'/alin/base/',['alin/base/sim_spec_data']),
				(py_folder+'/alin/config/',['alin/config/Config']),
				(py_folder+'/alin/deviceslib/',['alin/deviceslib/EM2_DAC',
											'alin/deviceslib/SPI',
											'alin/deviceslib/WB-EM2-DIGITAL_IO',
											'alin/deviceslib/WB-FMC-ADC-CORE',
											'alin/deviceslib/WB-FMC-FV-CONTROL',
											'alin/deviceslib/WB-HRMY-AVERAGE',
											'alin/deviceslib/WB-HRMY-CROSSBAR',
											'alin/deviceslib/WB-HRMY-FIFO',
											'alin/deviceslib/WB-HRMY-ID-GEN',
											'alin/deviceslib/WB-HRMY-MEMORY',
											]),
			]
	
	# Add files needed for the webserver including libraries
	datafiles = datafiles + [ (d.replace('resources','/var'), [os.path.join(d, f) for f in files]) for d,folders,files in os.walk("resources/www")]
	
	setup(name='AlIn',
			version=version.version(),
			description='Alba Instrument',
			author='Manolo Broseta',
			author_email='mbroseta@cells.es',
			url='git@gitcomputing.cells.es:electronics/em2.git',
			cmdclass={'install': alin_install},
			packages=['alin', 'alin.applications','alin.base','alin.deviceslib', 'alin.drivers', 'alin.tools'],
			scripts = ['scripts/alin',
						'scripts/alingen',
						'scripts/alinmain',
						'scripts/alinmainoff'
						],
			long_description=open('README.txt').read(),
			data_files=datafiles,
			)
				
if __name__ == "__main__":
    main()