import pandas as pd
import numpy as np
from statsmodels.stats.anova import AnovaRM
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.collections import PatchCollection
import argparse
from data_analysis import read_from_numpy
import scienceplots

mpl.rcParams['hatch.linewidth'] = 0.2 
bar_colors_group1 = ['#FED976', '#FEB24C', '#9EC9E2', '#5F97D2']
bar_colors_group2 = ['#5F97D2', '#FFBE7A', '#2A65A1']
hatch_patterns = ['xxx', 'ooo', '...', '\oo', '+++', '+o', 'o', 'O', '.', '*']

def draw_bar_plot_selectiontime_radius(tech_type1, tech_type2, tech_type3, tech_type4):
    data1 = read_from_numpy('./output_numpy/' + tech_type1 + '_radius_007_data.npy')
    data2 = read_from_numpy('./output_numpy/' + tech_type2 + '_radius_007_data.npy')
    data3 = read_from_numpy('./output_numpy/' + tech_type3 + '_radius_007_data.npy')
    data4 = read_from_numpy('./output_numpy/' + tech_type4 + '_radius_007_data.npy')

    data5 = read_from_numpy('./output_numpy/' + tech_type1 + '_radius_014_data.npy')
    data6 = read_from_numpy('./output_numpy/' + tech_type2 + '_radius_014_data.npy')
    data7 = read_from_numpy('./output_numpy/' + tech_type3 + '_radius_014_data.npy')
    data8 = read_from_numpy('./output_numpy/' + tech_type4 + '_radius_014_data.npy')

    data9 = read_from_numpy('./output_numpy/' + tech_type1 + '_radius_021_data.npy')
    data10 = read_from_numpy('./output_numpy/' + tech_type2 + '_radius_021_data.npy')
    data11 = read_from_numpy('./output_numpy/' + tech_type3 + '_radius_021_data.npy')
    data12 = read_from_numpy('./output_numpy/' + tech_type4 + '_radius_021_data.npy')

    title = 'Selection Time for ' + tech_type1 + ', ' + tech_type2 + ', ' + tech_type3 + ' and ' + tech_type4
    ylabel = 'Selection Time (s)'

    xaxis_labels = ['radius = 7', 'radius = 14', 'radius = 21']
    plt.style.use('ieee')
    plt.rcParams["font.family"] = "sans-serif"

    data_selection_time_type1 = [data1['global_avg_selection_time'], data5['global_avg_selection_time'], data9['global_avg_selection_time']]
    data_selection_sem_type1 = [data1['global_sem_selection_time'], data5['global_sem_selection_time'], data9['global_sem_selection_time']]

    data_selection_time_type2 = [data2['global_avg_selection_time'], data6['global_avg_selection_time'], data10['global_avg_selection_time']]
    data_selection_sem_type2 = [data2['global_sem_selection_time'], data6['global_sem_selection_time'], data10['global_sem_selection_time']]

    data_selection_time_type3 = [data3['global_avg_selection_time'], data7['global_avg_selection_time'], data11['global_avg_selection_time']]
    data_selection_sem_type3 = [data3['global_sem_selection_time'], data7['global_sem_selection_time'], data11['global_sem_selection_time']]

    data_selection_time_type4 = [data4['global_avg_selection_time'], data8['global_avg_selection_time'], data12['global_avg_selection_time']]
    data_selection_sem_type4 = [data4['global_sem_selection_time'], data8['global_sem_selection_time'], data12['global_sem_selection_time']]

    figure, axis = plt.subplots(1, 1, figsize=(5, 4))
    figure.set_dpi(800);
    figure.tight_layout(pad=4.0) 
    #figure.tight_layout(h_pad=4.0, w_pad=3.0)
    figure.suptitle('', x=0.5)
    axis.set_ylabel('Selection Time (Sec)', fontsize=8)
    axis.set_xlabel('Target Size (cm)', fontsize=8)
    x_axis = np.arange(len(xaxis_labels))

    # 'BareHandIntenSelect', 'ControllerIntenSelect', 'BareHandTracking','ControllerTracking'
    if tech_type1 == 'BareHandIntenSelect':
        tech_type1 = 'Score-based Hand Tracking'

    if tech_type2 == 'ControllerIntenSelect':
        tech_type2 = 'Score-based Controller Tracking'

    if tech_type3 == 'BareHandTracking':
        tech_type3 = 'Direct Hand Tracking'

    if tech_type4 == 'ControllerTracking':
        tech_type4 = 'Direct Controller Tracking'

    axis.bar(x_axis - 0.15, data_selection_time_type1, width=0.15, label = tech_type1, 
            color = bar_colors_group1[0], yerr = data_selection_sem_type1 , error_kw= {'elinewidth':1}, ecolor='black', capsize=3)
    axis.bar(x_axis, data_selection_time_type2, width=0.15, label = tech_type2, 
            color = bar_colors_group1[1],  yerr = data_selection_sem_type2, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[0])
    axis.bar(x_axis + 0.15, data_selection_time_type3, width=0.15, label = tech_type3, 
            color = bar_colors_group1[2],  yerr = data_selection_sem_type3, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[1])
    axis.bar(x_axis + 0.3, data_selection_time_type4, width=0.15, label = tech_type4, 
            color = bar_colors_group1[3],  yerr = data_selection_sem_type4, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[2])

    #axis.set_ylabel('Selection Time (Sec)', fontsize=8);
    axis.tick_params(bottom = False, left = False);
    axis.set_xticks(np.arange(len(xaxis_labels)))
    axis.set_xticklabels(xaxis_labels)
    axis.set_axisbelow(True)
    axis.yaxis.grid(visible=True, linestyle='--', linewidth=0.5);
    axis.spines['right'].set_visible(False);
    axis.spines['top'].set_visible(False);
    axis.legend(loc='upper right', bbox_to_anchor=(1.03, 1.02))

    return

