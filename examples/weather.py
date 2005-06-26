#!/usr/bin/env python
# 
# Hygrosens Logging/Graphing application
# Copyright 2005 by Brian C. Lane <bcl@brianlane.com>
# http://www.brianlane.com/software/hygrosens/
#
# Requires Python MySQLdb module and Round Robin Database binaries
#
# Logs data to a MySQL database and to a RRDb graph log
# 
# 1. Read current sensors
# 2. Log to mysql database (if available)
# 3. Log to RRDB database
# 4. Generate graphs
# 5. Generate HTTP
# ------------------------------------------------------------------------
# Setup of PostgreSQL database
#   As the system postgres user execute the following:
#   createuser
#       Enter name of user to add: USERNAME
#       Shall the new user be allowed to create databases? (y/n) n
#       Shall the new user be allowed to create more new users? (y/n) n
#   createdb -O USERNAME hygrosens 
#   psql hygrosens < hygrosens.sql
#
# Substitute the system username that will be executing this program for
# the USERNAME parameters above.
# ------------------------------------------------------------------------

# DSN is "{host:{port}:}database{:user}{:password}".
# Note: Items between { } are optional.
dsn = '::hygrosens'

rrdtool_paths = ["/usr/bin/rrdtool","/usr/local/bin/rrdtool","/usr/local/rrdtool/bin/rrdtool"]
rrd_time = [ "-3hours", "-32hours", "-8days", "-5weeks", "-13months" ]


rrd_path     = "/home/bcl/rrdb"
html_path    = "/home/bcl/public_html/hygrosens"


timefmt = '%Y-%m-%d %H:%M:%S'

# Graph related settings
width  = 400
height = 100 

# debugging options for development
debug     = 0
debug_sql = 0
debug_rrd = 0

##########################################################################
import string, os, sys, time, traceback
from getopt import *

# ------------------------------------------------------------------------

def debug_print( text ):
    """
    Print debugging information to STDERR, including function namw and
    line number along with a message
    """
    module, line, function, info = traceback.extract_stack()[-2]
    sys.stderr.write( "%s (%s) : %s\n" % (function, line, text) )
                        
                        
def c2f( c ):
  f = 32.0 + ((c * 9.0) / 5.0)
  return f


def create_rrd( rrd_file ):
    """
    Create a RRD file for a single sensor
    """
    
    if os.path.isfile( rrd_file ):
        print "%s exists, skipping creation" % (rrd_file)
        return None
    else:
        rrd_cmd = ( rrdtool_path, "create", rrd_file, 
                    "DS:value:GAUGE:600:U:U",
                    "RRA:AVERAGE:0.5:1:676",
                    "RRA:AVERAGE:0.5:6:672",
                    "RRA:AVERAGE:0.5:24:720",
                    "RRA:AVERAGE:0.5:288:730",
                    "RRA:MAX:0.5:1:676",
                    "RRA:MAX:0.5:6:672",
                    "RRA:MAX:0.5:24:720",
                    "RRA:MAX:0.5:288:797",
                  )

        if debug_rrd>0: 
            debug_print(rrd_cmd)
            
        rrd_string = ""
        for i in rrd_cmd:
            rrd_string = rrd_string + i + " "
        
        output = os.popen( rrd_string ).readlines()


def setup_rrd(result):
    """
    Setup the rrd files for the attached Hygrosens devices
    """
    for key in result.keys():
        rrd_file = rrd_path + os.sep + str(result[key]['channel']) + ".rrd"
        create_rrd( rrd_file )


def setup_html(result):
    """
    Setup the html pages for the sensors detected
    """
    
    # Create individual pages first
    for key in result.keys():
        f = open( html_path + os.sep + str(result[key]['channel']) + ".html", "w" )
        f.write("<html><head><title>")
        f.write( sensors.sensor_type[result[key]['type']][0] )
        f.write('</title>\n<body bgcolor="white"><center>\n')

        for graph_time in rrd_time:
            png_file = str(result[key]['channel']) + graph_time + ".png"
            f.write('<img src="' + png_file + '"><p>\n')
        
        f.write("</body></html>\n")
        f.close()

    # Create index pages
    for graph_time in rrd_time:
        if( graph_time == '-3hours' ):
            index_name = "index.html"
        else:
            index_name = "index" + graph_time + ".html"
        f = open( html_path + os.sep + index_name, "w" )
        f.write("<html><head><title>Hygrosens Sensor Display</title></head>\n")
        f.write('<body bgcolor="white"><center>\n')
        
        f.write("<a href=\"index.html\">3 Hour View</a>&nbsp;<b>|</b>");
        f.write("<a href=\"index-32hours.html\">32 hour View</a>&nbsp;<b>|</b>");
        f.write("<a href=\"index-8days.html\">8 day View</a>&nbsp;<b>|</b>");
        f.write("<a href=\"index-5weeks.html\">5 week View</a>&nbsp;<b>|</b>");
        f.write("<a href=\"index-13months.html\">13 month View</a><p>");
                                    
        for key in result.keys():
            channel_html = str(result[key]['channel']) + ".html"
            f.write('<a href=' + channel_html + '>' )
            png_file = str(result[key]['channel']) + graph_time + ".png"
            f.write('<img src="' + png_file + '"></a><p>\n')
        f.write("</center></body></html>\n")
        f.close()
        

