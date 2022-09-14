import os
import glob
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.animation as manimation
import streamlit as st

import scalar_field_viz as sfv
import vector_field_viz as vfv

def init_writer(data_dir):
    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title = data_dir, 
                artist='Vaibhavi',
                comment='')
    return FFMpegWriter(fps=12, metadata=metadata)

def init_fig():
    fig = plt.figure(figsize = (16, 8))
    plot = st.pyplot(fig)

    return plot, fig

def animate(file_list, data_dir, fname, quiver = None, ocean_var = None):
    writer = init_writer(data_dir)
    plot, fig = init_fig()

    with writer.saving(fig, fname, dpi = 250):
        i = 0
        while i < len(file_list):
            filename = file_list[i]
            
            if quiver:
                vfv.plot_data(data_dir + filename, data_dir[:8] + 'meridional-current/' + filename, quiver)
            
            if ocean_var:
                sfv.plot_data(filename, ocean_var)
            
            plot.pyplot(plt, clear_fig = True)

            writer.grab_frame()

            if "Nov_2004" in filename or "Dec_2004" in filename: #or "Jan_2005" in filename:
                i += 1
            else:
                i += 11

def make_scalar_animation(data_dir):
    file_list = sorted(glob.glob('../data/' + data_dir + '/*.txt'))
    video_fname = "../Visualisations/scalar/" + sfv.PARAMETERS[data_dir]['fname'] + ".mp4"
    animate(file_list, data_dir, video_fname, ocean_var = data_dir)    

def make_vector_animation(data_dir, quiver):
    file_list = sorted(os.listdir(data_dir))
    video_fname = "../Visualisations/vector/zonal_meridian_" + quiver + "_currents.mp4"
    animate(file_list, data_dir, video_fname, quiver = quiver)