def draw_bar_plot_accuracy_radius(tech_type1, tech_type2, tech_type3, tech_type4):
    
    data1 = read_from_numpy('./output_numpy/' + tech_type1 + '_radius_007_data.npy')
    data2 = read_from_numpy('./output_numpy/' + tech_type2 + '_radius_007_data.npy')
    data3 = read_from_numpy('./output_numpy/' + tech_type3 + '_radius_007_data.npy')
    data4 = read_from_numpy('./output_numpy/' + tech_type4 + '_radius_007_data.npy')

    data5 = read_from_numpy('./output_numpy/' + tech_type1 + '_radius_014_data.npy')
    data6 = read_from_numpy('./output_numpy/' + tech_type2 + '_radius_014_data.npy')
    data7 = read_from_numpy('./output_numpy/' + tech_type3 + '_radius_014_data.npy')
    data8 = read_from_numpy('./output_numpy/' + tech_type4 + '_radius_014_data.npy')

    data9 = read_from_numpy('./output_numpy/' + tech_type1 + '_radius_021_data.npy')
    data10 = read_from_numpy('./output_numpy/' + tech_type2 + '_radius_021_data.npy')
    data11 = read_from_numpy('./output_numpy/' + tech_type3 + '_radius_021_data.npy')
    data12 = read_from_numpy('./output_numpy/' + tech_type4 + '_radius_021_data.npy')

    title = 'Selection Time for ' + tech_type1 + ', ' + tech_type2 + ', ' + tech_type3 + ' and ' + tech_type4
    ylabel = 'Selection Time (s)'

    xaxis_labels = ['radius = 7', 'radius = 14', 'radius = 21']
    plt.style.use('ieee')
    plt.rcParams["font.family"] = "sans-serif"

    data_selection_time_type1 = [data1['global_error_rate']*100, data5['global_error_rate']*100, data9['global_error_rate']*100]
    data_selection_sem_type1 = [data1['global_error_rate_sem']*100, data5['global_error_rate_sem']*100, data9['global_error_rate_sem']*100]

    data_selection_time_type2 = [data2['global_error_rate']*100, data6['global_error_rate']*100, data10['global_error_rate']*100]
    data_selection_sem_type2 = [data2['global_error_rate_sem']*100, data6['global_error_rate_sem']*100, data10['global_error_rate_sem']*100]

    data_selection_time_type3 = [data3['global_error_rate']*100, data7['global_error_rate']*100, data11['global_error_rate']*100]
    data_selection_sem_type3 = [data3['global_error_rate_sem']*100, data7['global_error_rate_sem']*100, data11['global_error_rate_sem']*100]


    data_selection_time_type4 = [data4['global_error_rate']*100, data8['global_error_rate']*100, data12['global_error_rate']*100]
    data_selection_sem_type4 = [data4['global_error_rate_sem']*100, data8['global_error_rate_sem']*100, data12['global_error_rate_sem']*100]

    figure, axis = plt.subplots(1, 1, figsize=(5, 4))
    figure.set_dpi(800);
    figure.tight_layout(pad=4.0) 
    #figure.tight_layout(h_pad=4.0, w_pad=3.0)
    figure.suptitle('', x=0.5)
    axis.set_ylabel('Selection Accuracy (%)', fontsize=8)
    axis.set_xlabel('Target Size (cm)', fontsize=8)
    x_axis = np.arange(len(xaxis_labels))

    # 'BareHandIntenSelect', 'ControllerIntenSelect', 'BareHandTracking','ControllerTracking'
    if tech_type1 == 'BareHandIntenSelect':
        tech_type1 = 'Score-based Hand Tracking'

    if tech_type2 == 'ControllerIntenSelect':
        tech_type2 = 'Score-based Controller Tracking'

    if tech_type3 == 'BareHandTracking':
        tech_type3 = 'Direct Hand Tracking'

    if tech_type4 == 'ControllerTracking':
        tech_type4 = 'Direct Controller Tracking'

    axis.bar(x_axis - 0.15, data_selection_time_type1, width=0.15, label = tech_type1, 
            color = bar_colors_group1[0], yerr = data_selection_sem_type1 , error_kw= {'elinewidth':1}, ecolor='black', capsize=3)
    axis.bar(x_axis, data_selection_time_type2, width=0.15, label = tech_type2, 
            color = bar_colors_group1[1],  yerr = data_selection_sem_type2, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[0])
    axis.bar(x_axis + 0.15, data_selection_time_type3, width=0.15, label = tech_type3, 
            color = bar_colors_group1[2],  yerr = data_selection_sem_type3, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[1])
    axis.bar(x_axis + 0.3, data_selection_time_type4, width=0.15, label = tech_type4, 
            color = bar_colors_group1[3],  yerr = data_selection_sem_type4, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[2])

    #axis.set_ylabel('Selection Time (Sec)', fontsize=8);
    axis.tick_params(bottom = False, left = False);
    axis.set_xticks(np.arange(len(xaxis_labels)))
    axis.set_xticklabels(xaxis_labels)
    axis.set_axisbelow(True)
    axis.yaxis.grid(visible=True, linestyle='--', linewidth=0.5);
    axis.spines['right'].set_visible(False);
    axis.spines['top'].set_visible(False);
    # axis.legend(loc='upper right', bbox_to_anchor=(1.03, 1.02))

    return

