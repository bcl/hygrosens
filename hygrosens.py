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

#CREATE TABLE hygrosens (
#  ReadingKey bigint UNSIGNED NOT NULL auto_increment,
#  SerialNumber varchar(20) NOT NULL,
#  Channel int NOT NULL,
#  Type int NOT NULL,
#  Family int NOT NULL,
#  RecTime timestamp NOT NULL,
#  Value float NOT NULL,
#  PRIMARY KEY(SerialNumber),
#  KEY(ReadingKey),
#  KEY(RecTime),
#  KEY(Value),
#  KEY(Type),
#  KEY(Family)
#);
                
                  

"""
Hygrosens sensor output
Copyright 2005 by Brian C. Lane <bcl@brianlane.com>

"""

import os,sys
from binascii import *
import struct


try:
    import serial
except ImportError:
    print """
          Error importing the serial library. You need to make sure 
          that it is properly installed. The pyserial library is available
          from http://pyserial.sourceforge.net
          """
    sys.exit(-1)

try:
    import MySQLdb
except ImportError:
    print """
          Error importing MySQLdb module. You need to install the Python
          MySQL module if you want to store data in a MySQL database.
          """
    sys.exit(-1)
    

debug = 1

db_host = "localhost"
db_name = "hygrosens"
db_user = "hygrosens"
db_pass = "hygrosens"




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


def temperature( value ):
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
    channel = int(line[1:3])
    type   = int(line[3:5],16)
    family = int(line[5:7],16)
    serial = line[7:19]

    # Return a dictionary
    return { 'channel': channel,
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
    channel = int(line[1:3])
    value   = int(line[3:7],16)

    if debug > 1:
        print "%02d  : %d" % (channel, value)

    if sensor['type'] == 1:
        # Temperature sensor
#        print "Temperature = %7.2fC / %7.2fF" % (temperature(value), c2f(temperature(value)))
#        sys.stdout.write( ",%7.2f,%7.2f" % (temperature(value), c2f(temperature(value))) )
        return temperature(value)

    elif sensor['type'] == 2:
        # Humidity
#        print "Humidity = %7.3f%%" % (value / 200.0)
#        sys.stdout.write( ",%7.3f" % (value / 200.0) )
        return value / 200.0

    elif sensor['type'] == 0x53:
        # Dew Point
#        print "Dew Point = %7.2fC / %7.2fF" % (temperature(value), c2f(temperature(value)))
#        sys.stdout.write( ",%7.2f,%7.2f" % (temperature(value), c2f(temperature(value))) )
        return temperature(value)
        
    elif sensor['type'] == 0x55:
        # Absolute Humidity
#        print "Humidity = %7.2fg/m^3" % (value / 100.0)
#        sys.stdout.write( ",%7.2f" % (value / 100.0) )
        return value / 100.0
        
    elif sensor['type'] == 0x0A:
        # Light Sensor
#        print "Light = %d Lux" % (value)
#        sys.stdout.write( ",%d" % (value) )
        return value
        
    elif sensor['type'] == 3:
        # Air Pressure
        # IEEE Single Precision Float Value
        s = unhexlify(line[3:11])
        value = struct.unpack("!f", s)[0]
#        print "Pressure = %f Pascal" % (value)
#        sys.stdout.write( ",%f" % (value) )
        return value    

if __name__ == '__main__':
    """
    Test code to read the output continuously
    """


    # Connect to the database
    try:
        mydb = MySQLdb.Connect(host=db_host,user=db_user,passwd=db_pass,db=db_name)
    except:
        print "Problem connecting to database"
        raise
        sys.exit(-1)
            
    # Create a dictionary cursor
    db=mydb.cursor(MySQLdb.cursors.DictCursor)
            





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
            value = process_value( sensor, line )

#  (NULL,962F8D56E49B,1,1,1,NULL,22.470000)
#  SerialNumber varchar(20) NOT NULL,
#  Channel int NOT NULL,
#  Type int NOT NULL,
#  Family int NOT NULL,
#  RecTime timestamp NOT NULL,
#  Value float NOT NULL,
            
#            sql = "INSERT INTO hygrosens VALUES(NULL,%s,%d,%d,%d,NULL,%f)"
            sql = "INSERT INTO hygrosens VALUES(NULL,%s,%s,%s,%s,NULL,%s)"
            try:
                db.execute( sql, (sensor['serial'],sensor['channel'],sensor['type'],sensor['family'],value) )
            except:                
                sys.stderr.write( sql % (sensor['serial'],sensor['channel'],sensor['type'],sensor['family'],value) )
                sys.stderr.write( "\n" )
                raise
                
        elif line[0] == '@':
            sys.stdout.write("\n")
                
        line = ser.readline(eol='\r')
        
    ser.close()
