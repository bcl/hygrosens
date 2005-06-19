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

db_host = 'localhost'
db_user = 'hygrosens'
db_pass = '1212kdurm'
db_name = 'htgrosens'

rrdtool_paths = ["/usr/bin/rrdtool","/usr/local/bin/rrdtool","/usr/local/rrdtool/bin/rrdtool"]
rrd_time = [ "-3hours", "-32hours", "-8days", "-5weeks", "-13months" ]
rrd_path     = "/home/brian/temperature/"
html_path    = "/home/brian/public_html/hygrosens/"

timefmt = '%Y-%m-%d %H:%M:%S'

debug = 1
##########################################################################
import string, os, sys, time



# ------------------------------------------------------------------------
def c2f( c ):
  f = 32.0 + ((c * 9.0) / 5.0)
  return f

def create_loadavg( rrd_file ):
    """
    Create the initial loadavg RRD file
    """
    
    if os.path.isfile( rrd_file ):
        print "%s exists, skipping creation" % (rrd_file)
    else:
        rrd_cmd = ( rrdtool_path, "create", rrd_file, 
                    "DS:load_1:GAUGE:600:U:U",
                    "DS:load_5:GAUGE:600:U:U",
                    "DS:load_15:GAUGE:600:U:U",
                    "DS:running:GAUGE:600:U:U",
                    "DS:total:GAUGE:600:U:U",
                    "RRA:AVERAGE:0.5:1:676",
                    "RRA:AVERAGE:0.5:6:672",
                    "RRA:AVERAGE:0.5:24:720",
                    "RRA:AVERAGE:0.5:288:730",
                    "RRA:MAX:0.5:1:676",
                    "RRA:MAX:0.5:6:672",
                    "RRA:MAX:0.5:24:720",
                    "RRA:MAX:0.5:288:797",
                  )

        if debug>0: 
            debug_print(rrd_cmd)
            
        rrd_string = ""
        for i in rrd_cmd:
            rrd_string = rrd_string + i + " "
        
        output = os.popen( rrd_string ).readlines()




# ------------------------------------------------------------------------
try:
    import MySQLdb
    use_sql = 1
except:
    sys.stderr.write("No MySQL database support. Skipping SQL database store.\n")
    use_sql = 0


# Find the rrdtool binary
rrdtool_path = ""
for path in rrdtool_paths:
    if os.path.isfile(path):
        rrdtool_path = path
        break
else:
    sys.stderr.write("No RRD Tool executable found at %s\n" % (rrdtool_path))
    sys.exit(-1)

try:
    from hygrosens import *
except:
    sys.stderr.write("Error importing the Hygrosens module. Is it installed?\n\n")
    sys.exit(-1)


# Connect to the Hygrosens device
try:    
    sensors = hygrosens(debug=0,port='/dev/ttyS0',timeout=5)
except:
    sys.stderr.write("Error opening the Hygosens device\n")
    sys.exit(-1)


# Read a single output from the attached Hygrosens sensors into the result
# dictionary
result = sensors.read_all()

# Connect to the database
if use_sql:
    try:
        mydb = MySQLdb.Connect(host=db_host,user=db_user,passwd=db_pass,db=db_name)
    except:
        print "Problem connecting to database"
        raise
        sys.exit(-1)

    cursor=mydb.cursor()

# Insert the results into the database and RRD tables
# 'value': 15, 'serial': '02A0A61C0100', 'type': 10, 'family': 0, 'channel': 5
for key in result.keys():
    print result[key]

    if use_sql == 1:
        sql = "INSERT INTO hygrosens VALUES(NULL, %s, %s, %s, %s, %s, %s)"
        sqltime = time.strftime( timefmt, time.time() )
        cursor.execute( sql, (sqltime, result['channel'], result['serial'], result['type'], result['family'], result['value']) );

    # Update the interface rrd
    rrd_data = "N:%0.2f"  % (result['value'])
    # Run rrdtool in as secure a fashion as possible
    rrd_file = rrd_path + os.sep + result['channel'] + ".rrd"
    rrd_cmd = ("rrdtool","update", rrd_file, rrd_data)
    if debug>0: 
        debug_print(rrd_cmd)
    pid = os.spawnv( os.P_NOWAIT, rrdtool_path, rrd_cmd)

    # Graph the data
    for graph_time in rrd_time:
        png_file = png_path + os.sep + result['channel'] + graph_time + ".png"

        in_print = " GPRINT:in_bits:MIN:\"%-8s %%8.2lf%%s \"" % (iface + " in")
        out_print = " GPRINT:out_bits:MIN:\"%-8s %%8.2lf%%s \"" % (iface + " out")
        width_str = "%d" % (width)
        height_str = "%d" % (height)

        rrd_cmd = ( rrdtool_path, " graph ", png_file, " --imgformat PNG",
                    " --start '", starttime, 
                    "' --end '", endtime, "'",
                    " --width ", width_str,
                    " --height ", height_str,
                    " DEF:in_bytes=", rrd_file, ":rx_bytes:AVERAGE",
                    " DEF:out_bytes=", rrd_file, ":tx_bytes:AVERAGE",
                    " CDEF:in_bits=in_bytes,8,*",
                    " CDEF:out_bits=out_bytes,8,*",
                    " AREA:in_bits#00FF00:'Input bits/s'",
                    " LINE1:out_bits#0000FF:'Output bits/s\\c'",
                    " COMMENT:\"              \"",
                    " COMMENT:\"           Min          Max          Avg         Last\\n\"",
                    " COMMENT:\"           \"",
                    in_print,
                    " GPRINT:in_bits:MAX:\" %8.2lf%s \"",
                    " GPRINT:in_bits:AVERAGE:\" %8.2lf%s \"",
                    " GPRINT:in_bits:LAST:\" %8.2lf%s \\n\"",
                    " COMMENT:\"           \"",
                    out_print,
                    " GPRINT:out_bits:MAX:\" %8.2lf%s \"",
                    " GPRINT:out_bits:AVERAGE:\" %8.2lf%s \"",
                    " GPRINT:out_bits:LAST:\" %8.2lf%s \\n\"",
                    " COMMENT:\"           \"",
                    " COMMENT:\"Last Updated ", ctime(), "\\c\""
                  )

        if debug>0: 
            debug_print(rrd_cmd)
                
        rrd_string = ""
        for i in rrd_cmd:
            rrd_string = rrd_string + i

        if debug>0: 
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


