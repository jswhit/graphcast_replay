import matplotlib
matplotlib.use('agg')
from netCDF4 import Dataset
import sys, pygrib
import matplotlib.pyplot as plt
import numpy as np
from dateutils import daterange
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.tri as tri
#yyyymmdd1 = sys.argv[1]+'00'
#yyyymmdd2 = sys.argv[2]+'00'
yyyymmdd1 = '2025120100'
yyyymmdd2 = '2025120100'
dates = daterange(yyyymmdd1,yyyymmdd2,24)
for date in dates:
    yyyymmdd = date[0:8]
    yyyy = yyyymmdd[0:4]; mm = yyyymmdd[4:6]
    url='https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDL.07/%s/%s/3B-DAY-L.MS.MRG.3IMERG.%s-S000000-E235959.V07B.nc4' % (yyyy,mm,yyyymmdd)
    print(yyyymmdd)
    print(url)
    nc=Dataset(url)
    #print(nc)
    #print(nc['lat'])
    lons = nc['lon'][:]
    lats = nc['lat'][:]
    precip_imerg = nc['precipitation'][:].T.squeeze()
    nc.close()
    grbfile = '0p1/pratefday1.gfs.%s.grib2' % yyyymmdd
    print(grbfile)
    grbs = pygrib.open(grbfile)
    grb = grbs.readline()
    print(grb)
    precip_ufs = grb.values*86400./8.
    for grb in grbs:
        print(grb)
        precip_ufs += grb.values*86400./8.
    grbs.close()
    grbfile = '0p1_graphcast/apcpfday1.aigfs.%s.grib2' % date
    print(grbfile)
    grbs = pygrib.open(grbfile)
    grb = grbs.readline()
    print(grb)
    precip_gcast = grb.values
    for grb in grbs:
        print(grb)
        precip_gcast += grb.values
    grbs.close()
    print(precip_imerg.min(), precip_imerg.max(), precip_imerg.shape)
    print(precip_ufs.min(), precip_ufs.max(), precip_ufs.shape)
    print(precip_gcast.min(), precip_gcast.max(), precip_gcast.shape)
    lons2d, lats2d = np.meshgrid(lons, lats)
    regionmask = np.logical_and(np.logical_and(lats2d >= 25, lats2d <= 53), np.logical_and(lons2d >= -125, lons2d <= -67))
    latsmask = np.logical_and(lats >= 25, lats <= 53)
    latsubset = lats[latsmask]
    ny = latsmask.sum()
    lonsmask = np.logical_and(lons >= -125, lons <= -67)
    lonsubset = lons[lonsmask]
    nx = lonsmask.sum()

    #fig=plt.figure(figsize=(6,8))
    #plt.subplot(2,1,1)
    #plt.imshow(precip_imerg[regionmask].reshape(ny,nx),cmap=plt.cm.terrain_r,vmin=0,vmax=100)
    #plt.title('IMERG')
    #plt.subplot(2,1,2)
    #plt.imshow(precip_ufs[regionmask].reshape(ny,nx),cmap=plt.cm.terrain_r,vmin=0,vmax=100)
    #plt.title('UFS AI REPLAY DAY 1')
    #plt.savefig('test.png')

    fig, axs = plt.subplots(3,1,figsize=(8,11),subplot_kw={'projection': ccrs.PlateCarree()})
    ax = axs[0]
    ax.coastlines(resolution='110m')
    ax.add_feature(cfeature.BORDERS, linestyle=":")
    clevs = np.arange(0,101,5)
    contour=ax.contourf(lonsubset,latsubset,precip_imerg[regionmask].reshape(ny,nx),levels=clevs,transform=ccrs.PlateCarree(),cmap=plt.cm.terrain_r)
    cbar = fig.colorbar(contour, ax=ax, orientation="vertical", shrink=0.75, label="precip")
    ax.set_title('IMERG')
    ax = axs[1]
    ax.coastlines(resolution='110m')
    ax.add_feature(cfeature.BORDERS, linestyle=":")
    clevs = np.arange(0,101,5)
    contour=ax.contourf(lonsubset,latsubset,precip_ufs[regionmask].reshape(ny,nx),levels=clevs,transform=ccrs.PlateCarree(),cmap=plt.cm.terrain_r)
    cbar = fig.colorbar(contour, ax=ax, orientation="vertical", shrink=0.75, label="precip")
    ax.set_title('UFS AI REPLAY DAY 1')
    ax = axs[2]
    ax.coastlines(resolution='110m')
    ax.add_feature(cfeature.BORDERS, linestyle=":")
    clevs = np.arange(0,101,5)
    contour=ax.contourf(lonsubset,latsubset,precip_gcast[regionmask].reshape(ny,nx),levels=clevs,transform=ccrs.PlateCarree(),cmap=plt.cm.terrain_r)
    cbar = fig.colorbar(contour, ax=ax, orientation="vertical", shrink=0.75, label="precip")
    ax.set_title('AIGFS DAY 1')
    plt.savefig('test.png')
