import pandas as pd
import os
import datetime
import numpy as np
from netCDF4 import Dataset, num2date
from scipy import spatial
import pickle


# import class for aircraft data
class ImportPlane:

    def __init__(self, base_date, date, plane_file_list, ipath_icon, file_string):

        self.base_date = base_date
        self.flight_data = []
        self.icon_file_range = []
        self.icon_timestep_range = []
        self.plane_file_list = plane_file_list

        t_min_max = np.empty(2*len(self.plane_file_list))

        # import plane data for all flights of a day
        for n_file, ifile_plane in enumerate(self.plane_file_list):
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
        self.icon_timestep_range = np.array(icon_timestep_convert[nt_dif_start:nt_dif_end])


# import class for ICON data
class ImportICON:

    def __init__(self, ipath_icon, var_icon, plane_data, opath):

        self.ipath_icon = ipath_icon
        self.plane_data = plane_data
        self.icon_data = []
        self.opath = opath

        # hard code always needed variables and added desired ones
        self.icon_vars = ['time', 'pres', 'pres_sfc']
        self.icon_vars = np.concatenate((self.icon_vars, var_icon))

        # some arrays needed later
        self.icon_data_info = {}

        # import ICON grid and metadata
        icon_latlon = self.meta_import()

        # import ICON data on flight track
        self.icon_import(icon_latlon)

    def meta_import(self):

        # import ICON dataset
        ifile_icon = os.path.join(self.ipath_icon, self.plane_data.icon_file_range[0])
        icon_data_in = Dataset(ifile_icon)

        # get grid information and transform into deg
        icon_latlon = {}
        rad2deg = 180./np.pi
        icon_latlon['lat_grid'] = np.array(icon_data_in.variables['clat'])*rad2deg
        icon_latlon['lon_grid'] = np.array(icon_data_in.variables['clon'])*rad2deg

        # get variable meta data
        for var in self.icon_vars:
            for meta in 'units', 'long_name':
                if var == 'time' and meta == 'long_name':
                    continue
                self.icon_data_info[var, meta] = icon_data_in.variables[var].getncattr(meta)

        return icon_latlon

    # apply kd-tree decomposition and find gridpoints and timesteps closest to flight track
    def kd_tree(self, track, plane_time, icon_latlon):

        kdtree_save_file = '.kdtree_save.p'
        # apply kd-tree decomposition and save it to a file to speed things up when doing it the next time
        if os.path.isfile(self.opath+kdtree_save_file):
            tree = pickle.load(open(self.opath+kdtree_save_file, "rb"))
        else:
            tree = spatial.cKDTree(list(zip(icon_latlon['lat_grid'], icon_latlon['lon_grid'])))
            pickle.dump(tree, open(self.opath+kdtree_save_file, "wb"))

        icon_timestep = []
        for file_name in self.plane_data.icon_file_range:
            ifile_icon = os.path.join(self.ipath_icon, file_name)
            icon_data = Dataset(ifile_icon)
            icon_timestep = np.concatenate((icon_timestep, icon_data.variables["time"][:]), axis=0)

        # some empty arrays
        idx = np.zeros(len(track), dtype=np.int_)
        idt = np.zeros(len(track), dtype=np.int_)

        # find gridpoints and timesteps closest to flight track
        for i_p, pts in enumerate(track):
            idx[i_p] = tree.query(pts)[1]
            idt[i_p] = np.int(np.argmin(np.abs(self.plane_data.icon_timestep_range - plane_time[i_p])))

        return idx, idt

    def icon_import(self, icon_latlon):

        # loop through flights of chose day and only import data along the flight-track
        for n_flight in range(len(self.plane_data.flight_data)):

            icon_data_flight = {}

            # apply kd-tree decomposition to get the ICON grid indices along the flight track
            plane_time = self.plane_data.flight_data[n_flight]['time_new_ts']
            idx, idt = self.kd_tree(self.plane_data.flight_data[n_flight]['track'], plane_time, icon_latlon)

            for var in self.icon_vars:
                first_read = True
                icon_data_all = []
                for n_file, file_name in enumerate(self.plane_data.icon_file_range):
                    ifile_icon = os.path.join(self.ipath_icon, file_name)
                    if var in ('v_10m', 'u_10m', 'rh_2m', 't_2m'):
                        icon_data_in = Dataset(ifile_icon).variables[var][:, 0, :]
                    else:
                        icon_data_in = Dataset(ifile_icon).variables[var][:]

                    if first_read:
                        icon_data_all = icon_data_in
                        first_read = False
                    else:
                        icon_data_all = np.concatenate((icon_data_all, icon_data_in), axis=0)

                if var == 'time':
                    icon_data_inter = np.zeros(len(idx), dtype=np.float_)
                    for i_p in range(0, len(idx)):
                        icon_data_inter[i_p] = (num2date(icon_data_all[idt[i_p]], self.icon_data_info['time', 'units'])
                                                - self.plane_data.base_date).total_seconds()
                else:
                    dim_var = len(icon_data_all.shape)
                    if dim_var == 2:
                        icon_data_inter = np.zeros(len(idx), dtype=np.float_)
                        for i_p in range(0, len(idx)):
                            icon_data_inter[i_p] = icon_data_all[idt[i_p], idx[i_p]]
                    elif dim_var == 3:
                        icon_data_inter = np.zeros((icon_data_all.shape[1], len(idx)), dtype=np.float_)
                        for i_p in range(0, len(idx)):
                            icon_data_inter[:, i_p] = icon_data_all[idt[i_p], :, idx[i_p]]

                icon_data_flight[var] = icon_data_inter
                del icon_data_inter, icon_data_all
            self.icon_data.append(icon_data_flight)
