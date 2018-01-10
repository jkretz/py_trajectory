#######################################################################
# settings
#######################################################################

# set date of flight and set common timestep
settings_in = {}

settings_in['date'] = '20170531'

settings_in['lmulday'] = False
settings_in['range_start'] = '20170531'
settings_in['range_stop'] = '20170630'

# list of variables to be used
settings_in['var_icon'] = ['thb_s', 'thu_s', 'sou_s', 'sou_t', 'sob_s', 'qv', 'qc', 'qi', 'qr', 'qs', 'temp', 'tqv',
                           'tqc', 'tqi', 'tqr', 'tqs']

# number of output vertical levels
settings_in['dim_vert'] = 100

# path that contains airplane data
settings_in['ipath_plane'] = '/home_local/jkretzs/work_new/ac3/xcut/plane_model_trajectory/data/flight_track'

# path that contains ICON data
settings_in['ipath_icon_base'] = '/work/bb1037/b380425/ICON_AC3/output/'

# output path
settings_in['opath'] = '/work/bb1037/b380425/ICON_AC3/output/ICON_acloud/'

#######################################################################
# end settings_in
#######################################################################