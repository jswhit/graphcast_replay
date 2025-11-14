import matplotlib
matplotlib.use('agg')
import numpy as np
import pygrib, sys
import matplotlib.pyplot as plt
from spharm import Spharmt, getspecindx

def getvarspectrum(vrtspec,divspec,norm,indxm,indxn,ntrunc):
    varspect = np.zeros(ntrunc+1,np.float32)
    nlm = (ntrunc+1)*(ntrunc+2)//2
    for n in range(nlm):
        vrtmag = (vrtspec[n]*np.conj(vrtspec[n])).real
        divmag = (divspec[n]*np.conj(divspec[n])).real
        if indxm[n] == 0:
            varspect[indxn[n]] += norm[n]*vrtmag
            varspect[indxn[n]] += norm[n]*divmag
        else:
            varspect[indxn[n]] += 2.*norm[n]*vrtmag
            varspect[indxn[n]] += 2.*norm[n]*divmag
    return varspect

fhr = int(sys.argv[1])

grbs = pygrib.open('FV3ATM_OUTPUT/GFSPRScorr_0p25deg.GrbF%s' % fhr)
grb_u250 = grbs.select(shortName='u',level=250)[0]
grb_v250 = grbs.select(shortName='v',level=250)[0]
u250 = grb_u250.values
v250 = grb_v250.values
print(u250.min(), u250.max(), v250.min(), v250.max())
lats, lons = grb_u250.latlons()
nlats, nlons = lats.shape
print(nlats,nlons)
grbs.close()

grbs = pygrib.open('graphcastgfs.t00z.pgrb2.0p25.f%03i.20250915' % fhr)
grb_u250 = grbs.select(shortName='u',level=250)[0]
grb_v250 = grbs.select(shortName='v',level=250)[0]
u250gc = grb_u250.values
v250gc = grb_v250.values
grbs.close()

grbs = pygrib.open('FV3ATM_OUTPUT_control/GFSPRS_0p25deg.GrbF%s' % fhr)
grb_u250 = grbs.select(shortName='u',level=250)[0]
grb_v250 = grbs.select(shortName='v',level=250)[0]
u250c = grb_u250.values
v250c = grb_v250.values
grbs.close()

rsphere = 6.3712e6
ntrunc = nlats-1
sp = Spharmt(nlons,nlats,rsphere=rsphere,gridtype='regular')
indxm, indxn = getspecindx(ntrunc)
lap = -(indxn*(indxn+1.0)/rsphere**2).astype(np.float32)
ilap = np.zeros(lap.shape, np.float32)
ilap[1:] = 1./lap[1:]
kenorm = (-0.25*ilap).astype(np.float32)
vrtspec, divspec = sp.getvrtdivspec(u250,v250)
kespec = getvarspectrum(vrtspec,divspec,kenorm,indxm,indxn,ntrunc)

vrtspec, divspec = sp.getvrtdivspec(u250gc,v250gc)
kespec2 = getvarspectrum(vrtspec,divspec,kenorm,indxm,indxn,ntrunc)

vrtspec, divspec = sp.getvrtdivspec(u250c,v250c)
kespec3 = getvarspectrum(vrtspec,divspec,kenorm,indxm,indxn,ntrunc)

plt.loglog(np.arange(ntrunc+1),kespec,linewidth=2,\
        label='UFS replay')
plt.loglog(np.arange(ntrunc+1),kespec2,linewidth=2,\
        label='Graphcast')
plt.loglog(np.arange(ntrunc+1),kespec3,linewidth=2,\
        label='UFS control')
plt.legend()
plt.xlabel('total wavenumber')
plt.ylabel('kinetic energy')
plt.xlim(1,500)
plt.savefig('kespec.png')