def usage():
    print """
    weather.py --graph|--setup|--html

    --graph   read the current sensor values, log to the SQL database
              and update the RRD graphs.
    --setup   generate rrd graph files for the current sensors and then
              execute --graph
    --html    generate html files for displaying the RRD graphs

    -c        Graph temperatures in Centigrade
    -f        Graph temperatures in Fahrenheit
    """ 
    

# ------------------------------------------------------------------------
try:
    from pyPgSQL import PgSQL
    use_sql = 1
except:
    debug_print("No PostgreSQL database support. Skipping SQL database store.\n")
    use_sql = 0


# Find the rrdtool binary
rrdtool_path = ""
for path in rrdtool_paths:
    if os.path.isfile(path):
        rrdtool_path = path
        break
else:
    debug_print("No RRD Tool executable found at %s\n" % (rrdtool_paths))
    sys.exit(-1)

try:
    from hygrosens import *
except:
    debug_print("Error importing the Hygrosens module. Is it installed?\n\n")
    sys.exit(-1)

# Process command line arguments
opts, args = getopt( sys.argv[1:], "cf", ["graph","setup","html"])

if not opts:
    usage()
    sys.exit(-1)

# Stuff the arguments into a dictionary        
command = {}
for i,value in opts:
    command[i] = value
            

# Connect to the Hygrosens device
try:    
    sensors = hygrosens(debug=0,port='/dev/ttyS0',timeout=5)
except:
    debug_print("Error opening the Hygosens device\n")
    sys.exit(-1)


# Read a single output from the attached Hygrosens sensors into the result
# dictionary
result = sensors.read_all()

if command.has_key('--setup'):
    setup_rrd(result)

if command.has_key('--html'):
    setup_html(result)

# Exit without logging when setting up rrd or html files
if command.has_key('--setup') or command.has_key('--html'):
    sys.exit(0)

# Connect to the database
if use_sql:
    try:
        mydb = PgSQL.connect(dsn)
    except:
        print "Problem connecting to database"
        raise
        sys.exit(-1)

    cursor=mydb.cursor()

# Insert the results into the database and RRD tables
# 'value': 15, 'serial': '02A0A61C0100', 'type': 10, 'family': 0, 'channel': 5
for key in result.keys():
    if debug>0:
        debug_print(result[key])

    if use_sql == 1:
        sql = "INSERT INTO hygrosens VALUES(%s, %s, %s, %s, %s, %s)"
        sqltime = time.strftime( timefmt, time.localtime() )
        cursor.execute( sql, (sqltime, result[key]['channel'], result[key]['serial'], result[key]['type'], result[key]['family'], result[key]['value']) );
        if debug_sql > 0:
            debug_print(sql % (sqltime, result[key]['channel'], result[key]['serial'], result[key]['type'], result[key]['family'], result[key]['value']))
        mydb.commit()
        
    # Update the interface rrd
    if result[key]['type'] == 1 and command.has_key("-f"):
        rrd_data = "N:%0.2f"  % (c2f(result[key]['value']))
    else:
        rrd_data = "N:%0.2f"  % (result[key]['value'])

    # Run rrdtool in as secure a fashion as possible
    rrd_file = rrd_path + os.sep + str(result[key]['channel']) + ".rrd"
    rrd_cmd = ("rrdtool","update", rrd_file, rrd_data)
    if debug_rrd>0: 
        debug_print(rrd_cmd)
    pid = os.spawnv( os.P_NOWAIT, rrdtool_path, rrd_cmd)

    # Graph the data for this sensor
    for graph_time in rrd_time:
        png_file = html_path + os.sep + str(result[key]['channel']) + graph_time + ".png"
        starttime = "%s" % (graph_time)
        endtime = "now"

        in_print = " GPRINT:value:MIN:\"%-8s %%8.2lf%%s \"" % (sensors.sensor_type[result[key]['type']][0])
        width_str  = "%d" % (width)
        height_str = "%d" % (height)
        
        rrd_cmd = ( rrdtool_path, " graph ", png_file, " --imgformat PNG",
                    " --start '", starttime, 
                    "' --end '", endtime, "'",
                    " --width ", width_str,
                    " --height ", height_str,
                    " DEF:value=", rrd_file, ":value:AVERAGE",
                    " LINE1:value#0000FF:'\\c'",
                    " COMMENT:\"              \"",
                    " COMMENT:\"           Min          Max          Avg         Last\\n\"",
                    " COMMENT:\"           \"",
                    in_print,
                    " GPRINT:value:MAX:\" %8.2lf%s \"",
                    " GPRINT:value:AVERAGE:\" %8.2lf%s \"",
                    " GPRINT:value:LAST:\" %8.2lf%s \\n\"",
                    " COMMENT:\"           \"",
                    " COMMENT:\"Last Updated ", sqltime, "\\c\""
                  )

        if debug_rrd>0: 
            debug_print(rrd_cmd)
                
        rrd_string = ""
        for i in rrd_cmd:
            rrd_string = rrd_string + i

        if debug_rrd>0: 
            debug_print(rrd_string)
                
        output = os.popen( rrd_string ).readlines()

        
if use_sql == 1:
    mydb.close()

# Write a new .signature file
#outfile = open('/home/user/.signature','w')
#sig = "--[Inside %0.1fF]--[Outside %0.1fF]--[Kermit %0.1fF]--[Coaster %0.1fF]--\n" % (c2f(rrd_sensors['Office'][1]),c2f(rrd_sensors['Attic'][1]),c2f(rrd_sensors['DS1822'][1]),c2f(rrd_sensors['Drink'][1]))
#outfile.write(sig)
#outfile.close()


# Write html


