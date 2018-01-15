import datetime
import os
import fnmatch
from setting_file import settings_in
from import_data import ImportICON, ImportPlane
from output_data import DataOutNetcdf


# set day range for multiple day
date_flights = []
if settings_in['lmulday']:
    date_flight_start = settings_in['range_start']
    date_flight_end = settings_in['range_stop']
    start = datetime.datetime(int(date_flight_start[0:4]), int(date_flight_start[4:6]),
                              int(date_flight_start[6::]), 0, 0, 0)
    end = datetime.datetime(int(date_flight_end[0:4]), int(date_flight_end[4:6]), int(date_flight_end[6::]), 0, 0, 0)

    delta = end - start
    for i in range(delta.days + 1):
        date_flights.append((start + datetime.timedelta(days=i)).strftime('%Y%m%d'))
else:
    date_flights.append(settings_in['date'])


# loop through days
for date_flight in date_flights:

    print('')
    print('Processing: '+date_flight)

    ts_base_date = datetime.datetime(int(date_flight[0:4]), int(date_flight[4:6]), int(date_flight[6::]), 0, 0, 0)
    plane_file_list = []

    # check if flight track file exists for chosen day
    for file in os.listdir(settings_in['ipath_plane']):
        if fnmatch.fnmatch(file, '*'+date_flight+'*.asc'):
            plane_file_list.append(settings_in['ipath_plane']+file)
    if not plane_file_list:
        print('WARNING: No flight track file found for day: '+date_flight)
        continue

    # check if ICON data exists for chosen day
    ipath_icon = settings_in['ipath_icon_base'] + (ts_base_date - datetime.timedelta(days=1)).strftime('%Y%m%d')
    if not (os.path.isdir(ipath_icon)):
        print('WARNING: No ICON data for day: '+date_flight)
        continue

    # import plane data and find the necessary ICON files
    plane_data = ImportPlane(ts_base_date, date_flight, plane_file_list, ipath_icon, settings_in['icon_file_string'])

    # now import ICON data
    in_data = ImportICON(ipath_icon, settings_in['var_icon'], plane_data)

    # write sampled data to file. For 3D data, interpolate on a new vertical grid
    DataOutNetcdf(plane_data, in_data)


exit('FINISH: icon_plane_trajectory.py')
