from netCDF4 import Dataset
import numpy as np
import pandas as pd
from scipy import spatial

# read ICON input
ipath = "/home_local/jkretzs/work_new/ac3/xcut/plane_model_trajectory/data/"
ifile_grid = ipath+"/grid/NWP_LAM_DOM01_20170531T120000Z_0024.nc"
in_grid = Dataset(ifile_grid)
rad2deg = 180./np.pi
lat_grid = np.array(in_grid.variables['clat'])*rad2deg
lon_grid = np.array(in_grid.variables['clon'])*rad2deg

thb_s = np.array(in_grid.variables['thb_s'])

# read flight track
ifile_track = ipath+"/flight_kml/acloud_polar5_flight_10_20170531.csv"
track = pd.read_csv(ifile_track).values
lat_track = track[:, 1]
lon_track = track[:, 0]
flight_track = list(zip(lat_track, lon_track))

f_out = Dataset('test.nc', 'w', format='NETCDF4')
f_out.createDimension('track', len(flight_track))
thb_s_track_out = f_out.createVariable('thb_s_track', 'f4', 'track')

tree = spatial.cKDTree(list(zip(lat_grid,lon_grid)))
thb_s_track = []
for pts in flight_track:
    idx = tree.query(pts)[1]
    thb_s_track = np.append(thb_s_track, thb_s[0, idx])

thb_s_track_out[:] = thb_s_track