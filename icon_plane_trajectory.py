from import_data import ImportData
from process_data import ProcessData

settings = {}

settings['plane_path'] = 'data/HALO_flight_15'
settings['plane_file'] = f'{settings["plane_path"]}/Bahamas_min.csv'

settings['icon_path'] = 'data/ICON_data'
settings['icon_grid_file'] = 'icon_grid_0015_R02B09_DOM01.nc'
settings['icon_file_base_string'] = 'lam_amaz_cafe_atm'

input_data = ImportData(settings['plane_file'], settings['icon_path'], settings['icon_file_base_string'],
                        settings['icon_grid_file'])
ProcessData(input_data)
