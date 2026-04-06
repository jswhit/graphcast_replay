import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma
import os, sys, math
import scipy, dateutils, operator
from netCDF4 import Dataset
from scores.categorical import ThresholdEventOperator, BinaryContingencyManager
import xarray as xr

def create_conus_mask(lats, lons, lat1, lat2, lon1, lon2):
    lons2d, lats2d = np.meshgrid(lons, lats)
    maskconus = np.logical_and(np.logical_and(lats2d >= lat1, lats2d <= lat2), np.logical_and(lons2d >= lon1, lons2d <= lon2))
    latsmask = np.logical_and(lats >= lat1, lats <= lat2)
    latsubset = lats[latsmask]
    lonsmask = np.logical_and(lons >= lon1, lons <= lon2)
    lonsubset = lons[lonsmask]
    return maskconus, latsubset, lonsubset

# reads in data created by readprecip.py and plots FSS

date1 = '2025120100'
date2 = '2026013100'
fday = int(sys.argv[1])

threshold = float(sys.argv[2]) # mm

# verif region
#lat1=25; lat2=53
#lon1=-125; lon2=-67
lat1=25; lat2=60
lon1=-140; lon2=40

initdates = dateutils.daterange(date1,date2,24)
lons = None
ets_ufsc_mean = None

for nt, initdate in enumerate(initdates):

    yyyymmddi = initdate[0:8]
    yyyyi = yyyymmddi[0:4]; mmi = yyyymmddi[4:6]
    validdate = dateutils.dateshift(initdate, fday*24)
    yyyymmddv = validdate[0:8]
    yyyyv = yyyymmddv[0:4]; mmv = yyyymmddv[4:6]
    print('initial, valid dates: %s %s' % (initdate,validdate))

    if lons is None:
        print('reading in saved data from file...')
        ncin = Dataset('precip_fday%s_dj2526.nc' % fday)
        lons = ncin['lons'][:]
        lats = ncin['lats'][:]
        conusmask, latsconus, lonsconus = create_conus_mask(lats, lons, lat1, lat2, lon1, lon2)
        ny = len(latsconus); nx = len(lonsconus)
    if initdate != str(ncin['init_dates'][nt]):
        raise ValueError('init date mismatch, got %s expected %s' % str(ncin['init_dates'][nt]), initdate)
     
    precip_imerg = ncin['imerg'][nt]
    precip_verif = precip_imerg[conusmask].reshape(ny,nx)
    precip_verif_da = xr.DataArray(precip_verif,coords=[latsconus,lonsconus],dims=["lat","lon"])
    precip_ufs = ncin['ufs_control'][nt]
    precip_ufsc = precip_ufs[conusmask].reshape(ny,nx)
    precip_ufsc_da = xr.DataArray(precip_ufsc,coords=[latsconus,lonsconus],dims=["lat","lon"])
    precip_ufs = ncin['ufs_replay'][nt]
    precip_ufsr = precip_ufs[conusmask].reshape(ny,nx)
    precip_ufsr_da = xr.DataArray(precip_ufsr,coords=[latsconus,lonsconus],dims=["lat","lon"])
    precip_gcast = ncin['aigfs'][nt]
    precip_aigfs = precip_gcast[conusmask].reshape(ny,nx)
    precip_aigfs_da = xr.DataArray(precip_aigfs,coords=[latsconus,lonsconus],dims=["lat","lon"])
         
    print('IMERG min/max', precip_verif.min(), precip_verif.max())
    print('Control min/max', precip_ufsc.min(), precip_ufsc.max())
    print('Replay min/max', precip_ufsr.min(), precip_ufsr.max())
    print('AIGFS min/max', precip_aigfs.min(), precip_aigfs.max())

    event_operator = ThresholdEventOperator(default_event_threshold=threshold, default_op_fn=operator.gt)
    forecast_binary_ufsc, observed_binary = event_operator.make_event_tables(precip_ufsc_da, precip_verif_da)
    contingency_manager_ufsc = BinaryContingencyManager(forecast_binary_ufsc, observed_binary)
    #print(contingency_manager_ufsc.format_table())
    ets_ufsc = contingency_manager_ufsc.equitable_threat_score()
    bias_ufsc = contingency_manager_ufsc.bias_score()

    event_operator = ThresholdEventOperator(default_event_threshold=threshold, default_op_fn=operator.gt)
    forecast_binary_ufsr, observed_binary = event_operator.make_event_tables(precip_ufsr_da, precip_verif_da)
    contingency_manager_ufsr = BinaryContingencyManager(forecast_binary_ufsr, observed_binary)
    ets_ufsr = contingency_manager_ufsr.equitable_threat_score()
    bias_ufsr = contingency_manager_ufsr.bias_score()

    event_operator = ThresholdEventOperator(default_event_threshold=threshold, default_op_fn=operator.gt)
    forecast_binary_aigfs, observed_binary = event_operator.make_event_tables(precip_aigfs_da, precip_verif_da)
    contingency_manager_aigfs = BinaryContingencyManager(forecast_binary_aigfs, observed_binary)
    ets_aigfs = contingency_manager_aigfs.equitable_threat_score()
    bias_aigfs = contingency_manager_aigfs.bias_score()
    if ets_ufsc_mean is None:
        ets_ufsc_mean = ets_ufsc.item()/len(initdates)
        ets_ufsr_mean = ets_ufsr.item()/len(initdates)
        ets_aigfs_mean = ets_aigfs.item()/len(initdates)
        bias_ufsc_mean = bias_ufsc.item()/len(initdates)
        bias_ufsr_mean = bias_ufsr.item()/len(initdates)
        bias_aigfs_mean = bias_aigfs.item()/len(initdates)
    else:
        ets_ufsc_mean += ets_ufsc.item()/len(initdates)
        ets_ufsr_mean += ets_ufsr.item()/len(initdates)
        ets_aigfs_mean += ets_aigfs.item()/len(initdates)
        bias_ufsc_mean += bias_ufsc.item()/len(initdates)
        bias_ufsr_mean += bias_ufsr.item()/len(initdates)
        bias_aigfs_mean += bias_aigfs.item()/len(initdates)
print('fday, threshold, ets for ufsc,ufsr,aigfs = ',fday,threshold,ets_ufsc_mean,ets_ufsr_mean,ets_aigfs_mean)
print('fday, threshold, biass for ufsc,ufsr,aigfs = ',fday,threshold,bias_ufsc_mean,bias_ufsr_mean,bias_aigfs_mean)

ncin.close()
