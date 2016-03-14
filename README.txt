===============
ALba INstrument
===============

ALba INstrumnet (alin) provides a way to control the hardeware defined in the SPEC borad
Typical usage often looks like this::

    #!/usr/bin/env python

    from alin import *

    al = alinSDB()
    al.SDB_writeAddress(0x3100,0x01)
    ...
    
