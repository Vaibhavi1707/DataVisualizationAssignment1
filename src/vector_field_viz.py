import os
import sys
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as manimation
from mpl_toolkits.basemap import Basemap
import matplotlib.cm as cm

# Run this command: python3 vector_field_viz.py <quiver>
# quiver can take the values: quiver, magnitude or both

TIME_LINE = 5
LON_LINE = 6
LAT_LINE = 7
DEP_LINE = 8
DATA_LINE = 9

CONTOUR_VALS = np.linspace(0, 2.8, 30)
CMAP = cm.magma
CBAR_LABEL = "Zonal and Meridional Currents magnitude"
VIZ_TYPE = {
    'quiver': 'q',
    'magnitude': 'm',
    'both': 'both'
}


def extract_csv_format(lines):
    time_bad_flag = lines[TIME_LINE].split(' ')[-1].strip('\t').strip(' ')
    lon_bad_flag = lines[LON_LINE].split(' ')[-1][:-1].strip('\t').strip(' ')
    lat_bad_flag = lines[LAT_LINE].split(' ')[-1][:-1].strip('\t').strip(' ')
    dep_bad_flag = lines[DEP_LINE].split(' ')[-1][:-1].strip('\t').strip(' ')
    data_bad_flag = lines[DATA_LINE].split(' ')[-1][:-1].strip('\t').strip(' ')

    return [time_bad_flag, lon_bad_flag, lat_bad_flag, dep_bad_flag, data_bad_flag], lines[11:]

def extract_data(data_bad_flag, lines):
    date_time = lines[0].split(',')[:2]
    data = dict()
    all_lat, all_lon = [], []

    for line in lines:
        lon, lat, dep, value = line.split(',')[2:]
        value = value[:-1].strip('\t').strip(' ')

        if value == data_bad_flag:
            continue

        all_lat.append(float(lat))
        all_lon.append(float(lon))

        if float(lon) not in data:
            data[float(lon)] = dict()    
        data[float(lon)][float(lat)] = float(value) * -1
        
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

def retrieve_current_data(filename):
    lines = open(filename).readlines()
    bad_flags, lines = extract_csv_format(lines)
    date_time, all_lon, all_lat, data = extract_data(bad_flags[3], lines)

    return date_time, all_lon, all_lat, data

def plot_data(zonal_file, meridional_file, quiver, save_cal = False):
    date_time, all_lon, all_lat, zonal_data = retrieve_current_data(zonal_file)
    date_time, all_lon, all_lat, meridional_data = retrieve_current_data(meridional_file)

    magnitude_mat = np.sqrt((zonal_data ** 2) + (meridional_data ** 2))

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
    
    if VIZ_TYPE[quiver] == 'm' or VIZ_TYPE[quiver] == 'both':
        map.contourf(lon, 
                        lat, 
                        magnitude_mat.T,
                        levels = CONTOUR_VALS,
                        cmap=CMAP)

        cbar = plt.colorbar()
        cbar.set_label(CBAR_LABEL)

    if VIZ_TYPE[quiver] == 'q' or VIZ_TYPE[quiver] == 'both':
        
        map.quiver(lon, 
                    lat, 
                    zonal_data.T,
                    meridional_data.T,
                    width = 0.001,
                    color = 'black',
                    scale = 150)
    
    plt.title("Currents (zonal and meridional) at depth = 5 in Indian Ocean on {}".format(date_time[0].strip("\"")))

    if save_cal and ("NOV-2004" in date_time[0] or "DEC" in date_time[0] or "JAN-2005" in date_time[0]):
        plt.savefig("../Visualisations/vector/" + date_time[0] + '_' + VIZ_TYPE[quiver] + '.png', dpi=300)

def animate_data(data_dir, quiver):
    fig = plt.figure(figsize = (16, 8))

    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title = data_dir, 
                artist='Vaibhavi',
                comment='Movie support!')
    writer = FFMpegWriter(fps=12, metadata=metadata)

    file_list = sorted(os.listdir(data_dir))

    with writer.saving(fig, "../Visualisations/vector/zonal_meridian_" + VIZ_TYPE[quiver] + "_currents.mp4", dpi = 250):
        i = 0
        while i < len(file_list):
            filename = file_list[i]
            
            plot_data(data_dir + filename, data_dir[:8] + 'meridional-current/' + filename, quiver)
            writer.grab_frame()

            if "Nov_2004" in filename or "Dec_2004" in filename or "Jan_2005" in filename:
                i += 1
            else:
                i += 4

if __name__ == '__main__':
    animate_data('../data/zonal-current/', quiver = sys.argv[1]) 