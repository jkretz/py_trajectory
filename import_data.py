from netCDF4 import Dataset, num2date
import matplotlib.dates as datempl
import numpy.ma as ma
import datetime
import os
import pytz
import numpy as np
import pickle
from scipy import spatial


# import class for aircraft data
class ImportPlane:

    def __init__(self, base_date, plane_file, ipath_icon, file_string):

        self.var_plane = {}
        self.plane_data_import(plane_file)
        self.plane_mask_day(base_date)
        print
        self.icon_files = self.find_icon_files(ipath_icon)

    def plane_data_import(self, ifile_plane):
        # Import plane data
        f_plane = Dataset(ifile_plane)
        self.var_plane['lat'] = f_plane.variables['Lat'][:]
        self.var_plane['lon'] = f_plane.variables['Lon'][:]
        self.var_plane['time'] = datempl.num2date(f_plane.variables['time'][:])
        self.var_plane['time_old'] = f_plane.variables['time'][:]
        self.var_plane['p'] = f_plane.variables['Pres'][:]
        self.var_plane['plane'] = f_plane.variables['Airc'][:]

    def plane_mask_day(self, base_date):
        day_acloud = []
        for ts in self.var_plane['time'][:]:
            day_acloud.append(ts.date() != base_date.date())
        for keys_plane in self.var_plane.keys():
            self.var_plane[keys_plane] = ma.array(self.var_plane[keys_plane], mask=day_acloud).compressed()

    def find_icon_files(self, ipath_icon):
        icon_filelist = []
        time_max = max(self.var_plane['time']).replace(microsecond=0, second=0, minute=0)+datetime.timedelta(hours=1)
        time_min = min(self.var_plane['time']).replace(microsecond=0, second=0, minute=0)
        for ifile_icon in sorted(os.listdir(ipath_icon)):
            ifile_split = ifile_icon.split('_')[3].split('T')
            ifile_datetime = datetime.datetime.strptime(ifile_split[0]+ifile_split[1][:-1], '%Y%m%d%H%M%S').replace(tzinfo=pytz.UTC)
            if time_min <= ifile_datetime <= time_max:
                icon_filelist.append(ipath_icon+'/'+ifile_icon)
        return icon_filelist


class ImportICON:

    def __init__(self, var_list, plane_data, base_date, opath, num_sample):

        base_date = base_date.replace(tzinfo=pytz.UTC)
        self.opath = opath
        self.var_list = ['time', 'pres', 'pres_sfc'] + var_list
        self.num_sample = num_sample

        idt, idx, num_timestep, num_file = self.icon_trajectory(plane_data.icon_files, plane_data.var_plane, base_date)
        self.var_icon, self.var_icon_info = self.query_var_icon(plane_data.icon_files, idt, idx, num_timestep, num_file)

    def icon_trajectory(self, icon_files, var_plane, base_date):

        # get ICON grid
        rad2deg = 180./np.pi
        icon_inifile = Dataset(icon_files[0])
        icon_lat, icon_lon = icon_inifile.variables['clat'][:]*rad2deg, icon_inifile.variables['clon'][:]*rad2deg

        # apply kd-tree decomposition and save it to a file to speed things up when doing it the next time
        kdtree_save_file = '.kdtree_save.p'
        if os.path.isfile(self.opath+kdtree_save_file):
            tree = pickle.load(open(self.opath+kdtree_save_file, "rb"))
        else:
            tree = spatial.cKDTree(list(zip(icon_lat, icon_lon)))
            pickle.dump(tree, open(self.opath+kdtree_save_file, "wb"))

        time_icon = []
        num_file = []
        num_timestep = []
        for nf, ifile_icon in enumerate(icon_files):
            icon_timestamp = Dataset(ifile_icon).variables["time"].getncattr("units")
            time_file = num2date(Dataset(ifile_icon).variables['time'][:], icon_timestamp)
