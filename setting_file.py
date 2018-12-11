#######################################################################
# settings
#######################################################################

# set date of flight and set common timestep
settings_in = {}

# set a single day
settings_in['date'] = '20170602'

# set True for multiple days and give range of days to analyse
settings_in['lmulday'] = False
settings_in['range_start'] = '20170531'
settings_in['range_stop'] = '20170630'

# set beginning of file
file_start_string = 'NWP_LAM_DOM0'

# select domain to process
settings_in['domain'] = 1

settings_in['icon_file_string'] = file_start_string+str(settings_in['domain'])

# list of variables to be used
settings_in['var_icon'] = ['thb_s', 'thu_s', 'sou_s', 'sou_t', 'sob_s', 'qv', 'qc', 'qi', 'temp', 'tqv',
                          'tqc', 'tqi', 'albdif', 'u',
                           'v', 'geopot', 'fr_seaice', 'fr_glac', 'rh_2m', 't_2m', 'u_10m', 'v_10m', 'swflx_up',
                           'swflx_dn', 'lwflx_up', 'lwflx_dn', 'swflx_up_clr', 'swflx_dn_clr',
                           'lwflx_up_clr', 'lwflx_dn_clr', 'swflx_up_sfc_clr', 'swflx_dn_sfc_clr', 'lwflx_up_sfc_clr',
                           'lwflx_dn_sfc_clr']


# number of output vertical levels
settings_in['dim_vert'] = 100

# path that contains airplane data
settings_in['plane_file'] = '/media/jkretzs/intenso8tb/jkretzs/data/icon_acloud/acloud/ACLOUD_Measurements.nc'

# path that contains ICON data
settings_in['ipath_icon_base'] = '/media/jkretzs/intenso8tb/jkretzs/data/icon_acloud/tmp/'

# output path
settings_in['opath'] = '/home_local/jkretzs/work/scripts/python/icon_acloud/'

#######################################################################
# end settings_in
#######################################################################
