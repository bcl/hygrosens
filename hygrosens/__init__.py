#!/usr/bin/python

# -------------------------------------------------------------------------
# Hygrosens Support Library
# Copyright 2005 by Brian C. Lane
# All rights Reserved
# Licensed under GPL v2, see the COPYRIGHT and COPYING files
# =========================================================================
# 02/20/2005   Putting all the pices into a library.
# bcl          Need to add checksum function
#              Need to test with freezing temperatures
#              Core of this will be to grab a @/$ pass and return a
#              hash of all the readings.
#          ?   Are channel numbers integers 00-16 or hex?
# -------------------------------------------------------------------------
"""
Hygrosens sensor output
Copyright 2005 by Brian C. Lane <bcl@brianlane.com>
All Rights Reserved

Requires the pyserial library from http://pyserial.sourceforge.net
"""
import os,sys
from binascii import *
import struct

from exceptions import *

try:
    import serial
except ImportError:
    print """
          Error importing the serial library. You need to make sure 
          that it is properly installed. The pyserial library is available
          from http://pyserial.sourceforge.net
          """
    sys.exit(-1)


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



class hygrosens:
    """
    Hygrosens Class
    """
    def __init__(self,debug=0, port='/dev/ttyS0', timeout=0.1):
        """
        Initialize the connection to the Hygrosens device
        """
        self.ser = serial.Serial( port, 4800 )
        self.ser.setRtsCts(0)
        self.ser.setXonXoff(0)
        self.ser.setRTS(1)
        self.ser.setDTR(1)
        self.debug = debug

    def checksum( self, line ):
        """
        Check the checksum of the received line of data

        I need to write this. For now return true.
        """
        return True


    def temperature( self, value ):
        """
        Convert Hygrosens signed 16 bit integer value to signed
        temperature value
        """
        if value <0x8000:
            # Positive Temperature
            return value/100.0
        else:
            # 2's complement negative value
            return -1 * (0x10000 - value)/100.0


    def process_sensor( self, line ):
        """
        Parse the 'I' serial number, type and check the checksum
        I11223344444444444455
        1 = Logical channel number 01 to 16
        2 = Sensor Type
        3 = Family Type
        4 = Serial number
        5 = CRC
        
        Returns a dictionary of:
          'channel'
          'type'
          'family'
          'serial'

        Raises a 'CRCError' if the checksum fails to match
        """
        if not self.checksum(line):
            raise CRCError

        channel = int(line[1:3])
        type   = int(line[3:5],16)
        family = int(line[5:7],16)

        # Dew Point and Humidity don't have serial numbers
        if type not in [0x53,0x55]:
            serial = line[7:19]
        else:
            serial = "NA"

        # Return a dictionary of the sensor info
        return { 'channel': channel,
                 'type'   : type,
                 'family' : family,
                 'serial' : serial
               }
    

    def process_value( self, sensor, line ):
        """
        Parse the 'V' data for a temperature sensor (type 01)
        V11222233
        1 = Logical Channel Number
        2 = Measurement data
        3 = CRC

        Must pass the sensor type dictionary returned from process_sensor

        Returns the value for this channel

        Raises a 'CRCError' if the checksum fails to match
        """
        if not self.checksum(line):
            raise CRCError

        channel = int(line[1:3])
        value   = int(line[3:7],16)

        if self.debug > 1:
            print "%02d  : %d" % (channel, value)

        if sensor['type'] == 1:
            # Temperature sensor
            return self.temperature(value)

        elif sensor['type'] == 2:
            # Humidity
            return value / 200.0

        elif sensor['type'] == 0x53:
            # Dew Point
            return self.temperature(value)
        
        elif sensor['type'] == 0x55:
            # Absolute Humidity
            return value / 100.0
        
        elif sensor['type'] == 0x0A:
            # Light Sensor
            return value
        
        elif sensor['type'] == 3:
            # Air Pressure
            # IEEE Single Precision Float Value
            s = unhexlify(line[3:11])
            value = struct.unpack("!f", s)[0]
            return value    


    def read_all(self):
        """
        Capture all the sensor readings and return an array of
        the responses to the calling routine.
        
        This function waits for a complete @/$ output cycle from the
        Hygrosens device, only returning when it is finished or 
        times out.
        """

        # Wait for '@' from the device
        line = self.ser.readline(eol='\r')            
        if not line:
            raise ReadTimeout, "Timeout reading Hygrosens device"
        while line[0] != '@':
            line = self.ser.readline(eol='\r')            
            if not line:
                raise ReadTimeout, "Timeout reading Hygrosens device"

        if self.debug > 0:
            sys.stderr.write("GOT: %s\n" % (line))
            sys.stderr.write("Found '@', starting to process sensors\n")

        results = {}            
        # Process incoming data until '$' is received
        while line[0] != '$':
            if line[0] == 'I':
                # A new sensor report
                sensor = self.process_sensor( line );
            elif line[0] == 'V':
                # Value report for the sensor
                sensor['value'] = self.process_value( sensor, line )
                results[sensor['channel']] = sensor

            line = self.ser.readline(eol='\r')
            if not line:
                raise ReadTimeout, "Timeout reading Hygrosens device"

            if self.debug > 0:
                sys.stderr.write("GOT: %s\n" % (line))            
            
        # Return a hash of the results for all sensors
        return results


