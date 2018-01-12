import datetime
import os
import fnmatch
from setting_file import settings_in
from import_data import ImportICON, ImportPlane
from pro_data import ProData
from output_data import DataOutNetcdf


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

    for file in os.listdir(settings_in['ipath_plane']):
        if fnmatch.fnmatch(file, '*'+date_flight+'*.asc'):
            plane_file_list.append(settings_in['ipath_plane']+file)
    if not plane_file_list:
        print('WARNING: No flight track file found for day: '+date_flight)
        continue

    ipath_icon = settings_in['ipath_icon_base'] + (ts_base_date - datetime.timedelta(days=1)).strftime('%Y%m%d')
    if not (os.path.isdir(ipath_icon)):
        print('WARNING: No ICON data for day: '+date_flight)
        continue

    # import plane data and find the necessary ICON files
    plane_data = ImportPlane(ts_base_date, date_flight, plane_file_list, ipath_icon, settings_in['icon_file_string'])

    # now import ICON data
    in_data = ImportICON(ipath_icon, plane_data.icon_file_range, settings_in['var_icon'])

    # # loop through flight track files
    # for ifile_plane in ifiles_plane:
    #
    #     ifile_plane_split = ifile_plane.split('/')[-1].split('_')
    #     ofile = 'ICON_'+ifile_plane_split[1]+'_'+ifile_plane_split[2]+'_'+ifile_plane_split[3]+'.nc'
    #     print(date_flight)
    #
    #     # call import data class
    #     in_data = ImportData(date_flight, ts_base_date, ifile_plane, ipath_icon, settings_in['var_icon'],
    #                          settings_in['icon_file_string'])
    #
    #     # process data
    #     pro_data = ProData(in_data, settings_in['var_icon'], settings_in['dim_vert'])
    #
    #     # write data to netcdf file
    #     DataOutNetcdf(in_data, pro_data, settings_in['dim_vert'], settings_in['var_icon'], ofile,
    #                   settings_in['opath'])
    #
    #     del in_data, pro_data

exit('FINISH: icon_plane_trajectory.py')
