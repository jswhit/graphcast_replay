import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
import os, sys, math
import scipy, dateutils, pygrib
from netCDF4 import Dataset

def main():

    eval_radius_list = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0, 20.0] # degrees
    grid_size = 0.1  # degress
    date1 = '2025120100'
    date2 = '2026013100'
    fday = int(sys.argv[1])
    threshold = int(sys.argv[2])
    # verif region
    lat1=25; lat2=53
    lon1=-125; lon2=-67

    initdates = dateutils.daterange(date1,date2,24)
    lons = None
    fss_meanc = None
    fss_meanr = None
    fss_meang = None
    savedata = 'precip_fday%s_dj2526.nc' % fday
    #savedata = None # read in saved data
    print('forecast day = ',fday)
    print('threshold = ',threshold)
    print('eval_radius = ',eval_radius_list)

    for nt, initdate in enumerate(initdates):

        yyyymmddi = initdate[0:8]
        yyyyi = yyyymmddi[0:4]; mmi = yyyymmddi[4:6]
        validdate = dateutils.dateshift(initdate, fday*24)
        yyyymmddv = validdate[0:8]
        yyyyv = yyyymmddv[0:4]; mmv = yyyymmddv[4:6]
        print('initial, valid dates: %s %s' % (initdate,validdate))

        if savedata is None:
            if lons is None:
                print('reading in saved data from file...')
                ncin = Dataset('precip_fday%s_dj2526.nc' % fday)
                lons = ncin['lons'][:]
                lats = ncin['lats'][:]
                conusmask, latsconus, lonsconus = create_conus_mask(lats, lons, lat1, lat2, lon1, lon2)
                ny = len(latsconus); nx = len(lonsconus)
            if initdate != str(ncin['init_dates'][nt]):
                raise ValueError('init date mismatch, got %s expected %s' % str(ncin['init_dates'][nt]), initdate)
            precip_imerg = ncin['imerge'][nt]
            precip_verif = precip_imerg[conusmask].reshape(ny,nx)
            precip_ufs = ncin['ufs_control'][nt]
            precip_ufsc = precip_ufs[conusmask].reshape(ny,nx)
            precip_ufs = ncin['ufs_replay'][nt]
            precip_ufsr = precip_ufs[conusmask].reshape(ny,nx)
            precip_gcast = ncin['aigfs'][nt]
            precip_aigfs = precip_gcast[conusmask].reshape(ny,nx)
        else:
            # get IMERG verification data.
            url='https://gpm1.gesdisc.eosdis.nasa.gov/opendap/GPM_L3/GPM_3IMERGDL.07/%s/%s/3B-DAY-L.MS.MRG.3IMERG.%s-S000000-E235959.V07B.nc4' % (yyyyv,mmv,yyyymmddv)
            print('IMERGE URL:',url)
            nc=Dataset(url)
            if lons is None:
                lons = nc['lon'][:]
                lats = nc['lat'][:]
                conusmask, latsconus, lonsconus = create_conus_mask(lats, lons, lat1, lat2, lon1, lon2)
                ny = len(latsconus); nx = len(lonsconus)
                ncout = Dataset(savedata,'w')
                londim = ncout.createDimension('lons',len(lons))
                latdim = ncout.createDimension('lats',len(lats))
                timedim = ncout.createDimension('init_dates',len(initdates))
                p_verif = ncout.createVariable('imerg',np.float32,(timedim,latdim,londim),zlib=True)
                p_ufsc = ncout.createVariable('ufs_control',np.float32,(timedim,latdim,londim),zlib=True)
                p_ufsr = ncout.createVariable('ufs_replay',np.float32,(timedim,latdim,londim),zlib=True)
                p_ufsg = ncout.createVariable('aigfs',np.float32,(timedim,latdim,londim))
                lonsv = ncout.createVariable('lons',np.float32,londim)
                latsv = ncout.createVariable('lats',np.float32,latdim)
                init_datesv = ncout.createVariable('init_dates',np.int32,timedim)
                lonsv[:] = lons; latsv[:] = lats
                init_datesv[:] = [int(d) for d in initdates] 
            precip_imerg = nc['precipitation'][:].T.squeeze()
            precip_verif = precip_imerg[conusmask].reshape(ny,nx)
            p_verif[nt] = precip_imerg
            nc.close()

            # get UFS replay data.
            grbfile = '0p1/pratefday%s.gfs.%s.grib2' % (fday, yyyymmddi)
            print("Replay GRIB: ",grbfile)
            grbs = pygrib.open(grbfile)
            grb = grbs.readline()
            print(grb)
            precip_ufs = grb.values*86400./8.
            for grb in grbs:
                print(grb)
                precip_ufs += grb.values*86400./8.
            precip_ufsr = precip_ufs[conusmask].reshape(ny,nx)
            p_ufsr[nt] = precip_ufs
            grbs.close()

            # get UFS control data.
            grbfile = '../graphcast_replay_control_C384/0p1/pratefday%s.gfs.%s.grib2' % (fday, yyyymmddi)
            print("Control GRIB: ",grbfile)
            grbs = pygrib.open(grbfile)
            grb = grbs.readline()
            print(grb)
            precip_ufs = grb.values*86400./8.
            for grb in grbs:
                print(grb)
                precip_ufs += grb.values*86400./8.
            precip_ufsc = precip_ufs[conusmask].reshape(ny,nx)
            p_ufsc[nt] = precip_ufs
            grbs.close()

            # get AIGFS data.
            grbfile = '0p1_graphcast/apcpfday%s.aigfs.%s.grib2' % (fday,initdate)
            print('AIGFS GRIB: ',grbfile)
            grbs = pygrib.open(grbfile)
            grb = grbs.readline()
            print(grb)
            precip_gcast = grb.values
            for grb in grbs:
                print(grb)
                precip_gcast += grb.values
            precip_aigfs = precip_gcast[conusmask].reshape(ny,nx)
            p_ufsg[nt] = precip_gcast
            grbs.close()

        print('IMERG min/max', precip_verif.min(), precip_verif.max())
        print('Control min/max', precip_ufsc.min(), precip_ufsc.max())
        print('Replay min/max', precip_ufsr.min(), precip_ufsr.max())
        print('AIGFS min/max', precip_aigfs.min(), precip_aigfs.max())

        # FSS for control
        fss_list = []
        for radius in eval_radius_list:
            # Calculate FSS
            FSS = calculate_fss(precip_ufsc, precip_verif, radius, grid_size, threshold)
            fss_list.append(FSS)
        if fss_meanc is None:
            fss_meanc = np.asarray(fss_list)/len(initdates)
        else:
            fss_meanc += np.asarray(fss_list)/len(initdates)

        # FSS for replay
        fss_list = []
        for radius in eval_radius_list:
            # Calculate FSS
            FSS = calculate_fss(precip_ufsr, precip_verif, radius, grid_size, threshold)
            fss_list.append(FSS)
        if fss_meanr is None:
            fss_meanr = np.asarray(fss_list)/len(initdates)
        else:
            fss_meanr += np.asarray(fss_list)/len(initdates)

        # FSS for AIGFS
        fss_list = []
        for radius in eval_radius_list:
            # Calculate FSS
            FSS = calculate_fss(precip_aigfs, precip_verif, radius, grid_size, threshold)
            fss_list.append(FSS)
        if fss_meang is None:
            fss_meang = np.asarray(fss_list)/len(initdates)
        else:
            fss_meang += np.asarray(fss_list)/len(initdates)

    if savedata is None:
        ncin.close()
    else:
        ncout.close()
    fss_dict = {}
    print('Control:',fss_meanc)
    fss_dict['UFS Control']=fss_meanc.tolist()
    print('Replay:',fss_meanr)
    fss_dict['UFS Replay']=fss_meanr.tolist()
    print('AIGFS:',fss_meang)
    fss_dict['AIGFS']=fss_meang.tolist()
    # Plot FSS for single threshold for varying eval radii
    plot_fss_versus_eval_radius(fss_dict, eval_radius_list, grid_size, fday, threshold)

