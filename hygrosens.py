#!/usr/bin/python

# Output from the Humidity-Temperature module
#
# @
#I01010100B007272701CD
#V01084E55
#I02020100B007272701FD
#V0219A6B2
#$
#
# Type = 1 for temperature
#        2 for humidity
# Temperture value is in 0.01C resolution (divide by 100)
# Humidity is in 0.005% resolution (divide by 200)
#
# What about temperatures below 0C?
# How is negative value calculated? Is hex data signed?

"""
Hygrosens sensor output
Copyright 2005 by Brian C. Lane <bcl@brianlane.com>

"""

import os,sys
from binascii import *


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




def c2f(c):
    """
    Convert degrees C to degrees F
    """
    return ((c * 9.0)/5.0)+32.0
    
def f2c(f):
    """
    Convert degrees F to degrees C
    """
    return ((f-32) * 5.0)/9.0
                                
def c2k(c):
    """
    Convert degrees C to degrees Kelvin
    """
    raise Unimplemented
                                                    
def k2c(k):
    """
    Convert degrees Kelvin to degrees C
    """
    raise Unimplemented
                                                                        
def c2j(c):
    """
    Convert degrees C to joules
    """
    raise Unimplemented
                                                                                            
def j2c(j):
    """
    Convert joules to degrees C
    """
    raise Unimplemented

def checksum( line ):
    """
    Check the checksum of the received line
    """
    pass
    

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
    
    sensor = int(line[1:3])
    type   = int(line[3:5])
    family = int(line[5:7])
    serial = line[7:19]

    # Return a dictionary
    return { 'sensor' : sensor,
             'type'   : type,
             'family' : family,
             'serial' : serial
           }
    

def process_value( sensor, line ):
    """
    Parse the 'V' data for a temperature sensor (type 01)
    V11222233
    1 = Logical Channel Number
    2 = Measurement data
    3 = CRC
    """
    print line

    channel = int(line[1:3])
    value   = int(line[3:7],16)

    print "%02d  : %d" % (channel, value)

    if sensor['type'] == 1:
        # Temperature sensor
        print "Temperature = %7.2fC / %7.2fF" % (value / 100.0, c2f(value / 100.0))

    elif sensor['type'] == 2:
        # Humidity
        print "Humidity = %7.3f%%" % (value / 200.0)
    

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

