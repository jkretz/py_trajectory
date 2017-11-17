from scipy import spatial
import numpy as np


class ProData:

    def __init__(self, data, var_icon, dim_vert):

        self.data = data
        len_track = len(self.data.flight_data['track'])

        self.idx, self.idt = self.kd_tree()
        self.var_out, self.p_level = self.icon_select(var_icon, len_track, dim_vert)

        del self.data

    # apply kd-tree decomposition and find gridpoints and timesteps closest to flight track
    def kd_tree(self):

        # apply kd-tree decomposition
        tree = spatial.cKDTree(list(zip(self.data.icon_data['lat_grid'], self.data.icon_data['lon_grid'])))

        # some empty arrays
        track = self.data.flight_data['track']
        idx = np.zeros(len(track), dtype=np.int_)
        idt = np.zeros(len(track), dtype=np.int_)

        # find gridpoints and timesteps closest to flight track
        for i_p, pts in enumerate(track):
            idx[i_p] = tree.query(pts)[1]
            idt[i_p] = np.int(np.argmin(np.abs(self.data.icon_data['time_ts'] -
                                               self.data.flight_data['time_new_ts'][i_p])))

        return idx, idt

    def icon_select(self, var_icon, len_track, dim_vert):

        var_out = {}

        # create new vertical grid and select desired pressure data for interpolation
        num_lev = dim_vert
        p_level_inter = np.linspace(50000., 102000., num=num_lev, dtype=float)
        pres_tmp = self.data.icon_data['pres'][self.idt, :, self.idx]

        for var in var_icon:

            # 2D-variable
            if len(self.data.icon_data[var].shape) == 2:

                # select variable on flight track
                var_select = self.data.icon_data[var][self.idt, self.idx]

            # 3D-variable
            elif len(self.data.icon_data[var].shape) == 3:

                # select variable on flight track
                var_pre_inter = self.data.icon_data[var][self.idt, :, self.idx]

                # interpolate to new gird
                var_select = np.zeros((num_lev, len_track))
                for i_p in range(0, len_track):
                    var_select[:, i_p] = np.interp(p_level_inter, pres_tmp[i_p, :], var_pre_inter[i_p, :])

            else:
                exit('strange variable dimension; exit')

            var_out[var] = var_select
            del var_select

        # select the used ICON timestep
        var_out['model_time'] = self.data.icon_data['time_ts'][self.idt]

        return var_out, p_level_inter