def create_conus_mask(lats, lons, lat1, lat2, lon1, lon2):
    lons2d, lats2d = np.meshgrid(lons, lats)
    maskconus = np.logical_and(np.logical_and(lats2d >= lat1, lats2d <= lat2), np.logical_and(lons2d >= lon1, lons2d <= lon2))
    latsmask = np.logical_and(lats >= lat1, lats <= lat2)
    latsubset = lats[latsmask]
    lonsmask = np.logical_and(lons >= lon1, lons <= lon2)
    lonsubset = lons[lonsmask]
    return maskconus, latsubset, lonsubset

# Set data array to 1 at or above threshold, zero below it
# NOTE: this function takes an xarray DataArray as input and returns a numpy array.
def mask_data_array_based_on_threshold(da, threshold):
    # Convert the arrays to 2-D, removing the time dimension
    if (len(da.shape) == 3):
        da = da[0,:,:]

    return np.where(da >= threshold, 1, 0) 

# Create circular footprint for FSS calculation
def get_footprint(radius, grid_cell_size):
    radius_number_grid_cells = int(radius/grid_cell_size)

    # Obtain a square of zeros (with size length, in grid squares, of radius/grid_cell_size * 2 + 1)
    # circumscribing a circle of ones (with radius, in grid_squares, of radius/grid_cell_size)

    # 1) Create a footprint: just an array of 1s
    footprint = (np.ones((radius_number_grid_cells * 2 + 1, radius_number_grid_cells * 2 + 1))).astype(int)

    # 2) Set the centerpoint of the array to zero (needed for the subsequent distance calculation)
    footprint[int(math.ceil(radius_number_grid_cells)), int(math.ceil(radius_number_grid_cells))] = 0

    # 3) Within the footprint, calculate each point's distance from the center point
    dist = scipy.ndimage.distance_transform_edt(footprint, sampling = [grid_cell_size, grid_cell_size])

    # 4) Set the footprint to zeros where distance calculated in step 3) is greater than radius; keep it
    # set to one where distance is less than radius, obtaining the square of zeros circumscribing the circle of ones 
    return np.where(np.greater(dist, radius), 0, 1)

