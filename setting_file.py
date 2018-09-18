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
#settings_in['var_icon'] = ['thb_s', 'thu_s', 'sou_s', 'sou_t', 'sob_s', 'qv', 'qc', 'qi', 'qr', 'qs', 'temp', 'tqv',
#                           'tqc', 'tqi', 'tqr', 'tqs','swflxclr','lwflxclr','swflxall','lwflxall','albdif']
settings_in['var_icon'] = ['thb_s', 'thu_s', 'sou_s', 'sou_t', 'sob_s', 'albdif']

# number of output vertical levels
settings_in['dim_vert'] = 100

# path that contains airplane data
settings_in['ipath_plane'] = '/pf/b/b380425/icon/postpro/icon_acloud/flight_track/all/'

# path that contains ICON data
settings_in['ipath_icon_base'] = '/work/bb1037/b380425/ICON_AC3/output/test/'

# output path
settings_in['opath'] = '/work/bb1037/b380425/ICON_AC3/output/test/'

#######################################################################
# end settings_in
#######################################################################
