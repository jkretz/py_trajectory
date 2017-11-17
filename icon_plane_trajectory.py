import datetime
from import_data import ImportData
from pro_data import ProData
from output_data import DataOutNetcdf

# set time of flight
date_flight = '20170531'

# set a common timestamp
base_date = '20170531'
ts_base_date = datetime.datetime(int(base_date[0:4]), int(base_date[4:6]), int(base_date[6::]), 0, 0, 0)

# path that contains airplane data
ipath_plane = '/home_local/jkretzs/work_new/ac3/xcut/plane_model_trajectory/data/flight_track/'

# path that contains ICON data
ipath_icon = "/home_local/jkretzs/work_new/ac3/xcut/plane_model_trajectory/data/icon_data/20170531"

# list of variables to be used
var_icon = ['qc', 'qi', 'qv', 'temp']

# number of output vertical levels
dim_vert = 100

# call import data class
in_data = ImportData(date_flight, ts_base_date, ipath_plane, ipath_icon, var_icon)

# process data
pro_data = ProData(in_data, var_icon, dim_vert)

# write data to netcdf file
DataOutNetcdf(in_data, pro_data, dim_vert, var_icon)

exit()
