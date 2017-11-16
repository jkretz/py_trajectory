from netCDF4 import Dataset, num2date
import numpy as np
import pandas as pd
import os
from scipy import spatial
import datetime


date_flight = "20170531"

# set common timestamp
date_base = "20170531"
ts_base = datetime.datetime(int(date_base[0:4]), int(date_base[4:6]), int(date_base[6::]), 0, 0, 0)

##############################################################
# Reading flight track information from input file
##############################################################

#  read flight track
ipath_track = "/home_local/jkretzs/work_new/ac3/xcut/plane_model_trajectory/data/flight_track/"
file_name_track = "Flight_20170531_10_P5_1s.asc"
ifile_track = ipath_track+file_name_track
track = pd.read_csv(ifile_track, delim_whitespace=True).values

# time of fix of flight track into common timestep
t_track = track[:, 0]
ts_track = datetime.datetime(int(date_flight[0:4]), int(date_flight[4:6]), int(date_flight[6::]), 0, 0, 0)
t_track_ts = np.zeros_like(t_track)
for nt, time in enumerate(t_track):
    t_track_ts[nt] = ((ts_track+datetime.timedelta(seconds=time))-ts_base).total_seconds()

# lat/lon coordinates
lon_track = track[:, 2]
lat_track = track[:, 3]
p_track = track[:, 4]

flight_track = list(zip(lat_track, lon_track))

##############################################################
# Reading ICON input
##############################################################

first_read = True

ipath_icon = "/home_local/jkretzs/work_new/ac3/xcut/plane_model_trajectory/data/icon_data/data_test"
for file_name in sorted(os.listdir(ipath_icon)):

    # read in files
    if file_name.endswith(".nc"):
        ifile_icon = os.path.join(ipath_icon, file_name)

    icon_data = Dataset(ifile_icon)

    # get all variables in files
    var_list_all = icon_data.variables.keys()
    # var_list = var_list_all
    var_list = ['time', 'pres', 'temp', 'qi', 'qc', 'qv']

    # read data for the first time
    if first_read:
        # get grid information and transform into deg
        rad2deg = 180./np.pi
        lat_grid = np.array(icon_data.variables['clat'])*rad2deg
        lon_grid = np.array(icon_data.variables['clon'])*rad2deg
        
        var_in = {}
        var_info = {}

        # get variables
        var_in = {}
        var_info = {}

        for var in var_list:
            var_in[var] = icon_data.variables[var][:]
            for meta in 'units', 'long_name':
                if var == 'time' and meta == 'long_name':
                    continue
                var_info[var, meta] = icon_data.variables[var].getncattr(meta)

        first_read = False
        continue

    # now append next timestep
    for var in var_list:
        var_in[var] = np.concatenate((var_in[var], icon_data.variables[var][:]), axis=0)

# convert timesteps into the right format
if "time" in var_list:
    t_icon_ts = np.zeros_like(var_in["time"])
    for nt, time in enumerate(var_in["time"]):
        t_icon_ts[nt] = (num2date(time, var_info["time", "units"]) - ts_base).total_seconds()
    var_in["time_icon_ts"] = t_icon_ts

# open dataset
f_out = Dataset('test.nc', 'w', format='NETCDF4')
f_out.createDimension('time', len(flight_track))

# write time of flight track to file

time_out = f_out.createVariable('time', 'f4', 'time')
time_out.standard_name = "time"
time_out.units = "seconds since "+ts_base.strftime('%Y-%-m-%-d %H:%M:%S')
time_out.calendar = "proleptic_gregorian"
time_out[:] = t_track_ts

# create new vertical grid and write to file
p_level_inter = np.linspace(50000., 102000., num=53, dtype=float)
f_out.createDimension('p_level', len(p_level_inter))
p_out_grid = f_out.createVariable('p_level', 'f4', 'p_level')
p_out_grid.units = 'Pa'
p_out_grid.long_name = 'pressure_grid'
p_out_grid[:] = p_level_inter

# lat/lon/p
lat_out = f_out.createVariable('lat_track', 'f4', 'time')
lat_out.units = 'degrees_north'
lat_out.long_name = 'lat_flight_track'
lat_out[:] = lat_track

lon_out = f_out.createVariable('lon_track', 'f4', 'time')
lon_out.units = 'degrees_east'
lon_out.long_name = 'lon_flight_track'
lon_out[:] = lon_track

p_out = f_out.createVariable('p_track', 'f4', 'time')
p_out.units = 'Pa'
p_out.long_name = 'Pressure_track'
p_out[:] = p_track*100.

# apply kdtree decomposition and find closest location/time
tree = spatial.cKDTree(list(zip(lat_grid, lon_grid)))
idx = np.zeros_like(t_track_ts, dtype=np.int_)
idt = np.zeros_like(t_track_ts, dtype=np.int_)
for i_p, pts in enumerate(flight_track):
    idx[i_p] = tree.query(pts)[1]
    idt[i_p] = np.int(np.argmin(np.abs(var_in["time_icon_ts"]-t_track_ts[i_p])))

# set up some variables for the writing data to file
var_out = {}
p_icon = (var_in['pres'])[idt, :, idx]

# used ICON timestep into output
var = "time_ICON"
var_out[var] = f_out.createVariable(str(var), 'f4', 'time')
var_out[var].standard_name = "model_time"
var_out[var].units = "seconds since "+ts_base.strftime('%Y-%-m-%-d %H:%M:%S')
var_out[var].calendar = "proleptic_gregorian"
for i_p in range(0,len(flight_track)):
    var_out[var][i_p] = var_in["time_icon_ts"][idt[i_p]]

for var in var_list:


    # skip time variable
    if var == 'time':
        continue

    # 2D-variable
    if len(var_in[var].shape) == 2:
        # create variable in output file
        var_out[var] = f_out.createVariable(str(var), 'f4', 'time')
        var_out[var].units = var_info[var, 'units']
        var_out[var].long_name = var_info[var, 'long_name']

        # select variable on flight track
        for i_p in range(0, len(flight_track)):
            var_out[var][i_p] = (var_in[var])[idt[i_p], idx[i_p]]

    # 3D-variable
    elif len(var_in[var].shape) == 3:

        if var != 'pres':
            # create variable in output file
            var_out[var] = f_out.createVariable(str(var), 'f4', ('p_level', 'time'))
            var_out[var].units = var_info[var, 'units']
            var_out[var].long_name = var_info[var, 'long_name']

            # select variable on flight track and interpolate it onto new vertical grid
            var_pre_inter = (var_in[var])[idt, :, idx]
            for i_p in range(0, len(flight_track)):
                var_out[var][:, i_p] = np.interp(p_level_inter, p_icon[i_p, :], var_pre_inter[i_p, :])

    else:
        exit('strange variable dimension; exit')

f_out.close()

exit()
