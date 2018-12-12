from netCDF4 import Dataset
import os
import numpy as np
import pickle
from scipy import spatial
from scipy.stats import norm
import matplotlib.pyplot as plt

ifile_icon = '/media/jkretzs/intenso8tb/jkretzs/data/icon_acloud/tmp/20170602/NWP_LAM_DOM01_20170602T000000Z_0012.nc'
opath = '/home_local/jkretzs/work/scripts/python/icon_acloud/'

f_icon = Dataset(ifile_icon, 'r')
lat = f_icon.variables['clat'][:]
lon = f_icon.variables['clon'][:]
rad2deg = 180./np.pi
lat_deg = lat*rad2deg
lon_deg = lon*rad2deg


# apply kd-tree decomposition and save it to a file to speed things up when doing it the next time
kdtree_save_file = '.kdtree_save.p'
if os.path.isfile(opath+kdtree_save_file):
    tree = pickle.load(open(opath+kdtree_save_file, "rb"))
else:
    tree = spatial.cKDTree(list(zip(lat_deg, lon_deg)))
    pickle.dump(tree, open(opath+kdtree_save_file, "wb"))

lat_plane = 80.
lon_plane = 10.
track = (lat_plane, lon_plane)
idx = tree.query(track)[1]

# average grid size
grid_size = 1.2/2.
# earth's radius
re = 6371.0
# sample radius
rs = 5.

samples = []


for n in np.arange(10000):
    lats = np.degrees(2*rs/re * np.linspace(-0.5, 0.5, int(rs/grid_size)+1))
    pdf_y = np.cos((np.pi/2.) * np.linspace(-1., 1., int(rs/grid_size)+1))**2
    lat_sample = np.random.choice(lat_plane + lats, p=pdf_y/sum(pdf_y))

    lons = np.degrees(2*rs/(re*np.cos(np.radians(lat_sample))) * np.linspace(-0.5, 0.5, int(rs/grid_size)+1))
    pdf_x = np.cos((np.pi/2.) * np.linspace(-1., 1., int(rs/grid_size)+1))**2
    lon_sample = np.random.choice(lon_plane + lons , p=pdf_x/sum(pdf_x))

    point_sample = (lat_sample, lon_sample)
    idx_sample = tree.query(point_sample)[1]
    if idx_sample not in samples:
        samples.append(idx_sample)

plt.scatter(lon_deg[samples], lat_deg[samples])
plt.axis('equal')
plt.show()

exit()
