from netCDF4 import Dataset
import numpy as np
import pandas as pd
import os
from scipy import spatial

first_read = True
# ifile_icon = {}
# var_list = {}

# read ICON input
ipath_icon = "/home_local/jkretzs/work_new/ac3/xcut/plane_model_trajectory/data/icon_data/"
for file_name in os.listdir(ipath_icon):

    # read in files
    if file_name.endswith(".nc"):
        ifile_icon = os.path.join(ipath_icon, file_name)

    icon_data = Dataset(ifile_icon)

    # read data for the first time
    if first_read:
        # get grid information and transform into deg
        rad2deg = 180./np.pi
        lat_grid = np.array(icon_data.variables['clat'])*rad2deg
        lon_grid = np.array(icon_data.variables['clon'])*rad2deg

        # get all variables in files
        var_list_all = icon_data.variables.keys()
        # var_list = var_list_all
        var_list = ['thb_s', 'u']
        var_in = {}
        var_info = {}
        for var in var_list:
            var_in[var] = icon_data.variables[var][:]
            for meta in 'units', 'long_name':
                var_info[var, meta] = icon_data.variables[var].getncattr(meta)
        first_read = False
        continue

    # now append next timestep
    for var in var_list:
        var_in[var] = np.concatenate((var_in[var], icon_data.variables[var][:]), axis=0)

# read flight track
ipath_flight_track = "/home_local/jkretzs/work_new/ac3/xcut/plane_model_trajectory/data/flight_kml/"

ifile_track = ipath_flight_track+"/acloud_polar5_flight_10_20170531.csv"
track = pd.read_csv(ifile_track).values
lat_track = track[:, 1]
lon_track = track[:, 0]
flight_track = list(zip(lat_track, lon_track))

# number of points during flight
num_track = track.shape[0]

# open dataset
f_out = Dataset('test.nc', 'w', format='NETCDF4')
f_out.createDimension('track', len(flight_track))

# write lat/lon to file
lat_out = f_out.createVariable('lat_track', 'f4', 'track')
lat_out.units = "degrees_north"
lat_out.long_name = 'lat_flight_track'
lon_out = f_out.createVariable('lon_track', 'f4', 'track')
lon_out.units = "degrees_east"
lon_out.long_name = 'lon_flight_track'

lat_out[:] = lat_track
lon_out[:] = lon_track

# apply kdtree decomposition
tree = spatial.cKDTree(list(zip(lat_grid, lon_grid)))

var_out = {}
first_w3d = True

for var in var_list:

    # 2D-variable
    if len(var_in[var].shape) == 2:
        # create variable in output file
        var_out[var] = f_out.createVariable(str(var), 'f4', 'track')
        var_out[var].units = var_info[var, 'units']
        var_out[var].long_name = var_info[var, 'long_name']
        # select variable on flight track
        for np, pts in enumerate(flight_track):
            idx = tree.query(pts)[1]
            var_out[var][np] = (var_in[var])[0, idx]

    # 3D-variable
    elif len(var_in[var].shape) == 3:

        # create vertical dimension if it is the first time to write it to file
        num_vertical = var_in[var].shape[1]
        if first_w3d:
            f_out.createDimension('height', num_vertical)
            first_w3d = False

        # create variable in output file
        var_out[var] = f_out.createVariable(str(var), 'f4', ('height', 'track'))
        var_out[var].units = var_info[var, 'units']
        var_out[var].long_name = var_info[var, 'long_name']
        # select variable on flight track
        for np, pts in enumerate(flight_track):
            idx = tree.query(pts)[1]
            var_out[var][:, np] = (var_in[var])[0, :, idx]

    else:
        exit('strange variable dimension; exit')

f_out.close()

exit()
