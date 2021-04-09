#######################################################################
# settings
#######################################################################

# set date of flight and set common timestep
settings_in = {}

# set a single day
settings_in['date'] = '20170604'

# set True for multiple days and give range of days to analyse
settings_in['lmulday'] = True
settings_in['range_start'] = '20170602'
settings_in['range_stop'] = '20170605'

# set beginning of file
file_start_string = 'ICON_ACLOUD_DOM0'

# select domain to process
settings_in['domain'] = 2

# number of samples to be draw
settings_in['num_sample'] = 1

settings_in['icon_file_string'] = file_start_string+str(settings_in['domain'])

# # list of variables to be used
settings_in['var_icon'] = ['qv', 'qc', 'qi', 'temp', 'tqv',
                          'tqc', 'tqi', 'albdif', 'u','rho', 'qnc', 'qni',
                           'v', 'geopot', 'fr_seaice', 'swflx_up',
                           'swflx_dn', 'lwflx_up', 'lwflx_dn', 'swflx_up_clr', 'swflx_dn_clr',
                           'lwflx_up_clr', 'lwflx_dn_clr', 'swflx_up_sfc_clr', 'swflx_dn_sfc_clr', 'lwflx_up_sfc_clr',
                           'lwflx_dn_sfc_clr']


# number of output vertical levels
settings_in['dim_vert'] = 100

# path that contains airplane data
settings_in['plane_file'] = '/pf/b/b380425/icon/postpro/icon_acloud/flight_track/data_all/ACLOUD_Measurements_01s.nc'

# path that contains ICON data
settings_in['ipath_icon_base'] = '/work/bb1036/b380425/bb1037/ICON_AC3/output_noicerad/dates/'

# output path
settings_in['opath'] = settings_in['ipath_icon_base'] + 'flighttrack/'

#######################################################################
# end settings_in
#######################################################################
