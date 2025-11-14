import xarray, gcsfs
from datetime import datetime
import numpy as np
def gs_get_mapper(path):
  fs = gcsfs.GCSFileSystem(project='neuralgcm')
  return fs.get_mapper(path)
era5_path = 'gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3'
full_era5_ds = xarray.open_zarr(gs_get_mapper(era5_path), chunks=None)
full_era5_ds = full_era5_ds['geopotential']
era5_ds = full_era5_ds.sel(time=slice('2025-09-01 00:00:00','2025-10-01 00:00:00'))
era5_ds = era5_ds.thin(time=6) # thin to every 6 hours
era5_ds = era5_ds.isel(level=21) # 500mb
era5_ds.to_netcdf('era5_z500_0p25deg.nc','w')
#if not (era5_ds['latitude'].diff('latitude') > 0).all():
#  # Ensure ascending latitude, 500 hpa only.
#  era5_ds = era5_ds.isel(latitude=slice(None, None, -1))
#new_lat = np.arange(-90,90.1,1.0)
#new_lon = np.arange(0,360,1.0)
#print(era5_ds)
#era5_ds_1deg = era5_ds.interp(latitude=new_lat, longitude=new_lon, assume_sorted=True)
#print(era5_ds_1deg)
#era5_ds_1deg.to_netcdf('era5_mslp_1deg.nc','w')
