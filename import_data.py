import pandas as pd
import xarray as xr
import os
import numpy as np
import glob


class ImportData:
    def __init__(self, plane_file, icon_path, icon_base_string, icon_grid_file):
        self.var_plane = {}
        self.var_icon, self.grid_icon = None, None
        self.plane_data_import(plane_file)
        self.icon_data_import(icon_path, icon_grid_file, icon_base_string)

    def icon_data_import(self, ipath_icon, icon_grid_file, icon_base_string):
        icon_filelist = [file for file in glob.glob(f'{ipath_icon}/{icon_base_string}*cld*')
                         if icon_grid_file not in file and '_pre_' not in file]

        icon_filelist_phalf = [file for file in glob.glob(f'{ipath_icon}/*') if '_pre_' in file]
        icon_grid = f'{ipath_icon}/{icon_grid_file}'

        time_min, time_max = ((min(self.var_plane['time'])-np.timedelta64(1, 'h')),
                              max(self.var_plane['time'])+np.timedelta64(1, 'h'))
        # Import ICON variables
        data_icon = xr.open_mfdataset(icon_filelist, combine='by_coords').sel(time=slice(time_min, time_max))

        # Import ICON grid information
        self.grid_icon = xr.open_dataset(icon_grid)[['clon', 'clat']]

        # Import ICON pfull
        pfull_icon = xr.open_mfdataset(icon_filelist_phalf, combine='by_coords').sel(time=slice(time_min, time_max)).isel(height_2=slice(38, 90))
        self.var_icon = xr.merge([data_icon, pfull_icon])

        if len(self.var_icon.time) == 0:
            raise ValueError('No ICON data during the flight. Check times in provided ICON files.')

    def plane_data_import(self, ifile_plane):
        df_plane = pd.read_csv(ifile_plane, sep='\t', engine='python')
        self.var_plane['lat'] = df_plane['IRS_LAT'].to_numpy()
        self.var_plane['lon'] = df_plane['IRS_LON'].to_numpy()
        self.var_plane['time'] = pd.to_datetime(df_plane['DateTime'], utc=False).to_numpy()
        self.var_plane['p'] = df_plane['PS'].to_numpy() * 100.
        print(123)
