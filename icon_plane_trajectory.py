import datetime
import os
import fnmatch
from import_data import ImportData
from pro_data import ProData
from output_data import DataOutNetcdf

#######################################################################
# settings
####################################################################### 

# set date of flight and set common timestep

date_flights = ['20170531']

day_range = False
date_flight_start = '20170531'
date_flight_end = '20170630'

# list of variables to be used
var_icon = ['thb_s', 'thu_s', 'sou_s', 'sou_t', 'sob_s', 'qv', 'qc', 'qi', 'qr', 'qs', 'temp', 'tqv', 'tqc', 'tqi', 'tqr', 'tqs']

# number of output vertical levels
dim_vert = 100

# path that contains airplane data 
ipath_plane = '/pf/b/b380425/icon/postpro/icon_acloud/flight_track/all/'

# path that contains ICON data
ipath_icon_base = '/work/bb1037/b380425/ICON_AC3/output/'

# output path
opath = '/work/bb1037/b380425/ICON_AC3/output/ICON_acloud/' 

####################################################################### 
# end settings
####################################################################### 



if day_range:
    date_flights = []
    start = datetime.datetime(int(date_flight_start[0:4]), int(date_flight_start[4:6]), int(date_flight_start[6::]), 0, 0, 0)
    end = datetime.datetime(int(date_flight_end[0:4]), int(date_flight_end[4:6]), int(date_flight_end[6::]), 0, 0, 0)

    delta = end - start
    for i in range(delta.days + 1):
        date_flights.append((start + datetime.timedelta(days=i)).strftime('%Y%m%d'))

# loop through days
for date_flight in date_flights:
    
    print('')
    print('Processing: '+date_flight)
    
    ts_base_date = datetime.datetime(int(date_flight[0:4]), int(date_flight[4:6]), int(date_flight[6::]), 0, 0, 0)
    ifiles_plane = []

    for file in os.listdir(ipath_plane):
        if fnmatch.fnmatch(file, '*'+date_flight+'*.asc'):
            ifiles_plane.append(ipath_plane+file)
    if not ifiles_plane:
        print('WARNING: No flight track file found for day: '+date_flight)
        continue

    ipath_icon = ipath_icon_base + (ts_base_date - datetime.timedelta(days=1)).strftime('%Y%m%d')
    if not (os.path.isdir(ipath_icon)):
        print('WARNING: No ICON data for day: '+date_flight)
        continue

    # loop through flight track files
    for ifile_plane in ifiles_plane:
        ofile = "ICON_"+ifile_plane[62:79]+".nc"

        # call import data class
        in_data = ImportData(date_flight, ts_base_date, ifile_plane, ipath_icon, var_icon)

        # process data
        pro_data = ProData(in_data, var_icon, dim_vert)

        # write data to netcdf file
        DataOutNetcdf(in_data, pro_data, dim_vert, var_icon, ofile , opath)
        
        del in_data, pro_data

exit('FINISH: icon_plane_trajectory.py')
