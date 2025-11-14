import numpy as np
import pygrib, sys
from netCDF4 import Dataset

# hybrid coeffs for GFS levels 

ak = np.array([0.999, 1.605, 2.532, 3.924, 5.976, 8.947, 13.177, 19.096, 27.243, 38.276, 52.984, 72.293, 97.269, 129.11, 169.135, 218.767, 279.506, 352.894, 440.481, 543.782, 664.236, 803.164, 961.734, 1140.931, 1341.538, 1564.119, 1809.028, 2076.415, 2366.252, 2678.372, 3012.51, 3368.363, 3745.646, 4144.164, 4563.881, 5004.995, 5468.017, 5953.848, 6463.864, 7000., 7563.494, 8150.661, 8756.529, 9376.141, 10004.55, 10636.85, 11268.16, 11893.64, 12508.52, 13108.09, 13687.73, 14242.89, 14769.15, 15262.2, 15717.86, 16132.09, 16501.02, 16820.94, 17088.32, 17299.85, 17453.08, 17548.35, 17586.77, 17569.7, 17498.7, 17375.56, 17202.3, 16981.14, 16714.5, 16405.02, 16055.49, 15668.86, 15248.25, 14796.87, 14318.04, 13815.15, 13291.63, 12750.92, 12196.47, 11631.66, 11059.83, 10484.21, 9907.927, 9333.967, 8765.155, 8204.142, 7653.387, 7115.147, 6591.468, 6084.176, 5594.876, 5124.949, 4675.554, 4247.633, 3841.918, 3458.933, 3099.01, 2762.297, 2448.768, 2158.238, 1890.375, 1644.712, 1420.661, 1217.528, 1034.524, 870.778, 725.348, 597.235, 485.392, 388.734, 306.149, 236.502, 178.651, 131.447, 93.74, 64.392, 42.274, 26.274, 15.302, 8.287, 4.19, 1.994, 0.81, 0.232, 0.029, 0., 0., 0.])
bk = np.array([0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 0., 1.018e-05, 8.141e-05, 0.00027469, 0.00065078, 0.00127009, 0.00219248, 0.00347713, 0.00518228, 0.00736504, 0.0100812, 0.01338492, 0.01732857, 0.02196239, 0.02733428, 0.03348954, 0.04047056, 0.04831661, 0.05706358, 0.06674372, 0.07738548, 0.08900629, 0.101594, 0.1151262, 0.1295762, 0.1449129, 0.1611008, 0.1780999, 0.195866, 0.2143511, 0.2335031, 0.2532663, 0.2735822, 0.294389, 0.3156229, 0.337218, 0.3591072, 0.3812224, 0.4034951, 0.4258572, 0.4482413, 0.4705813, 0.492813, 0.5148743, 0.5367062, 0.5582525, 0.5794605, 0.6002815, 0.6206707, 0.6405875, 0.6599957, 0.6788633, 0.6971631, 0.714872, 0.7319713, 0.7484465, 0.7642871, 0.7794867, 0.7940422, 0.8079541, 0.8212263, 0.8338652, 0.8458801, 0.8572826, 0.8680866, 0.8783077, 0.8879632, 0.8970718, 0.9056532, 0.9137284, 0.9213187, 0.9284464, 0.9351338, 0.9414037, 0.9472789, 0.9527821, 0.957936, 0.962763, 0.9672851, 0.971524, 0.9755009, 0.9792364, 0.9827508, 0.9860625, 0.9891851, 0.9921299, 0.9949077, 0.9975282, 1.])

# constants
rd = 2.8705e+2
cp = 1.0046e+3
kap = rd/cp
kapr = cp/rd
kap1 = kap + 1.0

filename_gcast = sys.argv[1]
filename_gfs = sys.argv[2]
filename_inc = sys.argv[3]

zero_qinc=True

def read_array(grbs, shortName, typeOfLevel="isobaricInhPa", levs=None):
    data_list = []
    levs_list = []
    if levs is None:
        grbs_selected = grbs.select(shortName=shortName, typeOfLevel=typeOfLevel)
    else: 
        grbs_selected = grbs.select(shortName=shortName, typeOfLevel=typeOfLevel, level=levs)
    for grb in grbs_selected:
        levs_list.append(grb.level)
        data_list.append(grb.values)
    return np.asarray(data_list), np.asarray(levs_list)

