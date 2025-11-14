#import matplotlib
#matplotlib.use('agg')
#import matplotlib.pyplot as plt
from netCDF4 import Dataset
import numpy as np
import os, sys, dateutils, pygrib, cftime
from datetime import datetime

def getmean(diff,coslats):
    meancoslats = coslats.mean()
    return (coslats*diff).mean()/meancoslats

dateinit = '2025091500'
yyyy,mm,dd,hh = dateutils.splitdate(dateinit)

lat1 = 90; lat2 = 20. # NH
#lat1 = 20; lat2 = -20 # tropics
#lat1 = -20; lat2 = -90 # SH
#lat1 = 90; lat2 = -90 # global

era5_ds = Dataset('era5_z500_0p25deg.nc')
tvar = era5_ds['time']
tvarl = tvar[:].tolist()
dates_era5 = cftime.num2date(tvarl,units=tvar.units,calendar=tvar.calendar)
lats = era5_ds['latitude'][:]
lons = era5_ds['longitude'][:]
lons, lats = np.meshgrid(lons, lats)
coslats = np.cos(np.radians(lats))
latmask = np.logical_or(lats > lat1, lats < lat2)
coslats = np.ma.masked_array(coslats, mask=latmask)

grav = 9.8066

z500rms_ts = []
dates_ts = []  
for fh in range(6,241,6):

    date = dateutils.dateshift(dateinit,fh)
    cfdate = cftime.datetime(*dateutils.splitdate(date))
    tval = cftime.date2num(cfdate, units=tvar.units, calendar=tvar.calendar)
    nt = tvarl.index(tval)
    dval = cftime.num2date(tvar[nt], units=tvar.units, calendar=tvar.calendar)
    z500_era5 = era5_ds['geopotential'][nt]/grav

    # graphcast forecast.
    grbs=pygrib.open('graphcastgfs.t%02iz.pgrb2.0p25.f%03i.%04i%02i%02i' % (hh,fh,yyyy,mm,dd))
    grb = grbs.select(shortName='gh',level=500)[0]
    z500_graphcast = grb.values
    grbs.close()

    # ufs forecast.
    grbs=pygrib.open('FV3ATM_OUTPUT/GFSPRScorr_0p25deg.GrbF%02i' % fh)
    #grbs=pygrib.open('FV3ATM_OUTPUT_control/GFSPRS_0p25deg.GrbF%02i' % fh)
    grb = grbs.select(shortName='gh',level=500)[0]
    z500_ufs = grb.values
    #print(date,z500_era5.min(),z500_era5.max(),z500_graphcast.min(),z500_graphcast.max(),z500_ufs.min(),z500_ufs.max())
    grbs.close()


    z500err = z500_era5-z500_ufs
    z500err = np.ma.masked_array(z500err, mask=latmask)
    z500rms_ufs = np.ma.sqrt(getmean(z500err**2,coslats))
    z500err = z500_era5-z500_graphcast
    z500err = np.ma.masked_array(z500err, mask=latmask)
    z500rms_graphcast = np.ma.sqrt(getmean(z500err**2,coslats))
    z500err = z500_ufs-z500_graphcast
    z500err = np.ma.masked_array(z500err, mask=latmask)
    diffrms = np.ma.sqrt(getmean(z500err**2,coslats))
    #z500rms_ts.append(z500rms)
    #dates_ts.append(dval)
    print(fh,dval,z500rms_graphcast,z500rms_ufs,diffrms)
