import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
z500err = np.loadtxt('z500err_replayuvt_filt30.out',usecols=(3,4,5))
fhrs = np.loadtxt('z500err_replayuvt_filt30.out',usecols=0)
plt.plot(fhrs,z500err[:,0],label='Graphcast')
plt.plot(fhrs,z500err[:,1],label='UFS')
plt.plot(fhrs,z500err[:,2],label='Difference')
plt.xlabel('forecast hour')
plt.ylabel('NH Z500 rms error')
plt.ylim(0,90)
plt.xlim(6,234)
plt.title('Replay UVT Filtered Increments')
plt.legend()
plt.savefig('z500err_replayuvt_filt30.png')
