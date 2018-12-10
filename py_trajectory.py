from netCDF4 import Dataset, num2date
import matplotlib.dates as date
import datetime
import numpy.ma as ma
import os
import pytz
from scipy import spatial
import pickle
import numpy as np


ifile_plane = '/media/jkretzs/intenso8tb/jkretzs/data/icon_acloud/acloud/ACLOUD_Measurements.nc'
ipath_icon = '/media/jkretzs/intenso8tb/jkretzs/data/icon_acloud/tmp/'
day = '20170602'

# import plane data
var_plane = {}
f_plane = Dataset(ifile_plane)
var_plane['lat'] = f_plane.variables['Lat'][:]
var_plane['lon'] = f_plane.variables['Lon'][:]
var_plane['time'] = date.num2date(f_plane.variables['time'][:])
var_plane['p'] = f_plane.variables['Pres'][:]
var_plane['plane'] = f_plane.variables['Airc'][:]

# mask not needed timesteps
day_datetime = datetime.datetime.strptime(day, '%Y%m%d').replace(tzinfo=pytz.UTC)
day_acloud = []
for ts in var_plane['time'][:]:
    day_acloud.append(ts.date() != day_datetime.date())

for keys_plane in var_plane.keys():
    var_plane[keys_plane] = ma.array(var_plane[keys_plane], mask=day_acloud).compressed()

# find needed ICON files
time_max = max(var_plane['time']).replace(microsecond=0, second=0, minute=0)+datetime.timedelta(hours=1)
time_min = min(var_plane['time']).replace(microsecond=0, second=0, minute=0)
icon_filelist = []
for ifile_icon in sorted(os.listdir(ipath_icon+day)):
    ifile_split = ifile_icon.split('_')[3].split('T')
    ifile_datetime = datetime.datetime.strptime(ifile_split[0]+ifile_split[1][:-1], '%Y%m%d%H%M%S').\
        replace(tzinfo=pytz.UTC)
    if time_min <= ifile_datetime <= time_max:
        icon_filelist.append(ipath_icon+day+'/'+ifile_icon)


# Find point and time in ICON files
kdtree_save_file = '.kdtree_save.p'
rad2deg = 180./np.pi
icon_inifile = Dataset(icon_filelist[0])
icon_lat, icon_lon = icon_inifile.variables['clat'][:]*rad2deg, icon_inifile.variables['clon'][:]*rad2deg

opath = ''
# apply kd-tree decomposition and save it to a file to speed things up when doing it the next time
if os.path.isfile(opath+kdtree_save_file):
    tree = pickle.load(open(opath+kdtree_save_file, "rb"))
else:
    tree = spatial.cKDTree(list(zip(icon_lat, icon_lon)))
    pickle.dump(tree, open(opath+kdtree_save_file, "wb"))

time_icon = []
data_icon = []
for ifile_icon in icon_filelist:
    data_icon.append(Dataset(ifile_icon))
    icon_timestamp = Dataset(ifile_icon).variables["time"].getncattr("units")
    time_file = num2date(Dataset(ifile_icon).variables['time'][:], icon_timestamp)
    num_timestep = len(time_file)
    for time in time_file:
        time_icon.append(time.replace(tzinfo=pytz.UTC))

track = list(zip(var_plane['lat'], var_plane['lon']))
idx = np.zeros(len(track), dtype=np.int_)
idt = np.zeros(len(track), dtype=np.int_)

for i_p, pts in enumerate(zip(var_plane['time'], track)):
    time_day = (pts[0]-day_datetime).total_seconds()
    timedif = []
    for date in time_icon:
        timedif.append(np.abs((date-day_datetime).total_seconds() - time_day))
    idt[i_p] = np.argmin(timedif)
    idx[i_p] = tree.query(pts[1])[1]

var_icon = {}
var_list = ['clat', 'clon']
for var in var_list:
    var_icon[var] = []

for loctime in zip(idx, idt):
    num_file = int(np.floor(loctime[1]/num_timestep))
    ts = int((loctime[1]/num_timestep-num_file)*num_timestep)
    ifile = data_icon[num_file]
    for var in var_list:
        if ts == 0:
            var_icon[var].append(ifile.variables[var][loctime[0]])
        else:
            var_icon[var].append(ifile.variables[var][ts, loctime[0]])

exit()
