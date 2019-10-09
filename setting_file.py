#######################################################################
# settings
#######################################################################

# set date of flight and set common timestep
settings_in = {}

# set a single day
settings_in['date'] = '20170604'

# set True for multiple days and give range of days to analyse
settings_in['lmulday'] = False
settings_in['range_start'] = '20170528'
settings_in['range_stop'] = '20170531'

# set beginning of file
file_start_string = 'ICON_ACLOUD_DOM0'

# select domain to process
settings_in['domain'] = 2

# number of samples to be draw
settings_in['num_sample'] = 1

settings_in['icon_file_string'] = file_start_string+str(settings_in['domain'])

# list of variables to be used
settings_in['var_icon'] = ['temp']


# number of output vertical levels
settings_in['dim_vert'] = 100

# path that contains airplane data
settings_in['plane_file'] = '/media/jkretzs/intenso8tb/jkretzs/data/icon_acloud/acloud/ACLOUD_Measurements_01s.nc'

# path that contains ICON data
settings_in['ipath_icon_base'] = '/media/jkretzs/intenso8tb/jkretzs/data/icon_acloud/tmp/'

# output path
settings_in['opath'] = '/home_local/jkretzs/work/scripts/python/icon_acloud/py_trajectory/'

#######################################################################
# end settings_in
#######################################################################
