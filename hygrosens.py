#!/usr/bin/python
"""
Hygrosens sensor output
Copyright 2005 by Brian C. Lane <bcl@brianlane.com>

"""

import os,sys


try:
    import serial
    
except ImportError:
    print """
          Error importing the serial library. You need to make sure 
          that it is properly installed. The pyserial library is available
          from http://pyserial.sourceforge.net
          """
    sys.exit(-1)


debug = 1



def process_sensor( line ):
    """
    Parse the 'I' serial number, type and check the checksum
    I11223344444444444455
    1 = Logical channel number 01 to 16
    2 = Sensor Type
    3 = Family Type
    4 = Serial number
    5 = CRC
    """
    print line
    

def process_value( sensor, line ):
    """
    Parse the 'V' data for a temperature sensor (type 01)
    V11222233
    1 = Logical Channel Number
    2 = Measurement data
    3 = CRC
    """
    print line







if __name__ == '__main__':
    """
    Test code to read the output continuously
    """

    port='/dev/ttyS0'
    timeout = 0.1
 
    ser = serial.Serial( port, 4800 )
    ser.setRtsCts(0)
    ser.setXonXoff(0)
    ser.setRTS(1)
    ser.setDTR(1)

    state = 0
    line = ser.readline(eol='\r')
    while line:
        if debug > 1:
            print line
            
        if line[0] == 'I':
            # A new sensor report
            sensor = process_sensor( line );

        elif line[0] == 'V':
            # Value report for the sensor
            process_value( sensor, line )

        line = ser.readline(eol='\r')
        
    ser.close()

