import datetime
import os
import pytz
from setting_file import settings_in
from import_data import ImportPlane, ImportICON
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

    # check if ICON data exists for chosen day
    ts_base_date = datetime.datetime(int(date_flight[0:4]), int(date_flight[4:6]), int(date_flight[6::]), 0, 0, 0)
    ts_base_date = ts_base_date.replace(tzinfo=pytz.UTC)

    ipath_icon = settings_in['ipath_icon_base'] + ts_base_date.strftime('%Y%m%d')
    if not (os.path.isdir(ipath_icon)):
        print('WARNING: No ICON data for day: '+date_flight)
        continue

    # import plane data and find the necessary ICON files
    plane_data = ImportPlane(ts_base_date, settings_in['plane_file'], ipath_icon, settings_in['icon_file_string'])

    # import ICON data
    in_data = ImportICON(settings_in['var_icon'], plane_data, ts_base_date, settings_in['opath'], settings_in['num_sample'])

    # DataOutNetcdf(date_flight, ts_base_date, plane_data, in_data)

exit('FINISH: icon_plane_trajectory.py')
