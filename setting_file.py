#######################################################################
# settings
#######################################################################

# set date of flight and set common timestep
settings_in = {}

# set a single day
settings_in['date'] = '20170608'

# set True for multiple days and give range of days to analyse
settings_in['lmulday'] = False
settings_in['range_start'] = '20170531'
settings_in['range_stop'] = '20170630'

# set beginning of file
file_start_string = 'ICON_AC3_DOM0'

# select domain to process
settings_in['domain'] = 2

settings_in['icon_file_string'] = file_start_string+str(settings_in['domain'])

# list of variables to be used
# settings_in['var_icon'] = ['thb_s', 'thu_s', 'sou_s', 'sou_t', 'sob_s', 'qv', 'qc', 'qi', 'qr', 'qs', 'temp', 'tqv',
#                            'tqc', 'tqi', 'tqr', 'tqs']

settings_in['var_icon'] = ['temp', 'thb_s']


# number of output vertical levels
settings_in['dim_vert'] = 100

# path that contains airplane data
settings_in['ipath_plane'] = '/home_local/jkretzs/work_new/ac3/xcut/plane_model_trajectory/data/flight_track/all/'

# path that contains ICON data
settings_in['ipath_icon_base'] = '/media/jkretzs/intenso8tb/jkretzs/mistral/ICON/ac3_nest/'

# output path
settings_in['opath'] = '/home_local/jkretzs/work_new/ac3/xcut/plane_model_trajectory/py_traj/'

#######################################################################
# end settings_in
#######################################################################
