import numpy as np
from scipy import spatial
import pickle
import os
import xarray as xr


class ProcessData:

    def __init__(self, input_data):

        var_plane, var_icon, grid_icon = input_data.var_plane, input_data.var_icon, input_data.grid_icon

        # Load or create kd-tree decompositions
        kdtree_save_file = '.kdtree_save.p'
        if not os.path.exists(kdtree_save_file):
            tree = self.kd_tree_decomposition(grid_icon, kdtree_save_file)
        else:
            tree = pickle.load(open(kdtree_save_file, "rb"))

        # Find grid points on flight track
        idt, idx = self.find_flighttrack_gridpoints(tree, var_plane, var_icon['time'])
        self.icon_processed = var_icon.isel(time=idt, ncells=idx)

        # Find closest point in the vertical
        idp = self.find_level(var_plane['p'])
        self.icon_processed = self.icon_processed.isel(height=idp, height_2=idp)

        # Write to file
        self.icon_processed.to_netcdf('tmp.nc')

    def find_level(self, p_plane):
        p_icon = self.icon_processed['pfull'].values[:, 1::]
        p_plane = p_plane
        idp = np.zeros_like(p_plane, dtype=int)
        for nt, _ in enumerate(p_plane):
            idp[nt] = np.argmin(np.abs(p_icon[nt, :] - p_plane[nt]))
        return xr.DataArray(idp, dims='track')

    @ staticmethod
    def find_flighttrack_gridpoints(tree, var_plane, var_icon_time):

        # Create list of flight track lats/lons
        flight_track = list(zip(var_plane['lat'], var_plane['lon']))

        # Indices of cells along flight track
        idx = np.zeros((len(flight_track)), dtype=np.int_)
        idt = np.zeros((len(flight_track)), dtype=np.int_)

        icon_time = var_icon_time.to_numpy()

        # Loop over flight track
        for i_p, pts in enumerate(zip(var_plane['time'], flight_track)):
            idt[i_p] = np.argmin(np.abs((icon_time - pts[0])))
            idx[i_p] = tree.query(pts[1])[1]

        return xr.DataArray(idt, dims='track'), xr.DataArray(idx, dims='track')

    @staticmethod
    def kd_tree_decomposition(grid_icon, kdtree_save_file):

        # Load center lons/lats from icon
        clon, clat = np.rad2deg(grid_icon['clon'].to_numpy()), np.rad2deg(grid_icon['clat'].to_numpy())

        # apply kd-tree decomposition and save it to a file to speed things up when doing it the next time
        tree = spatial.cKDTree(list(zip(clat, clon)))
        pickle.dump(tree, open(kdtree_save_file, "wb"))

        return tree
