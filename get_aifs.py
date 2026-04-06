from ecmwfapi import ECMWFService
import sys, pygrib, os
def splitdate(yyyymmddhh):
    yyyy = int(yyyymmddhh[0:4])
    mm = int(yyyymmddhh[4:6])
    dd = int(yyyymmddhh[6:8])
    hh = int(yyyymmddhh[8:10])
    return yyyy,mm,dd,hh

# get aifs-single forecasts archived on MARS

# Initialize the service
server = ECMWFService("mars")

analdate=sys.argv[1]
YYYYMMDD = analdate[0:8]
YYYY,MM,DD,HH=splitdate(analdate)

request = {
    "class": "ai",
    "model": "aifs-single",
    "date": "%04i-%02i-%02i" % (YYYY,MM,DD),
    "time": "%02i:00:00" % HH,
    "expver": 1,
    "grid": "0.25/0.25",
    "levtype": "pl",
    "levelist": "50/100/150/200/250/300/400/500/600/700/850/925/1000",
    "param": "130/131/132/133",
    "step": "6/12/18/24/30/36/42/48/54/60/66/72/78/84/90/96/102/108/114/120/126/132/138/144/150/156/162/168/174/180/186/192/198/204/210/216/222/228/234/240",
    "type": "fc",
    "format": "grib2"
}

# Execute the request
server.execute(request, "aifs.tmp.grib2")

request = {
    "class": "ai",
    "model": "aifs-single",
    "date": "%04i-%02i-%02i" % (YYYY,MM,DD),
    "time": "%02i:00:00" % HH,
    "levtype": "sfc",
    "grid": "0.25/0.25",
    "expver":1,
    "param": "134/151/165/166/167/228228", # 129 is surface geopotential
    "step": "6/12/18/24/30/36/42/48/54/60/66/72/78/84/90/96/102/108/114/120/126/132/138/144/150/156/162/168/174/180/186/192/198/204/210/216/222/228/234/240",
    "type": "fc",
    "format": "grib2"
}

# Execute the request
server.execute(request, "aifs_sfc.tmp.grib2")

# concatenate files.
# Read the content of the second file
with open('aifs_sfc.tmp.grib2', 'rb') as file2:
    content2 = file2.read()
# Open the first file in append mode and write the second file's content
with open('aifs.tmp.grib2', 'ab') as file1:
    file1.write(content2)

# now separate into separate files by forecast hour
import pygrib
grbs = pygrib.open('aifs.tmp.grib2')
for fh in range(6,241,6):
    grbs.rewind()
    grbs_subset = grbs.select(forecastTime=fh)
    grbout = open("graphcastgfs.t%02iz.pgrb2.0p25.f%03i.%s" % (HH,fh,YYYYMMDD),'wb')
    for grb in grbs_subset:
        msg = grb.tostring()
        grbout.write(msg)
    grbout.close()
grbs.close()
os.remove('aifs.tmp.grib2')
os.remove('aifs_sfc.tmp.grib2')
