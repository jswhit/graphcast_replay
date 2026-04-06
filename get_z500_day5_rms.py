from netCDF4 import Dataset
import numpy as np
import os, sys, dateutils, pygrib, cftime
from datetime import datetime

def getmean(diff,coslats):
    meancoslats = coslats.mean()
    return (coslats*diff).mean()/meancoslats

date1 = '2025120100'
date2 = '2026013100'
dates = dateutils.daterange(date1,date2,24)
fh = 120.

lat1 = 90; lat2 = 20. # NH
#lat1 = 20; lat2 = -20 # tropics
#lat1 = -20; lat2 = -90 # SH
#lat1 = 90; lat2 = -90 # global

era5_ds = Dataset('era5_z500_1deg_dj2526.nc')
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
level = 500

z500rms1mean = 0; z500rms2mean = 0; z500rms3mean = 0
for dateinit in dates:
    yyyy,mm,dd,hh = dateutils.splitdate(dateinit)

    date = dateutils.dateshift(dateinit,fh)
    cfdate = cftime.datetime(*dateutils.splitdate(date))
    tval = cftime.date2num(cfdate, units=tvar.units, calendar=tvar.calendar)
    nt = tvarl.index(tval)
    dval = cftime.num2date(tvar[nt], units=tvar.units, calendar=tvar.calendar)

    z500_anal = era5_ds['geopotential'][nt,::-1,:]/grav

    # analysis (ufs control)
    #grbs=pygrib.open('../graphcast_replay_control_C384/1p00/pgrbanl.gfs.%s.grib2' % date)
    #grb = grbs.select(shortName='gh',level=level)[0]
    #z500_anal = grb.values
    #grbs.close()

    # forecast 1 (ufs control)
    grbs=pygrib.open('../graphcast_replay_control_C384/1p00/pgrbf%02i.gfs.%s.grib2' % (fh,dateinit))
    grb = grbs.select(shortName='gh',level=level)[0]
    z500_f1 = grb.values
    grbs.close()

    # forecast 2 (ufs replay)
    grbs=pygrib.open('1p00/pgrbf%02i.gfs.%s.grib2' % (fh,dateinit))
    grb = grbs.select(shortName='gh',level=level)[0]
    z500_f2 = grb.values
    grbs.close()

    # forecast 3 (ai model)
    grbs=pygrib.open('1p00_graphcast/pgrbf%02i.gfs.%s.grib2' % (fh,dateinit))
    grb = grbs.select(shortName='z',level=level)[0]
    z500_f3 = grb.values/9.8066
    grbs.close()

    #print(z500_anal.min(), z500_anal.max())
    #print(z500_f1.min(), z500_f1.max())
    #print(z500_f2.min(), z500_f2.max())

    z500err1 = np.ma.masked_array(z500_anal-z500_f1, mask=latmask)
    z500rms1 = np.ma.sqrt(getmean(z500err1**2,coslats))
    z500err2 = np.ma.masked_array(z500_anal-z500_f2, mask=latmask)
    z500rms2 = np.ma.sqrt(getmean(z500err2**2,coslats))
    z500err3 = np.ma.masked_array(z500_anal-z500_f3, mask=latmask)
    z500rms3 = np.ma.sqrt(getmean(z500err3**2,coslats))
    z500rms1mean += z500rms1/len(dates)
    z500rms2mean += z500rms2/len(dates)
    z500rms3mean += z500rms3/len(dates)
    print(fh,dval,z500rms1,z500rms2,z500rms3)

print('# UFS control: %5.2f UFS replay: %5.2f AIGFS: %5.2f' % (z500rms1mean,z500rms2mean,z500rms3mean))

era5_ds.close()
