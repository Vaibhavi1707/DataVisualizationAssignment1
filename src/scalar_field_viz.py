import sys
import glob
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as manimation
from mpl_toolkits.basemap import Basemap
import matplotlib.cm as cm

# Run this command: python3 scalar_field_viz.py <data_dir>
# data_dir can take the values: sss, sst, ssha

TIME_LINE = 5
LON_LINE = 6
LAT_LINE = 7
DATA_LINE = 8

PARAMETERS = {
    'sss': {
        'fname': 'sea_surface_salinity',
        'timestep':10,
        'contour_vals': np.linspace(22.5, 42.5, 30),
        'cmap': cm.GnBu,
        'cbar_label': 'Sea Surface Salinity',
        'title': 'Indian Ocean Sea Surface Salinity'
    },
    'sst': {
        'fname': 'sea_surface_temperature',
        'timestep':10,
        'contour_vals': np.linspace(14, 37.5, 40),
        'cmap': cm.autumn_r,
        'cbar_label': 'Sea Surface Temperature',
        'title': 'Indian Ocean Sea Surface Temperature'
    },
    'ssha': {
        'fname': 'sea_surface_height_anomaly',
        'timestep':10,
        'contour_vals': np.linspace(-0.6, 0.6, 70),
        'cmap': cm.coolwarm_r,
        'cbar_label': 'Sea Surface Height Anomaly',
        'title': 'Indian Ocean Sea Surface Height Anomaly'
    }
}


def extract_csv_format(lines):
    time_bad_flag = lines[TIME_LINE].split(' ')[-1].strip('\t').strip(' ')
    lon_bad_flag = lines[LON_LINE].split(' ')[-1][:-1].strip('\t').strip(' ')
    lat_bad_flag = lines[LAT_LINE].split(' ')[-1][:-1].strip('\t').strip(' ')
    data_bad_flag = lines[DATA_LINE].split(' ')[-1][:-1].strip('\t').strip(' ')

    return [time_bad_flag, lon_bad_flag, lat_bad_flag, data_bad_flag], lines[10:]


def extract_data(data_bad_flag, lines):
    date_time = lines[0].split(',')[:2]
    data = dict()
    all_lat, all_lon = [], []

    for line in lines:
        lon, lat, value = line.split(',')[2:]
        value = value[:-1].strip('\t').strip(' ')

        if value == data_bad_flag:
            continue

        all_lat.append(float(lat))
        all_lon.append(float(lon))

        if float(lon) not in data:
            data[float(lon)] = dict()
        data[float(lon)][float(lat)] = float(value)
        
    all_lat = sorted(list(set(all_lat)))
    all_lon = sorted(list(set(all_lon)))
    
    value_grid = np.zeros((len(all_lon), len(all_lat)), np.float32)

    
    for i, lon in enumerate(all_lon):
        for j, lat in enumerate(all_lat):
            if lon in data and lat in data[lon]:
                value_grid[i, j] = data[lon][lat]
            else:
                value_grid[i, j] = np.nan


    return date_time, all_lon, all_lat, value_grid

def plot_data(filename, ocean_var, save_cal = False):
    CONTOUR_VALS = PARAMETERS[ocean_var]['contour_vals']
    CMAP = PARAMETERS[ocean_var]['cmap']
    CBAR_LABEL = PARAMETERS[ocean_var]['cbar_label']
    TITLE = PARAMETERS[ocean_var]['title']
    
    lines = open(filename).readlines()
    bad_flags, lines = extract_csv_format(lines)
    date_time, all_lon, all_lat, data = extract_data(bad_flags[3], lines)

    plt.clf()
    map = Basemap(projection = 'cyl', 
        llcrnrlon=min(all_lon),
        llcrnrlat=min(all_lat),
        urcrnrlon=max(all_lon),
        urcrnrlat=max(all_lat),
        lat_0=0,
        lon_0=min(all_lon))

    lon, lat = np.meshgrid(all_lon, all_lat)

    map.drawcoastlines()
    map.drawparallels(np.arange(-90., 90., 10.), 
                    linewidth=2, 
                    labels=[1,0,0,0])
    map.drawmeridians(np.arange(-180., 180., 10.), 
                    linewidth=2, 
                    labels=[0,0,0,1])

    h = map.contourf(lon, 
                    lat, 
                    data.T,
                    levels = CONTOUR_VALS,
                    cmap=CMAP)

    cbar = plt.colorbar()
    cbar.set_label(CBAR_LABEL)
    plt.title(TITLE + " on {}".format(date_time[0].strip("\"")))

    if save_cal and "NOV-2004" in date_time[0] or "DEC" in date_time[0] or "JAN-2005" in date_time[0]:
        plt.savefig("../Visualisations/scalar/" + date_time[0] + '_' + ocean_var + '.png', dpi=300)

    return h

def animate_data(data_dir, opt):
    fig = plt.figure(figsize = (20, 12))

    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title = data_dir, 
                artist='Vaibhavi',
                comment='')
    writer = FFMpegWriter(fps=5, metadata=metadata)

    file_list = sorted(glob.glob(data_dir + '/*.txt'))

    with writer.saving(fig, "../Visualisations/" + PARAMETERS[opt]['fname'] + ".mp4", dpi = 200):
        i = 0
        while i < len(file_list):
            filename = file_list[i]

            h = plot_data(filename, opt, save_cal=True)
            writer.grab_frame()

            if "Nov_2004" in filename or "Dec_2004" in filename or "Jan_2005" in filename:
                i += 1
            else:
                i += PARAMETERS[data_dir]['timestep']

if __name__ == '__main__':
    animate_data('../data/' + sys.argv[1], sys.argv[1])