def draw_bar_plot_Heisenberg_errorrate_radius(tech_type1, tech_type2, tech_type3, tech_type4):
    
    data1 = read_from_numpy('./output_numpy/' + tech_type1 + '_radius_007_data.npy')
    data2 = read_from_numpy('./output_numpy/' + tech_type2 + '_radius_007_data.npy')
    data3 = read_from_numpy('./output_numpy/' + tech_type3 + '_radius_007_data.npy')
    data4 = read_from_numpy('./output_numpy/' + tech_type4 + '_radius_007_data.npy')

    data5 = read_from_numpy('./output_numpy/' + tech_type1 + '_radius_014_data.npy')
    data6 = read_from_numpy('./output_numpy/' + tech_type2 + '_radius_014_data.npy')
    data7 = read_from_numpy('./output_numpy/' + tech_type3 + '_radius_014_data.npy')
    data8 = read_from_numpy('./output_numpy/' + tech_type4 + '_radius_014_data.npy')

    data9 = read_from_numpy('./output_numpy/' + tech_type1 + '_radius_021_data.npy')
    data10 = read_from_numpy('./output_numpy/' + tech_type2 + '_radius_021_data.npy')
    data11 = read_from_numpy('./output_numpy/' + tech_type3 + '_radius_021_data.npy')
    data12 = read_from_numpy('./output_numpy/' + tech_type4 + '_radius_021_data.npy')

    title = 'Selection Time for ' + tech_type1 + ', ' + tech_type2 + ', ' + tech_type3 + ' and ' + tech_type4
    ylabel = 'Selection Time (s)'

    xaxis_labels = ['radius = 7', 'radius = 14', 'radius = 21']
    plt.style.use('ieee')
    plt.rcParams["font.family"] = "sans-serif"

    data_selection_time_type1 = [data1['global_H_error_rate']*100, data5['global_H_error_rate']*100, data9['global_H_error_rate']*100]
    data_selection_sem_type1 = [data1['global_H_error_rate_sem']*100, data5['global_H_error_rate_sem']*100, data9['global_H_error_rate_sem']*100]

    data_selection_time_type2 = [data2['global_H_error_rate']*100, data6['global_H_error_rate']*100, data10['global_H_error_rate']*100]
    data_selection_sem_type2 = [data2['global_H_error_rate_sem']*100, data6['global_H_error_rate_sem']*100, data10['global_H_error_rate_sem']*100]

    data_selection_time_type3 = [data3['global_H_error_rate']*100, data7['global_H_error_rate']*100, data11['global_H_error_rate']*100]
    data_selection_sem_type3 = [data3['global_H_error_rate_sem']*100, data7['global_H_error_rate_sem']*100, data11['global_H_error_rate_sem']*100]


    data_selection_time_type4 = [data4['global_H_error_rate']*100, data8['global_H_error_rate']*100, data12['global_H_error_rate']*100]
    data_selection_sem_type4 = [data4['global_H_error_rate_sem']*100, data8['global_H_error_rate_sem']*100, data12['global_H_error_rate_sem']*100]

    figure, axis = plt.subplots(1, 1, figsize=(5, 4))
    figure.set_dpi(800);
    figure.tight_layout(pad=4.0) 
    #figure.tight_layout(h_pad=4.0, w_pad=3.0)
    figure.suptitle('', x=0.5)
    axis.set_ylabel('Heisenberg Error Rate (%)', fontsize=8)
    axis.set_xlabel('Target Size (cm)', fontsize=8)
    x_axis = np.arange(len(xaxis_labels))
    axis.set_ylim(0,50)

    # 'BareHandIntenSelect', 'ControllerIntenSelect', 'BareHandTracking','ControllerTracking'
    if tech_type1 == 'BareHandIntenSelect':
        tech_type1 = 'Score-based Hand Tracking'

    if tech_type2 == 'ControllerIntenSelect':
        tech_type2 = 'Score-based Controller Tracking'

    if tech_type3 == 'BareHandTracking':
        tech_type3 = 'Direct Hand Tracking'

    if tech_type4 == 'ControllerTracking':
        tech_type4 = 'Direct Controller Tracking'

    axis.bar(x_axis - 0.15, data_selection_time_type1, width=0.15, label = tech_type1, 
            color = bar_colors_group1[0], yerr = data_selection_sem_type1 , error_kw= {'elinewidth':1}, ecolor='black', capsize=3)
    axis.bar(x_axis, data_selection_time_type2, width=0.15, label = tech_type2, 
            color = bar_colors_group1[1],  yerr = data_selection_sem_type2, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[0])
    axis.bar(x_axis + 0.15, data_selection_time_type3, width=0.15, label = tech_type3, 
            color = bar_colors_group1[2],  yerr = data_selection_sem_type3, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[1])
    axis.bar(x_axis + 0.3, data_selection_time_type4, width=0.15, label = tech_type4, 
            color = bar_colors_group1[3],  yerr = data_selection_sem_type4, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[2])

    #axis.set_ylabel('Selection Time (Sec)', fontsize=8);
    axis.tick_params(bottom = False, left = False);
    axis.set_xticks(np.arange(len(xaxis_labels)))
    axis.set_xticklabels(xaxis_labels)
    axis.set_axisbelow(True)
    axis.yaxis.grid(visible=True, linestyle='--', linewidth=0.5);
    axis.spines['right'].set_visible(False);
    axis.spines['top'].set_visible(False);
    # axis.legend(loc='upper right', bbox_to_anchor=(1.03, 1.02))

    return