# FSS calculation from Craig Schwartz via Trevor Alcott
def calculate_fss(qpf, qpe, radius, grid_cell_size, threshold):
    # Calculate footprint, i.e., evaluation area
    footprint = get_footprint(radius, grid_cell_size)

    # Convert qpf and qpe arrays to numpy arrays containing 1s and 0s based on
    # whether precipitation amount is at or above or below threshold   
    binary_qpf =  mask_data_array_based_on_threshold(qpf, threshold)
    binary_qpe = mask_data_array_based_on_threshold(qpe, threshold)

    # Calculate forecast_fractions and observed fractions terms in the FSS formula.
    # These are the M (model) and O (observed) terms calculated in Roberts and Lean (2008) Equations 2 and 3
    # (https://doi.org/10.1175/2007MWR2123.1)
    # CONCEPTUAL PROCEDURE:
        # For every grid point, calculate the number of points within the footprint centered on the grid point
        # for which the binary_qpf and binary_qpe arrays equal 1 (i.e., <qpf> and <qpe> are at or above <threshold>).
        # Divide by the size of the footprint [np.sum(footprint)] to convert this number of points to a spatial
        # fraction of the footprint.
    # IMPLEMENTATION using fftconvolve:
        # I don't yet understand how fftconvolve calculates the number of points equal to one in each grid
        # point's neighborhood other than to state that it uses a Fast Fourier Transform (FFT) technique. 
    forecast_fractions = np.around(scipy.signal.fftconvolve(binary_qpf, footprint, mode = "same"))/np.sum(footprint)
    observed_fractions = np.around(scipy.signal.fftconvolve(binary_qpe, footprint, mode = "same"))/np.sum(footprint)

    # Calculate gridsize (Nx * Ny)
    gridsize = np.shape(qpe)[0] * np.shape(qpe)[1]

    # Calculate numerator [Equation 5 in Roberts and Lean (2008)]
    mse = 1/gridsize * np.sum((forecast_fractions - observed_fractions)**2)

    # Calculate denominator [Equation 7 in Roberts and Lean (2008)]
    mse_reference = 1/gridsize * (np.sum(forecast_fractions**2) + np.sum(observed_fractions**2))

    if (mse_reference > 0):
        return 1.0 - float(mse)/float(mse_reference)
    else:
        return np.nan 

# Plot against varying evaluation radii
def plot_fss_versus_eval_radius(fss_dict, eval_radius_list, grid_size, fday, threshold):
    # Create figure
    plt.figure(figsize = (12, 10))
    plt.title(f"FSS versus evaluation radius for threshold {threshold} mm (day {fday})", size = 15)
    plt.xlabel("Evaluation radius (degrees lat/lon)", size = 15)
    plt.ylabel("FSS", size = 15)
    plt.xlim(0, eval_radius_list[-1])
    plt.ylim(0, 1.0)
    plt.xticks(np.arange(0, eval_radius_list[-1] + 1, 1), fontsize = 15)
    plt.yticks(np.arange(0, 1.1, 0.1), fontsize = 15) 
    plt.grid(True, linewidth = 0.5)

    for dataset_name, fss_list in fss_dict.items():
        # Gather data to plot and plot data
        plt.plot(eval_radius_list, fss_list, linewidth = 2, label = dataset_name)

    # Save figure 
    plt.legend(loc = "best", prop = {"size": 15})
    plt.savefig('fss_day%s_threshold%smm.png' % (fday,threshold))

if __name__ == "__main__":
    main()
