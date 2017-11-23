import datetime
import os
import fnmatch
from import_data import ImportData
from pro_data import ProData
from output_data import DataOutNetcdf

# list of variables to be used
var_icon = ['thb_s']

# number of output vertical levels
dim_vert = 100

# path that contains airplane data 
ipath_plane = '/pf/b/b380425/icon/postpro/icon_acloud/flight_track/P5/'

# path that contains ICON data
ipath_icon_base = '/work/bb1037/b380425/ICON_AC3/output/'

# output path
opath = '/work/bb1037/b380425/ICON_AC3/output/ICON_acloud/' 

# set date of flight and set common timestep
date_flight = '20170531'
ts_base_date = datetime.datetime(int(date_flight[0:4]), int(date_flight[4:6]), int(date_flight[6::]), 0, 0, 0)

# find appropriate flight track file for chosen day
ifiles_plane = []
for file in os.listdir(ipath_plane):
    if fnmatch.fnmatch(file, '*'+date_flight+'*.asc'):
        ifiles_plane.append(ipath_plane+file)
if not ifiles_plane:
    exit('No flight track file found for day: '+date_flight)

# check if ICON data is available and get path
ipath_icon = ipath_icon_base + (ts_base_date - datetime.timedelta(days=1)).strftime('%Y%m%d')
if not (os.path.isdir(ipath_icon)):
    exit('No ICON data for day: '+date_flight)

# loop through flight track files
for ifile_plane in ifiles_plane:
    ofile = "ICON_"+ifile_plane[62:79]+".nc"

    # call import data class
    in_data = ImportData(date_flight, ts_base_date, ifile_plane, ipath_icon, var_icon)

    # process data
    pro_data = ProData(in_data, var_icon, dim_vert)

    # write data to netcdf file
    DataOutNetcdf(in_data, pro_data, dim_vert, var_icon, ofile , opath)

exit()
