from netCDF4 import Dataset
import numpy as np
from setting_file import settings_in


class DataOutNetcdf:

    def __init__(self, plane_data, icon_data):

        dim_vert = settings_in['dim_vert']
        opath = settings_in['opath']

        # vertical grid for interpolation
        p_level_inter = np.linspace(50000., 103500., num=dim_vert, dtype=float)

        def create_dimension_entry(file, name, dimsize):
            file.createDimension(name, dimsize)

        def create_variable_entry(file, name, dimension, values, **kwargs):
            var_write = file.createVariable(name, 'f4', dimension)
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

        for f in range(len(plane_data.flight_data)):

            ifile_plane_split = plane_data.plane_file_list[f].split('/')[-1].split('_')
            ofile = 'ICON_'+ifile_plane_split[1]+'_'+ifile_plane_split[2]+'_'+ifile_plane_split[3]+'_DOM' + \
                    str(settings_in['domain'])+'.nc'

            pres_tmp = icon_data.icon_data[f]['pres']

            f_out = Dataset(opath+ofile, 'w', format='NETCDF4')
            dim_time = len(plane_data.flight_data[f]['time_new_ts'])

            # write needed dimension
            create_dimension_entry(f_out, 'time', dim_time)
            create_dimension_entry(f_out, 'p_level', dim_vert)

            # write basic variables
            create_variable_entry(f_out, 'time', 'time', plane_data.flight_data[f]['time_new_ts'],
                                  units='seconds since '+plane_data.base_date.strftime('%Y-%-m-%-d %H:%M:%S'),
                                  long_name='Time',
                                  calendar='proleptic_gregorian')

            create_variable_entry(f_out, 'p_level', 'p_level', p_level_inter,
                                  units='Pa',
                                  long_name='Vertical pressure levels')

            create_variable_entry(f_out, 'lat_track', 'time', plane_data.flight_data[f]['lat'],
                                  units='degrees_north',
                                  long_name='Latitude flight track')

            create_variable_entry(f_out, 'lon_track', 'time', plane_data.flight_data[f]['lon'],
                                  units='degrees_east',
                                  long_name='Longitude flight track')

            create_variable_entry(f_out, 'p_track', 'time', plane_data.flight_data[f]['p']*100,
                                  units='Pa',
                                  long_name='Pressure at flight altitude')

            create_variable_entry(f_out, 'time_ICON', 'time', icon_data.icon_data[f]['time'],
                                  units='seconds since '+plane_data.base_date.strftime('%Y-%-m-%-d %H:%M:%S'),
                                  long_name='Time in ICON',
                                  calendar='proleptic_gregorian')

            # write all the other variables to file. For profiles, linearly interpolate on new grid
            for var in icon_data.icon_vars:
                if var in ['time', 'pres']:
                    continue
                else:
                    dim_var = len(icon_data.icon_data[f][var].shape)
                    if dim_var == 1:
                        create_variable_entry(f_out, var, 'time', icon_data.icon_data[f][var],
                                              units=icon_data.icon_data_info[var, 'units'],
                                              long_name=icon_data.icon_data_info[var, 'long_name'])
                    if dim_var == 2:
                        len_track = (icon_data.icon_data[f][var]).shape[-1]
                        var_select = np.zeros((len_track, dim_vert))
                        var_select_p = np.zeros(len_track)
                        for i_p in range(0, dim_time):
                            if var in ['swflxclr', 'lwflxclr', 'swflxall', 'lwflxall']:
                                var_select[i_p, :] = np.interp(p_level_inter, pres_tmp[:, i_p],
                                                               (icon_data.icon_data[f][var])[:-1, i_p])
                                var_select_p[i_p] = np.interp((plane_data.flight_data[f]['p'])[i_p]*100, pres_tmp[:, i_p], (icon_data.icon_data[f][var])[:-1, i_p])
                            else:
                                var_select[i_p, :] = np.interp(p_level_inter, pres_tmp[:, i_p],
                                                               (icon_data.icon_data[f][var])[:, i_p])
                                var_select_p[i_p] = np.interp((plane_data.flight_data[f]['p'])[i_p]*100, pres_tmp[:, i_p], (icon_data.icon_data[f][var])[:, i_p])

                            var_select[i_p, :] = np.where(p_level_inter < icon_data.icon_data[f]['pres_sfc'][i_p],
                                                          var_select[i_p, :], np.nan)
                        # output of profile
                        create_variable_entry(f_out, var, ('time', 'p_level'), var_select,
                                              units=icon_data.icon_data_info[var, 'units'],
                                              long_name=icon_data.icon_data_info[var, 'long_name'])
                        # output of values at flight altitude
                        create_variable_entry(f_out, var+'_falt', 'time', var_select_p,
                                              units=icon_data.icon_data_info[var, 'units'],
                                              long_name=icon_data.icon_data_info[var, 'long_name'])