#            num_timestep = len(time_file)
            for time in time_file:
                time_icon.append(time.replace(tzinfo=pytz.UTC))
                num_file.append(nf)
            num_timestep.append(len(time_file))

        # average grid size
        grid_size = 1.2
        # earth's radius
        re = 6371.0
        # sample radius
        rs = 20.

        track = list(zip(var_plane['lat'], var_plane['lon']))
        idx = np.squeeze(np.zeros((self.num_sample, len(track)), dtype=np.int_))
        idt = np.zeros(len(track), dtype=np.int_)

        for i_p, pts in enumerate(zip(var_plane['time'], track)):
            time_day = (pts[0]-base_date).total_seconds()
            timedif = []
            for date in time_icon:
                timedif.append(np.abs((date-base_date).total_seconds() - time_day))
            idt[i_p] = np.argmin(timedif)

            if self.num_sample <= 1:
                idx[i_p] = tree.query(pts[1])[1]
            else:
                idx[0, i_p] = tree.query(pts[1])[1]

                ns = 1
                infini_stop = 0
                while ns < self.num_sample:
                    lats = np.degrees(2*rs/re * np.linspace(-0.5, 0.5, int(rs/grid_size)+1))
                    pdf_y = np.cos((np.pi/2.) * np.linspace(-1., 1., int(rs/grid_size)+1))**2
                    lat_sample = np.random.choice(pts[1][0] + lats, p=pdf_y/sum(pdf_y))

                    lons = np.degrees(2*rs/(re*np.cos(np.radians(lat_sample))) * np.linspace(-0.5, 0.5, int(rs/grid_size)+1))
                    pdf_x = np.cos((np.pi/2.) * np.linspace(-1., 1., int(rs/grid_size)+1))**2
                    lon_sample = np.random.choice(pts[1][1] + lons, p=pdf_x/sum(pdf_x))

                    idx_sample = tree.query((lat_sample, lon_sample))[1]
                    if idx_sample not in idx[:, i_p]:
                        idx[ns, i_p] = idx_sample
                        ns += 1
                        infini_stop = 0
                    else:
                        infini_stop += 1
                        if infini_stop >= self.num_sample*100:
                            exit('Infinity loop detected. Increase sample radius')

        return idt, idx, num_timestep, num_file

    def query_var_icon(self, icon_files, idt, idx, num_timestep, num_file):
        var_icon = {}
        icon_data_info = {}
        
        for var in self.var_list:
            print(var)
            var_icon_in = {}
            for nf, file in enumerate(icon_files):
                var_icon_in[nf] = Dataset(file).variables[var]

                # get varibale metadata
                if nf == 0:
                    for meta in 'units', 'long_name':
                        if var == 'time' and meta == 'long_name':
                            continue
                        icon_data_info[var, meta] = Dataset(file).variables[var].getncattr(meta)

            if var == 'time':
                var_in = np.zeros(len(idt))
                for p, time in enumerate(idt):
                    nf = num_file[time]
                    ts = time-sum(num_timestep[:nf])
                    var_in[p] = var_icon_in[nf][ts]

            if len(var_icon_in[0].shape) == 2:
                var_in = np.zeros((self.num_sample, max(idx.shape)))
            elif len(var_icon_in[0].shape) == 3:
                var_in = np.zeros((self.num_sample, var_icon_in[0].shape[-2], max(idx.shape)))


            for ns in np.arange(self.num_sample):
                if self.num_sample == 1:
                    idx_sample = idx
                else:
                    idx_sample = idx[ns]

                for p, loctime in enumerate(zip(idx_sample, idt)):
                    nf = num_file[loctime[1]]
                    ts = loctime[1]-sum(num_timestep[:nf])
                    if len(var_icon_in[0].shape) == 2:
                        var_in[ns, p] = var_icon_in[nf][ts, loctime[0]]
                    elif len(var_icon_in[0].shape) == 3:
                        var_in[ns, :, p] = var_icon_in[nf][ts, :, loctime[0]]

            var_icon[var] = var_in

        return var_icon, icon_data_info
