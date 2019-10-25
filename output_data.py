from netCDF4 import Dataset
import numpy as np
from setting_file import settings_in


class DataOutNetcdf:

    def __init__(self, date_flight, base_date, plane_data, icon_data):

        dim_vert = settings_in['dim_vert']
        opath = settings_in['opath']

        # vertical grid for interpolation
        p_level_inter = np.linspace(50000., 103500., num=dim_vert, dtype=float)

        def create_dimension_entry(file, name, dimsize):
            file.createDimension(name, dimsize)

        def create_variable_entry(file, name, dimension, values, **kwargs):
            var_write = file.createVariable(name, 'd', dimension)
            var_write[:] = values

            for key, key_value in kwargs.items():
                if key == 'units':
                    var_write.units = key_value
                if key == 'standard_name':
                    var_write.standard_name = key_value
                if key == 'long_name':
                    var_write.long_name = key_value
                if key == 'calendar':
                    var_write.calendar = key_value

        ofile = 'ICON_'+date_flight+'.nc'
        f_out = Dataset(opath+ofile, 'w', format='NETCDF4')

        # write needed dimension
        create_dimension_entry(f_out, 'time', len(icon_data.var_icon['time']))
        create_dimension_entry(f_out, 'p_level', dim_vert)
        create_dimension_entry(f_out, 'num_sample', icon_data.num_sample)

        # get seconds of day
        seconds_day = []
        for ts in plane_data.var_plane['time']:
            seconds_day.append((ts - base_date).total_seconds())

        # write basic variables
        create_variable_entry(f_out, 'time', 'time', seconds_day,
                              units='seconds since '+date_flight+' 00:00:00 UTC', long_name='Time',
                              calendar='proleptic_gregorian')
        create_variable_entry(f_out, 'p_level', 'p_level', p_level_inter, units='Pa',
                              long_name='Vertical pressure levels')
        create_variable_entry(f_out, 'lat_track', 'time', plane_data.var_plane['lat'], units='degrees_north',
                              long_name='Latitude flight track')
        create_variable_entry(f_out, 'lon_track', 'time', plane_data.var_plane['lon'], units='degrees_east',
                              long_name='Longitude flight track')
        create_variable_entry(f_out, 'p_track', 'time', plane_data.var_plane['p']*100, units='Pa',
                              long_name='Pressure at flight altitude')
        create_variable_entry(f_out, 'time_ICON', 'time', icon_data.var_icon['time'],
                              units='seconds since '+date_flight+' 00:00:00 UTC', long_name='Time in ICON',
                              calendar='proleptic_gregorian')
        create_variable_entry(f_out, 'plane', 'time', plane_data.var_plane['plane'])

        # write all the other variables to file. For profiles, linearly interpolate on new grid
        pres_tmp = icon_data.var_icon['pres']
        var_rad_3d = ['swflx_up', 'swflx_dn', 'lwflx_up', 'lwflx_dn', 'swflx_up_clr', 'swflx_dn_clr',
                      'lwflx_up_clr', 'lwflx_dn_clr', 'trsolall']

        for var in icon_data.var_list:
            if var in ['time', 'pres']:
                continue
            else:
                dim_var = len(icon_data.var_icon[var].shape)
                if dim_var == 2:
                    create_variable_entry(f_out, var, ('time', 'num_sample'), icon_data.var_icon[var], units=icon_data.var_icon_info[var, 'units'], long_name=icon_data.var_icon_info[var, 'long_name'])
                elif dim_var == 3:
                    len_track = (icon_data.var_icon[var]).shape[1]
                    var_select = np.zeros((icon_data.num_sample, dim_vert, len_track))
                    var_select_p = np.zeros((icon_data.num_sample, len_track))
                    for ns in range(icon_data.num_sample):
                        for i_p in range(len_track):
                            if var in var_rad_3d:
                                var_select[ns, i_p, :] = np.interp(p_level_inter, pres_tmp[ns, :, i_p], (icon_data.var_icon[var])[ns, :-1, i_p])
                                var_select_p[ns, i_p] = np.interp((plane_data.var_plane['p'])[i_p]*100, pres_tmp[ns, :, i_p], (icon_data.var_icon[var])[ns, :-1, i_p])
                            else:
                                var_select[ns, :, i_p] = np.interp(p_level_inter, pres_tmp[:, i_p, ns], (icon_data.var_icon[var])[:, i_p, ns])
                                var_select_p[ns, i_p] = np.interp((plane_data.var_plane['p'])[i_p]*100, pres_tmp[:, i_p, ns], (icon_data.var_icon[var])[:, i_p, ns])

                            var_select[ns, :, i_p] = np.where(p_level_inter < icon_data.var_icon['pres_sfc'][i_p,ns], var_select[ns, :, i_p], np.nan)

                    # output of profile
                    #create_variable_entry(f_out, var, ('time', 'p_level', 'num_sample'), var_select, units=icon_data.var_icon_info[var, 'units'], long_name=icon_data.var_icon_info[var, 'long_name'])

                    # output of values at flight altitude
                    create_variable_entry(f_out, var+'_falt', ('time', 'num_sample'), var_select_p, units=icon_data.var_icon_info[var, 'units'], long_name=icon_data.var_icon_info[var, 'long_name'])