def draw_bar_plot_selectiontime_spacing(tech_type1, tech_type2, tech_type3, tech_type4):
    data1 = read_from_numpy('./output_numpy/' + tech_type1 + '_spacing_03_data.npy')
    data2 = read_from_numpy('./output_numpy/' + tech_type2 + '_spacing_03_data.npy')
    data3 = read_from_numpy('./output_numpy/' + tech_type3 + '_spacing_03_data.npy')
    data4 = read_from_numpy('./output_numpy/' + tech_type4 + '_spacing_03_data.npy')

    data5 = read_from_numpy('./output_numpy/' + tech_type1 + '_spacing_05_data.npy')
    data6 = read_from_numpy('./output_numpy/' + tech_type2 + '_spacing_05_data.npy')
    data7 = read_from_numpy('./output_numpy/' + tech_type3 + '_spacing_05_data.npy')
    data8 = read_from_numpy('./output_numpy/' + tech_type4 + '_spacing_05_data.npy')

    data9 = read_from_numpy('./output_numpy/' + tech_type1 + '_spacing_07_data.npy')
    data10 = read_from_numpy('./output_numpy/' + tech_type2 + '_spacing_07_data.npy')
    data11 = read_from_numpy('./output_numpy/' + tech_type3 + '_spacing_07_data.npy')
    data12 = read_from_numpy('./output_numpy/' + tech_type4 + '_spacing_07_data.npy')

    title = 'Selection Time for ' + tech_type1 + ', ' + tech_type2 + ', ' + tech_type3 + ' and ' + tech_type4
    ylabel = 'Selection Time (s)'

    xaxis_labels = ['spacing = 30', 'spacing = 50', 'spacing = 70']
    plt.style.use('ieee')
    plt.rcParams["font.family"] = "sans-serif"

    data_selection_time_type1 = [data1['global_avg_selection_time'], data5['global_avg_selection_time'], data9['global_avg_selection_time']]
    data_selection_sem_type1 = [data1['global_sem_selection_time'], data5['global_sem_selection_time'], data9['global_sem_selection_time']]

    data_selection_time_type2 = [data2['global_avg_selection_time'], data6['global_avg_selection_time'], data10['global_avg_selection_time']]
    data_selection_sem_type2 = [data2['global_sem_selection_time'], data6['global_sem_selection_time'], data10['global_sem_selection_time']]

    data_selection_time_type3 = [data3['global_avg_selection_time'], data7['global_avg_selection_time'], data11['global_avg_selection_time']]
    data_selection_sem_type3 = [data3['global_sem_selection_time'], data7['global_sem_selection_time'], data11['global_sem_selection_time']]

    data_selection_time_type4 = [data4['global_avg_selection_time'], data8['global_avg_selection_time'], data12['global_avg_selection_time']]
    data_selection_sem_type4 = [data4['global_sem_selection_time'], data8['global_sem_selection_time'], data12['global_sem_selection_time']]

    figure, axis = plt.subplots(1, 1, figsize=(5, 4))
    figure.set_dpi(800);
    figure.tight_layout(pad=4.0) 
    #figure.tight_layout(h_pad=4.0, w_pad=3.0)
    figure.suptitle('', x=0.5)
    axis.set_ylabel('Selection Time (Sec)', fontsize=8)
    axis.set_xlabel('Target Spacing (cm)', fontsize=8)
    x_axis = np.arange(len(xaxis_labels))
    axis.set_ylim(0,2.5)
    # 'BareHandIntenSelect', 'ControllerIntenSelect', 'BareHandTracking','ControllerTracking'
    if tech_type1 == 'BareHandIntenSelect':
        tech_type1 = 'Score-based Hand Tracking'

    if tech_type2 == 'ControllerIntenSelect':
        tech_type2 = 'Score-based Controller Tracking'

    if tech_type3 == 'BareHandTracking':
        tech_type3 = 'Direct Hand Tracking'

    if tech_type4 == 'ControllerTracking':
        tech_type4 = 'Direct Controller Tracking'

    axis.bar(x_axis - 0.15, data_selection_time_type1, width=0.15, label = tech_type1, 
            color = bar_colors_group1[0], yerr = data_selection_sem_type1 , error_kw= {'elinewidth':1}, ecolor='black', capsize=3)
    axis.bar(x_axis, data_selection_time_type2, width=0.15, label = tech_type2, 
            color = bar_colors_group1[1],  yerr = data_selection_sem_type2, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[0])
    axis.bar(x_axis + 0.15, data_selection_time_type3, width=0.15, label = tech_type3, 
            color = bar_colors_group1[2],  yerr = data_selection_sem_type3, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[1])
    axis.bar(x_axis + 0.3, data_selection_time_type4, width=0.15, label = tech_type4, 
            color = bar_colors_group1[3],  yerr = data_selection_sem_type4, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[2])

    #axis.set_ylabel('Selection Time (Sec)', fontsize=8);
    axis.tick_params(bottom = False, left = False);
    axis.set_xticks(np.arange(len(xaxis_labels)))
    axis.set_xticklabels(xaxis_labels)
    axis.set_axisbelow(True)
    axis.yaxis.grid(visible=True, linestyle='--', linewidth=0.5);
    axis.spines['right'].set_visible(False);
    axis.spines['top'].set_visible(False);
    # axis.legend(loc='upper right', bbox_to_anchor=(1.03, 1.02))

    return