# read 0.25 degree graphcast forecast data 
grbs = pygrib.open(filename_gcast)
t, plevs = read_array(grbs,'t')
u, plevs = read_array(grbs,'u')
v, plevs = read_array(grbs,'v')
q, plevs = read_array(grbs,'q')

grb_mslp = grbs.select(shortName='prmsl')[0]
lats, lons = grb_mslp.latlons()

# read 0.25 degree GFS forecast data
grbs = pygrib.open(filename_gfs)
t2, plevs2 = read_array(grbs, 't', levs=plevs)
u2, plevs2 = read_array(grbs, 'u', levs=plevs)
v2, plevs2 = read_array(grbs, 'v', levs=plevs)
q2, plevs2 = read_array(grbs, 'q', levs=plevs)
grb_mslp2 = grbs.select(shortName='prmsl')[0]
lats2, lons2 = grb_mslp2.latlons()
if np.max(np.abs(lats2-lats)) > 1.e-4 or np.max(np.abs(lons2-lons)) > 1.e-4:
    print('max diff lats,lons',(np.abs(lats2-lats)).max(), (np.abs(lons2-lons)).max())
    raise SystemExit('graphcast and GFS grids not the same!')
if np.max(np.abs(plevs2-plevs)) > 1.e-4:
    raise SystemExit('levels not the same!')
sp = (grbs.select(shortName='sp')[0]).values

# append 0.01 mb level (zero increment) and 1100mb level (same as 1000 mb).

plevs_list = plevs2.tolist()
press_data = 100.*np.array([0.01] + plevs_list + [1100.])

# create 3d pressure field
pressi = ak[:,np.newaxis,np.newaxis] + bk[:,np.newaxis,np.newaxis]*sp[np.newaxis,:,:]
press_target = 0.5*(pressi[:-1,:,:]+pressi[1:,:,:])
nlevs = press_target.shape[0]
nlats, nlons = sp.shape
for k in range(nlevs):
    # phillips vertical interpolation from guess_grids.F90 in GSI (used for global model)
    press_target[k] = ((pressi[k]**kap1-pressi[k+1]**kap1)/(kap1*(pressi[k]-pressi[k+1])))**kapr
    # linear in logp interpolation from interface pressures
    #press_target[k] = np.exp(0.5*(np.log(pressi[k])+np.log(pressi[k+1])))

# compute increments
t_inc = t-t2
u_inc = u-u2
v_inc = v-v2
q_inc = q-q2
print('u_inc min/max',u_inc.min(),u_inc.max())
print('v_inc min/max',v_inc.min(),v_inc.max())
print('t_inc min/max',t_inc.min(),t_inc.max())
print('q_inc min/max',q_inc.min(),q_inc.max())

#import matplotlib
#matplotlib.use('agg')
#import matplotlib.pyplot as plt
#fig=plt.figure()
#plt.subplot(2,1,1)
#nlev = (plevs2.tolist()).index(250)
#plt.imshow(u[nlev])
#plt.subplot(2,1,2)
#plt.imshow(u_inc[nlev],cmap='bwr',vmin=-25,vmax=25)
#plev_out = int(plevs_list[nlev])
#fig.suptitle('u %s mb' % plev_out)
#plt.savefig('u.png')
#raise SystemExit

def extend_array(arrin):
    # add array of zeros at top (0.01mb), persist lowest level (1000mb) to 1100mb.
    nlevs,nlats,nlons = arrin.shape
    arrout = np.zeros((nlevs+2,nlats,nlons),arrin.dtype)
    arrout[1:nlevs+1] = arrin
    arrout[nlevs+1] = arrin[-1]
    return arrout

u_inc = extend_array(u_inc)
v_inc = extend_array(v_inc)
t_inc = extend_array(t_inc)
q_inc = extend_array(q_inc)

# spectrally filter increments?

