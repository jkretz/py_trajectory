from netCDF4 import Dataset


class DataOutNetcdf:

    def __init__(self, data, pro_data, dim_vert, var_icon, ofile, opath):

        self.write_nc(dim_vert, data, pro_data, var_icon, ofile, opath)

    def write_nc(self, dim_vert, data, pro_data, var_icon, ofile, opath):

        f_out = Dataset(opath+ofile, 'w', format='NETCDF4')
        flight_data = data.flight_data
        dim_time = len(flight_data['time_new_ts'])

        # write needed dimension
        self.create_dimension_entry(f_out, 'time', dim_time)
        self.create_dimension_entry(f_out, 'p_level', dim_vert)

        # write basic variables
        self.create_variable_entry(f_out, 'time', 'time', flight_data["time_new_ts"],
                                   units='seconds since '+data.base_date.strftime('%Y-%-m-%-d %H:%M:%S'),
                                   long_name='Time',
                                   calendar='proleptic_gregorian')
        self.create_variable_entry(f_out, 'p_level', 'p_level', pro_data.p_level,
                                   units='Pa',
                                   long_name='Vertical pressure levels')

        self.create_variable_entry(f_out, 'lat_track', 'time', (flight_data['lat']),
                                   units='degrees_north',
                                   long_name='Latitude flight track')

        self.create_variable_entry(f_out, 'lon_track', 'time', (flight_data['lon']),
                                   units='degrees_east',
                                   long_name='Longitude flight track')

        self.create_variable_entry(f_out, 'p_track', 'time', flight_data['p']*100,
                                   units='Pa',
                                   long_name='Pressure at flight altitude')

        self.create_variable_entry(f_out, 'time_ICON', 'time', pro_data.var_out['model_time'],
                                   units='seconds since '+data.base_date.strftime('%Y-%-m-%-d %H:%M:%S'),
                                   long_name='Time in ICON',
                                   calendar='proleptic_gregorian')

        for var in var_icon:

            if len(pro_data.var_out[var].shape) == 1:
                self.create_variable_entry(f_out, var, 'time', pro_data.var_out[var],
                                           units=data.icon_data_info[var, 'units'],
                                           long_name=data.icon_data_info[var, 'long_name'])

            if len(pro_data.var_out[var].shape) == 2:
                self.create_variable_entry(f_out, var, ('time', 'p_level'), pro_data.var_out[var],
                                           units=data.icon_data_info[var, 'units'],
                                           long_name=data.icon_data_info[var, 'long_name'])

    # maybe this is a little too much
    @staticmethod
    def create_dimension_entry(file, name, dimsize):
        file.createDimension(name, dimsize)

    @staticmethod
    def create_variable_entry(file, name, dimension, values, **kwargs):
        var = file.createVariable(name, 'f4', dimension)
        var[:] = values

        for key, key_value in kwargs.items():
            if key == 'units':
                var.units = key_value
            if key == 'standard_name':
                var.standard_name = key_value
            if key == 'long_name':
                var.long_name = key_value
            if key == 'calendar':
                var.calendar = key_value