def draw_bar_plot_accuracy_spacing(tech_type1, tech_type2, tech_type3, tech_type4):
    data1 = read_from_numpy('./output_numpy/' + tech_type1 + '_spacing_03_data.npy')
    data2 = read_from_numpy('./output_numpy/' + tech_type2 + '_spacing_03_data.npy')
    data3 = read_from_numpy('./output_numpy/' + tech_type3 + '_spacing_03_data.npy')
    data4 = read_from_numpy('./output_numpy/' + tech_type4 + '_spacing_03_data.npy')

    data5 = read_from_numpy('./output_numpy/' + tech_type1 + '_spacing_05_data.npy')
    data6 = read_from_numpy('./output_numpy/' + tech_type2 + '_spacing_05_data.npy')
    data7 = read_from_numpy('./output_numpy/' + tech_type3 + '_spacing_05_data.npy')
    data8 = read_from_numpy('./output_numpy/' + tech_type4 + '_spacing_05_data.npy')

    data9 = read_from_numpy('./output_numpy/' + tech_type1 + '_spacing_07_data.npy')
    data10 = read_from_numpy('./output_numpy/' + tech_type2 + '_spacing_07_data.npy')
    data11 = read_from_numpy('./output_numpy/' + tech_type3 + '_spacing_07_data.npy')
    data12 = read_from_numpy('./output_numpy/' + tech_type4 + '_spacing_07_data.npy')

    title = 'Selection Time for ' + tech_type1 + ', ' + tech_type2 + ', ' + tech_type3 + ' and ' + tech_type4
    ylabel = 'Selection Time (s)'

    xaxis_labels = ['spacing = 30', 'spacing = 50', 'spacing = 70']
    plt.style.use('ieee')
    plt.rcParams["font.family"] = "sans-serif"

    data_selection_time_type1 = [data1['global_error_rate']*100, data5['global_error_rate']*100, data9['global_error_rate']*100]
    data_selection_sem_type1 = [data1['global_error_rate_sem']*100, data5['global_error_rate_sem']*100, data9['global_error_rate_sem']*100]

    data_selection_time_type2 = [data2['global_error_rate']*100, data6['global_error_rate']*100, data10['global_error_rate']*100]
    data_selection_sem_type2 = [data2['global_error_rate_sem']*100, data6['global_error_rate_sem']*100, data10['global_error_rate_sem']*100]

    data_selection_time_type3 = [data3['global_error_rate']*100, data7['global_error_rate']*100, data11['global_error_rate']*100]
    data_selection_sem_type3 = [data3['global_error_rate_sem']*100, data7['global_error_rate_sem']*100, data11['global_error_rate_sem']*100]


    data_selection_time_type4 = [data4['global_error_rate']*100, data8['global_error_rate']*100, data12['global_error_rate']*100]
    data_selection_sem_type4 = [data4['global_error_rate_sem']*100, data8['global_error_rate_sem']*100, data12['global_error_rate_sem']*100]

    figure, axis = plt.subplots(1, 1, figsize=(5, 4))
    figure.set_dpi(800);
    figure.tight_layout(pad=4.0) 
    #figure.tight_layout(h_pad=4.0, w_pad=3.0)
    figure.suptitle('', x=0.5)
    axis.set_ylabel('Selection Accuracy (%)', fontsize=8)
    axis.set_xlabel('Target Spacing (cm)', fontsize=8)
    x_axis = np.arange(len(xaxis_labels))

    # 'BareHandIntenSelect', 'ControllerIntenSelect', 'BareHandTracking','ControllerTracking'
    if tech_type1 == 'BareHandIntenSelect':
        tech_type1 = 'Score-based Hand Tracking'

    if tech_type2 == 'ControllerIntenSelect':
        tech_type2 = 'Score-based Controller Tracking'

    if tech_type3 == 'BareHandTracking':
        tech_type3 = 'Direct Hand Tracking'

    if tech_type4 == 'ControllerTracking':
        tech_type4 = 'Direct Controller Tracking'

    axis.bar(x_axis - 0.15, data_selection_time_type1, width=0.15, label = tech_type1, 
            color = bar_colors_group1[0], yerr = data_selection_sem_type1 , error_kw= {'elinewidth':1}, ecolor='black', capsize=3)
    axis.bar(x_axis, data_selection_time_type2, width=0.15, label = tech_type2, 
            color = bar_colors_group1[1],  yerr = data_selection_sem_type2, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[0])
    axis.bar(x_axis + 0.15, data_selection_time_type3, width=0.15, label = tech_type3, 
            color = bar_colors_group1[2],  yerr = data_selection_sem_type3, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[1])
    axis.bar(x_axis + 0.3, data_selection_time_type4, width=0.15, label = tech_type4, 
            color = bar_colors_group1[3],  yerr = data_selection_sem_type4, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[2])

    #axis.set_ylabel('Selection Time (Sec)', fontsize=8);
    axis.tick_params(bottom = False, left = False);
    axis.set_xticks(np.arange(len(xaxis_labels)))
    axis.set_xticklabels(xaxis_labels)
    axis.set_axisbelow(True)
    axis.yaxis.grid(visible=True, linestyle='--', linewidth=0.5);
    axis.spines['right'].set_visible(False);
    axis.spines['top'].set_visible(False);
    # axis.legend(loc='upper right', bbox_to_anchor=(1.03, 1.02))

    return