def get_indices_slope(press_target, press_input):
    log_press_target = np.log(press_target) # log pressure vert interp
    log_press_input = np.log(press_data)
    bin_indices = np.digitize(log_press_target, log_press_input)
    below = bin_indices-1
    above = bin_indices
    log_press_below = np.take_along_axis(log_press_input[:,np.newaxis,np.newaxis], below, axis=0)
    log_press_above = np.take_along_axis(log_press_input[:,np.newaxis,np.newaxis], above, axis=0)
    dlogp = log_press_above-log_press_below
    slope = (log_press_target - log_press_below)/(log_press_above-log_press_below)
    return below, above, slope

def vert_interp(a, below, above, slope):
    a_below = np.take_along_axis(a, below, axis=0)
    a_above = np.take_along_axis(a, above, axis=0)
    return a_below + (a_above - a_below)*slope

# interpolate to hybrid levels using GFS surface pressure

below, above, slope = get_indices_slope(press_target, press_data)
u_inc_out = vert_interp(u_inc, below, above, slope)
v_inc_out = vert_interp(v_inc, below, above, slope)
t_inc_out = vert_interp(t_inc, below, above, slope)
q_inc_out = vert_interp(q_inc, below, above, slope)

# write out to netcdf file 

# taper function for increments.
taper_vert = np.ones(t_inc_out.shape,t_inc.dtype)
ak_bot = 3000 # in Pa
ak_top = 1000
nlevsout = len(ak)-1
for k in range(nlevsout):
    if k > nlevsout/2 and ak[k] > ak_bot:
        taper_vert[k,...] = 1.
    elif k <= nlevsout/2 and (ak[k] <= ak_bot and ak[k] >= ak_top):
        taper_vert[k,...] = (ak[k] - ak_top)/(ak_bot - ak_top)
        if bk[k] > 0:
            msg = 'taper below pressure level region not allowed'
            raise ValueError(msg)
    elif k <= nlevsout/2 and ak[k] < ak_top:
        taper_vert[k,...] = 0.
    #print(k,ak[k],taper_vert[k,0,0])

# compute increments, write out to netcdf file.
# NOTE: increments assumed to go S->N, top->bottom
nc = Dataset(filename_inc,'w',format='NETCDF4_CLASSIC')
nc.createDimension('lat',nlats)
nc.createDimension('lon',nlons)
nc.createDimension('lev',nlevsout)
nc.createDimension('ilev',nlevsout+1)
lat = nc.createVariable('lat',np.float32,'lat')
lat.units = 'degrees north'
lon = nc.createVariable('lon',np.float32,'lon')
lon.units = 'degrees east'
lev = nc.createVariable('lev',np.float32,'lev')
ilev = nc.createVariable('ilev',np.float32,'ilev')
akv = nc.createVariable('ak',np.float32,'ilev')
bkv = nc.createVariable('bk',np.float32,'ilev')
akv[:] = ak[:]
bkv[:] = bk[:]
lat[:] = lats[::-1,0] # flip so lats go S to N.
lon[:] = lons[0,:]
lev[:] = np.arange(nlevsout)+1
ilev[:] = np.arange(nlevsout+1)+1
zlib = True # compress 3d vars?
u_inc = nc.createVariable('u_inc',np.float32,('lev','lat','lon'),zlib=zlib)
v_inc = nc.createVariable('v_inc',np.float32,('lev','lat','lon'),zlib=zlib)
tmp_inc = nc.createVariable('T_inc',np.float32,('lev','lat','lon'),zlib=zlib)
spfh_inc = nc.createVariable('sphum_inc',np.float32,('lev','lat','lon'),zlib=zlib)
inc = taper_vert*u_inc_out[:]
print('u increment min/max',inc.min(), inc.max())
u_inc[:] = inc[:,::-1,:] # flip lats so they go from S to N
inc = taper_vert*v_inc_out[:]
print('v increment min/max',inc.min(), inc.max())
v_inc[:] = inc[:,::-1,:]
inc = taper_vert*t_inc_out[:]
print('t increment min/max',inc.min(), inc.max())
tmp_inc[:] = inc[:,::-1,:]
inc = taper_vert*q_inc_out[:]
if zero_qinc:
    inc[:]=0
print('q increment min/max',inc.min(), inc.max())
spfh_inc[:] = inc[:,::-1,:]
