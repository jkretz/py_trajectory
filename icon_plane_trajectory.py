import datetime
from data_import import ImportData
from pro_input import ProData

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
var_icon = ['thb_s', 'temp']
#var_icon = ['temp']
#var_icon = ['thb_s']

# call import data class
data = ImportData(date_flight, ts_base_date, ipath_plane, ipath_icon, var_icon)

# process data
ProData(data, var_icon)


exit()
