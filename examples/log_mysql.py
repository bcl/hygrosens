#!/usr/bin/python

# Log Hygrosens readings to a MySQL database
# Copyright 2005 by Brian C. Lane
# All Rights Reserved
# Licensed under GPL v2, see the COPYRIGHT and COPYING files

"""
Hygrosens MySQL logging
Copyright 2005 by Brian C. Lane <bcl@brianlane.com>

SQL commands are in the hygrosens.sql file
"""

import os,sys
from binascii import *
import struct

# Output the SQL statements to stderr
debug = 1


try:
    import serial
except ImportError:
    sys.stderr.write("Error importing the serial library. You need to make sure that it is properly installed. The pyserial library is available from http://pyserial.sourceforge.net\n")
    sys.exit(-1)


try:
    from hygrosens import *
except:
    sys.stderr.write("Error importing the Hygrosens module. Is it installed?\n")
    sys.exit(-1)
    

try:
    import MySQLdb
except ImportError:
    sys.stderr.write("Error importing MySQLdb module. You need to install the Python MySQL module if you want to store data in a MySQL database.")
    sys.exit(-1)
    


# MySQL Database Connection 
db_host = "localhost"
db_name = "hygrosens"
db_user = "hygrosens"
db_pass = "hygrosens"


# Connect to the database
try:
    mydb = MySQLdb.Connect(host=db_host,user=db_user,passwd=db_pass,db=db_name)
except:
    sys.stderr.write("Problem connecting to database\n")
    sys.exit(-1)
            
# Create a dictionary cursor
db=mydb.cursor(MySQLdb.cursors.DictCursor)


# Connect to the Hygrosens device
try:    
    sensors = hygrosens(debug=0,port='/dev/ttyS0',timeout=5)
except:
    sys.stderr.write("Error opening the Hygosens device\n")
    sys.exit(-1)
    

# Do this forever
while 1:
    # Read the sensors as a hash of sensor info. The key is the channel number
    # Hash contains:
    #   channel
    #   type
    #   family
    #   serial
    #   value
    result = sensors.read_all()

    for key in result.keys():            
        sql = "INSERT INTO hygrosens VALUES(NULL,%s,%s,%s,%s,NULL,%s)"
        try:
            db.execute( sql, (result[key]['serial'],result[key]['channel'],result[key]['type'],result[key]['family'],result[key]['value']) )

            if debug > 0:
                sys.stderr.write( sql % (result[key]['serial'],result[key]['channel'],result[key]['type'],result[key]['family'],result[key]['value']) )
                sys.stderr.write( "\n" )

        except:                
            sys.stderr.write( sql % (result[key]['serial'],result[key]['channel'],result[key]['type'],result[key]['family'],result[key]['value']) )
            sys.stderr.write( "\n" )
            raise
