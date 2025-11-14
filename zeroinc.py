from netCDF4 import Dataset
nc = Dataset("fv3_increment.nc","a")
nc['u_inc'][:] = 0.
nc['v_inc'][:] = 0.
nc['T_inc'][:] = 0.
nc['delp_inc'][:] = 0.
nc['delz_inc'][:] = 0.
nc['sphum_inc'][:] = 0.
nc['liq_wat_inc'][:] = 0.
nc['icmr_inc'][:] = 0.
nc['o3mr_inc'][:] = 0.
nc.close()
