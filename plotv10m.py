import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import pygrib

grbs = pygrib.open('FV3ATM_OUTPUT_control/GFSFLX.GrbF96')
grbu10m = grbs.select(shortName='10u')[0]
grbv10m = grbs.select(shortName='10v')[0]
v10m = np.sqrt(grbu10m.values**2 + grbv10m.values**2)
lats, lons = grbu10m.latlons()
lats1d = lats[:,0]
lons1d = lons[0,:]
print(v10m.shape, v10m.min(), v10m.max())
fig=plt.figure(figsize=(20,6))
fig.add_subplot(1,3,1)
plt.pcolormesh(lons1d,lats1d,v10m[:-1,:-1],cmap="hot_r",vmin=0,vmax=25)
plt.xlim(280,350)
plt.ylim(10,80)
plt.xlabel('longitude')
plt.ylabel('latitude')
plt.title('UFS control',fontsize=18)

grbs = pygrib.open('graphcastgfs.t00z.pgrb2.0p25.f096.20250915')
grbu10m = grbs.select(shortName='10u')[0]
grbv10m = grbs.select(shortName='10v')[0]
v10m = np.sqrt(grbu10m.values**2 + grbv10m.values**2)
lats, lons = grbu10m.latlons()
lats1d = lats[:,0]
lons1d = lons[0,:]
print(v10m.shape, v10m.min(), v10m.max())
fig.add_subplot(1,3,2)
plt.pcolormesh(lons1d,lats1d,v10m[:-1,:-1],cmap="hot_r",vmin=0,vmax=25)
plt.xlim(280,350)
plt.ylim(10,80)
plt.xlabel('longitude')
plt.ylabel('latitude')
plt.title('Graphcast',fontsize=18)

#grbs = pygrib.open('FV3ATM_OUTPUT/GFSFLX.GrbF96')
grbs = pygrib.open('FV3ATM_OUTPUT_replayuvt/GFSFLX.GrbF96')
grbu10m = grbs.select(shortName='10u')[0]
grbv10m = grbs.select(shortName='10v')[0]
v10m = np.sqrt(grbu10m.values**2 + grbv10m.values**2)
lats, lons = grbu10m.latlons()
lats1d = lats[:,0]
lons1d = lons[0,:]
print(v10m.shape, v10m.min(), v10m.max())
fig.add_subplot(1,3,3)
plt.pcolormesh(lons1d,lats1d,v10m[:-1,:-1],cmap="hot_r",vmin=0,vmax=25)
plt.xlim(280,350)
plt.ylim(10,80)
plt.xlabel('longitude')
plt.ylabel('latitude')
#plt.title('UFS replay filt n=25 r=4 v10m',fontsize=18)
plt.title('UFS replay v10m',fontsize=18)

plt.tight_layout()
plt.savefig('v10m.png')
