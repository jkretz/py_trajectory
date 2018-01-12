import pandas as pd
import os
import datetime
import numpy as np
from netCDF4 import Dataset, num2date


class ImportPlane:

    def __init__(self, base_date, date, plane_file_list, ipath_icon, file_string):

        self.base_date = base_date
        self.flight_data = []
        self.icon_file_range = []

        t_min_max = np.empty(2*len(plane_file_list))

        # import plane data for all flights of a day
        for n_file, ifile_plane in enumerate(plane_file_list):
            out_flight, t_min_max[n_file*2], t_min_max[(n_file*2)+1] = self.plane_data_import(date, ifile_plane)
            self.flight_data.append(out_flight)

        # find range of need ICON files for a given day
        self.find_icon(ipath_icon, file_string, t_min_max)

    # import plane data for a given file
    def plane_data_import(self, date, ifile_plane):

        # read data
        plane_input = {}
        flight_data = {}

        input_file = pd.read_csv(str(ifile_plane), delim_whitespace=True).values
        plane_input["time"] = input_file[:, 0]
        plane_input["lon"] = input_file[:, 2]
        plane_input["lat"] = input_file[:, 3]
        flight_data["p"] = input_file[:, 4]

        # combine lat/lon into flight track
        flight_data["track"] = list(zip(plane_input["lat"], plane_input["lon"]))
        flight_data["lat"] = plane_input["lat"]
        flight_data["lon"] = plane_input["lon"]

        # convert timestep of flight track into common timestamp
        ts_track = datetime.datetime(int(date[0:4]), int(date[4:6]), int(date[6::]), 0, 0, 0)
        flight_data["time_new_ts"] = np.zeros_like(plane_input["time"])
        for nt, time in enumerate(plane_input["time"]):
            flight_data["time_new_ts"][nt] = ((ts_track+datetime.timedelta(seconds=time))-self.base_date)\
                .total_seconds()

        return flight_data, flight_data["time_new_ts"][0], flight_data["time_new_ts"][-1]

    # find largest and smallest timestep to only import needed files
    def find_icon(self, ipath_icon, file_string, t_min_max):

        icon_timestep_file = []
        icon_timestep_convert = []
        file_for_time = []

        for file_name in sorted(os.listdir(ipath_icon)):
            if file_name.startswith(file_string):
                ifile_icon = os.path.join(ipath_icon, file_name)
                icon_timestep_file.append(file_name)
            else:
                continue

            # now import timesteps and timestamp
            icon_timestep = []
            icon_data = Dataset(ifile_icon)
            icon_timestep = np.concatenate((icon_timestep, icon_data.variables["time"][:]), axis=0)
            icon_timestamp = icon_data.variables["time"].getncattr("units")

            # convert ICON timestep into common timestep
            for time in icon_timestep:
                icon_timestep_convert.append((num2date(time, icon_timestamp) - self.base_date).total_seconds())
                file_for_time.append(file_name)

        # get index of first ICON timestep in flight track
        t_dif_start = (np.array(icon_timestep_convert)-min(t_min_max))
        nt_dif_start = np.argmin(np.abs(t_dif_start))
        if t_dif_start[nt_dif_start] > 0:
            nt_dif_start = nt_dif_start - 1
            if nt_dif_start < 0:
                raise ValueError('First timestep of flight track not in ICON files, exiting.')  # is not working

        # get index of last ICON timestep in flight track
        t_dif_end = (np.array(icon_timestep_convert)-max(t_min_max))
        nt_dif_end = np.argmin(np.abs(t_dif_end))
        if t_dif_end[nt_dif_end] < 0:
            nt_dif_end = nt_dif_end + 1
            if nt_dif_end > len(icon_timestep_convert):
                raise ValueError('Last timestep of flight track not in ICON files, exiting.')  # is not working

        icon_files = file_for_time[nt_dif_start:nt_dif_end]
        self.icon_file_range = sorted(set(icon_files))


class ImportICON:

    def __init__(self, ipath_icon, icon_files, var_icon):

        self.ipath_icon = ipath_icon
        self.icon_files = icon_files
        self.icon_data = {}

        # hard code always needed variables and added desired ones
        self.icon_vars = ['time', 'pres']
        self.icon_vars = np.concatenate((self.icon_vars, var_icon))

        # some arrays needed later
        self.icon_data_info = {}

        self.read_icon_data()


    # read in all the data from the ICON files
    def read_icon_data(self):

        first_read = True
        for file_name in self.icon_files:

            print(file_name)

            ifile_icon = []
            # read only *.nc file
            if file_name.endswith(".nc"):
                ifile_icon = os.path.join(self.ipath_icon, file_name)
            icon_data_in = Dataset(ifile_icon)

            # read data for the first time to get the metadata only once
            if first_read:

                # get grid information and transform into deg
                rad2deg = 180./np.pi
                self.icon_data['lat_grid'] = np.array(icon_data_in.variables['clat'])*rad2deg
                self.icon_data['lon_grid'] = np.array(icon_data_in.variables['clon'])*rad2deg

                # loop through all the variables
                for var in self.icon_vars:
                    self.icon_data[var] = icon_data_in.variables[var][:]
                    for meta in 'units', 'long_name':
                        if var == 'time' and meta == 'long_name':
                            continue
                        self.icon_data_info[var, meta] = icon_data_in.variables[var].getncattr(meta)

                first_read = False
                continue

            # now append all the other timesteps
            for var in self.icon_vars:
                self.icon_data[var] = np.concatenate((self.icon_data[var], icon_data_in.variables[var][:]), axis=0)

            del icon_data_in