def draw_bar_plot_Heisenberg_errorrate_spacing(tech_type1, tech_type2, tech_type3, tech_type4):
    data1 = read_from_numpy('./output_numpy/' + tech_type1 + '_spacing_03_data.npy')
    data2 = read_from_numpy('./output_numpy/' + tech_type2 + '_spacing_03_data.npy')
    data3 = read_from_numpy('./output_numpy/' + tech_type3 + '_spacing_03_data.npy')
    data4 = read_from_numpy('./output_numpy/' + tech_type4 + '_spacing_03_data.npy')

    data5 = read_from_numpy('./output_numpy/' + tech_type1 + '_spacing_05_data.npy')
    data6 = read_from_numpy('./output_numpy/' + tech_type2 + '_spacing_05_data.npy')
    data7 = read_from_numpy('./output_numpy/' + tech_type3 + '_spacing_05_data.npy')
    data8 = read_from_numpy('./output_numpy/' + tech_type4 + '_spacing_05_data.npy')

    data9 = read_from_numpy('./output_numpy/' + tech_type1 + '_spacing_07_data.npy')
    data10 = read_from_numpy('./output_numpy/' + tech_type2 + '_spacing_07_data.npy')
    data11 = read_from_numpy('./output_numpy/' + tech_type3 + '_spacing_07_data.npy')
    data12 = read_from_numpy('./output_numpy/' + tech_type4 + '_spacing_07_data.npy')

    title = 'Selection Time for ' + tech_type1 + ', ' + tech_type2 + ', ' + tech_type3 + ' and ' + tech_type4
    ylabel = 'Selection Time (s)'

    xaxis_labels = ['spacing = 30', 'spacing = 50', 'spacing = 70']
    plt.style.use('ieee')
    plt.rcParams["font.family"] = "sans-serif"

    data_selection_time_type1 = [data1['global_H_error_rate']*100, data5['global_H_error_rate']*100, data9['global_H_error_rate']*100]
    data_selection_sem_type1 = [data1['global_H_error_rate_sem']*100, data5['global_H_error_rate_sem']*100, data9['global_H_error_rate_sem']*100]

    data_selection_time_type2 = [data2['global_H_error_rate']*100, data6['global_H_error_rate']*100, data10['global_H_error_rate']*100]
    data_selection_sem_type2 = [data2['global_H_error_rate_sem']*100, data6['global_H_error_rate_sem']*100, data10['global_H_error_rate_sem']*100]

    data_selection_time_type3 = [data3['global_H_error_rate']*100, data7['global_H_error_rate']*100, data11['global_H_error_rate']*100]
    data_selection_sem_type3 = [data3['global_H_error_rate_sem']*100, data7['global_H_error_rate_sem']*100, data11['global_H_error_rate_sem']*100]


    data_selection_time_type4 = [data4['global_H_error_rate']*100, data8['global_H_error_rate']*100, data12['global_H_error_rate']*100]
    data_selection_sem_type4 = [data4['global_H_error_rate_sem']*100, data8['global_H_error_rate_sem']*100, data12['global_H_error_rate_sem']*100]

    figure, axis = plt.subplots(1, 1, figsize=(5, 4))
    figure.set_dpi(800);
    figure.tight_layout(pad=4.0) 
    #figure.tight_layout(h_pad=4.0, w_pad=3.0)
    figure.suptitle('', x=0.5)
    axis.set_ylabel('Heisenberg Error Rate (%)', fontsize=8)
    axis.set_xlabel('Target Spacing (cm)', fontsize=8)
    x_axis = np.arange(len(xaxis_labels))
    axis.set_ylim(0,50)

    # 'BareHandIntenSelect', 'ControllerIntenSelect', 'BareHandTracking','ControllerTracking'
    if tech_type1 == 'BareHandIntenSelect':
        tech_type1 = 'Score-based Hand Tracking'

    if tech_type2 == 'ControllerIntenSelect':
        tech_type2 = 'Score-based Controller Tracking'

    if tech_type3 == 'BareHandTracking':
        tech_type3 = 'Direct Hand Tracking'

    if tech_type4 == 'ControllerTracking':
        tech_type4 = 'Direct Controller Tracking'

    axis.bar(x_axis - 0.15, data_selection_time_type1, width=0.15, label = tech_type1, 
            color = bar_colors_group1[0], yerr = data_selection_sem_type1 , error_kw= {'elinewidth':1}, ecolor='black', capsize=3)
    axis.bar(x_axis, data_selection_time_type2, width=0.15, label = tech_type2, 
            color = bar_colors_group1[1],  yerr = data_selection_sem_type2, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[0])
    axis.bar(x_axis + 0.15, data_selection_time_type3, width=0.15, label = tech_type3, 
            color = bar_colors_group1[2],  yerr = data_selection_sem_type3, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[1])
    axis.bar(x_axis + 0.3, data_selection_time_type4, width=0.15, label = tech_type4, 
            color = bar_colors_group1[3],  yerr = data_selection_sem_type4, error_kw= {'elinewidth':1}, ecolor='black', capsize=3, hatch=hatch_patterns[2])

    #axis.set_ylabel('Selection Time (Sec)', fontsize=8);
    axis.tick_params(bottom = False, left = False);
    axis.set_xticks(np.arange(len(xaxis_labels)))
    axis.set_xticklabels(xaxis_labels)
    axis.set_axisbelow(True)
    axis.yaxis.grid(visible=True, linestyle='--', linewidth=0.5);
    axis.spines['right'].set_visible(False);
    axis.spines['top'].set_visible(False);
    # axis.legend(loc='upper right', bbox_to_anchor=(1.03, 1.02))

    return

