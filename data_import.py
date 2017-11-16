import pandas as pd
import os
import fnmatch
import datetime
import numpy as np
from netCDF4 import Dataset, num2date


class ImportData:

    def __init__(self, date, ts_base_date, ipath_plane, ipath_icon, var_icon):

        self.ipath_plane = ipath_plane
        self.ipath_icon = ipath_icon
        self.date = date
        self.base_date = ts_base_date

        # hard code always needed variables and added desired ones
        self.icon_vars = ['time', 'pres']
        self.icon_vars = np.concatenate((self.icon_vars, var_icon))

        # some arrays needed later
        self.flight_data = {}
        self.icon_data = {}
        self.icon_data_info = {}
        self.icon_files = []

        self.plane_data_import()
        self.find_icon_files()
        self.read_icon_data()

    # read flight track information from input file
    def plane_data_import(self):

        # find appropriate file for chosen day
        for file in os.listdir(self.ipath_plane):
                if fnmatch.fnmatch(file, '*'+self.date+'*.asc'):
                    ifile_plane = self.ipath_plane+file

        # read data
        plane_input = {}
        input_file = pd.read_csv(ifile_plane, delim_whitespace=True).values
        plane_input["time"] = input_file[:, 0]
        plane_input["lon"] = input_file[:, 2]
        plane_input["lat"] = input_file[:, 3]
        self.flight_data["p"] = input_file[:, 4]

        # combine lat/lon into flight track
        self.flight_data["track"] = list(zip(plane_input["lat"], plane_input["lon"]))

        # convert timestep of flight track into common timestamp
        ts_track = datetime.datetime(int(self.date[0:4]), int(self.date[4:6]), int(self.date[6::]), 0, 0, 0)
        self.flight_data["time_new_ts"] = np.zeros_like(plane_input["time"])
        for nt, time in enumerate(plane_input["time"]):
            self.flight_data["time_new_ts"][nt] = ((ts_track+datetime.timedelta(seconds=time))-self.base_date)\
                .total_seconds()

    # find the necessary ICON files before reading in all the data
    def find_icon_files(self):

        icon_timestep = []
        icon_timestep_file = []

        for file_name in sorted(os.listdir(self.ipath_icon)):

            # read only *.nc file
            if file_name.endswith(".nc"):
                ifile_icon = os.path.join(self.ipath_icon, file_name)

            # now import timesteps and timestamp
            icon_data = Dataset(ifile_icon)
            icon_timestep = np.concatenate((icon_timestep, icon_data.variables["time"][:]), axis=0)
            icon_timestamp = icon_data.variables["time"].getncattr("units")

            # make list of filenames depending on number of timesteps per file
            for _ in range(len(icon_data.variables["time"][:])):
                icon_timestep_file.append(file_name)

        # convert ICON timestep into common timestep
        icon_timestep_convert = []
        for time in icon_timestep:
            icon_timestep_convert.append((num2date(time, icon_timestamp) - self.base_date).total_seconds())

        # get index of first ICON timestep in flight track
        t_dif_start = (icon_timestep_convert-self.flight_data["time_new_ts"][0])
        nt_dif_start = np.argmin(np.abs(t_dif_start))
        if t_dif_start[nt_dif_start] < 0:
            nt_dif_start = nt_dif_start - 1
            if nt_dif_start < 0:
                raise ValueError('First timestep of flight track not in ICON files, exiting.')  # is not working

        # get index of last ICON timestep in flight track
        t_dif_end = (icon_timestep_convert-self.flight_data["time_new_ts"][-1])
        nt_dif_end = np.argmin(np.abs(t_dif_end))
        if t_dif_end[nt_dif_end] > 0:
            nt_dif_end = nt_dif_end + 1
            if nt_dif_end > len(icon_timestep):
                raise ValueError('Last timestep of flight track not in ICON files, exiting.')  # is not working

        self.icon_files = icon_timestep_file[nt_dif_start:nt_dif_end]

    # read in all the data from the ICON files
    def read_icon_data(self):

        first_read = True
        for file_name in self.icon_files:

            # read only *.nc file
            if file_name.endswith(".nc"):
                ifile_icon = os.path.join(self.ipath_icon, file_name)
            icon_data = Dataset(ifile_icon)

            # read data for the first time to get the metadata only once
            if first_read:

                # get grid information and transform into deg
                rad2deg = 180./np.pi
                self.icon_data['lat_grid'] = np.array(icon_data.variables['clat'])*rad2deg
                self.icon_data['lon_grid'] = np.array(icon_data.variables['clon'])*rad2deg

                # loop through all the variables
                for var in self.icon_vars:
                    self.icon_data[var] = icon_data.variables[var][:]
                    for meta in 'units', 'long_name':
                        if var == 'time' and meta == 'long_name':
                            continue
                        self.icon_data_info[var, meta] = icon_data.variables[var].getncattr(meta)

                first_read = False
                continue

            # now append all the other timesteps
            for var in self.icon_vars:
                self.icon_data[var] = np.concatenate((self.icon_data[var], icon_data.variables[var][:]), axis=0)