def main():
    draw_bar_plot_selectiontime_radius('BareHandIntenSelect', 'ControllerIntenSelect', 'BareHandTracking','ControllerTracking')
    plt.savefig(f'./output_image/selection_time_radius.png', bbox_inches='tight')
    draw_bar_plot_accuracy_radius('BareHandIntenSelect', 'ControllerIntenSelect', 'BareHandTracking','ControllerTracking')
    plt.savefig(f'./output_image/accuracy_radius.png', bbox_inches='tight')
    draw_bar_plot_Heisenberg_errorrate_radius('BareHandIntenSelect', 'ControllerIntenSelect', 'BareHandTracking','ControllerTracking')
    plt.savefig(f'./output_image/HeisenbergErrorRate_radius.png', bbox_inches='tight')
    draw_bar_plot_selectiontime_spacing('BareHandIntenSelect', 'ControllerIntenSelect', 'BareHandTracking','ControllerTracking')
    plt.savefig(f'./output_image/selection_time_spacing.png', bbox_inches='tight')
    draw_bar_plot_accuracy_spacing('BareHandIntenSelect', 'ControllerIntenSelect', 'BareHandTracking','ControllerTracking')
    plt.savefig(f'./output_image/accuracy_spacing.png', bbox_inches='tight')
    draw_bar_plot_Heisenberg_errorrate_spacing('BareHandIntenSelect', 'ControllerIntenSelect', 'BareHandTracking','ControllerTracking')
    plt.savefig(f'./output_image/HeisenbergErrorRate_spacing.png', bbox_inches='tight')

if __name__ == '__main__':
    
    main()