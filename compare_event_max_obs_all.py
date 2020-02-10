
###############################################################################
# compare_event_max_obs_all.py 
# author: Craig Smith 
# purpose: plot event max observed for all events 
# revision history:  
#   01/01/2020 - original 
# data required: 
#   obs data 
# usage:  
#   - 
# to do: 
#   - 
# notes: 
#   - 
# debugging: 
#   - 
###############################################################################


###############################################################################
# module import and set directories
 
#manual_mode = False
#manual_mode = True

host_name = 'chromebook'
project_name = 'offshore_winds'
 
import os
import sys
#import requests 
from datetime import datetime as dt
from datetime import timedelta as td
#import time 
#import pandas 
#import numpy 
import argparse 
import numpy
import xarray
from netCDF4 import Dataset 


import matplotlib
#if (manual_mode): 
#    matplotlib.use('Agg') 
#    matplotlib.use('TkAgg') # MUST BE CALLED BEFORE IMPORTING plt
import matplotlib.pyplot as plt
from matplotlib.dates import drange, DateFormatter
from matplotlib.ticker import MultipleLocator 

import matplotlib.ticker as mticker
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from cartopy.io import shapereader
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
import cartopy.feature as cfeature
from cartopy.feature import ShapelyFeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

if   (host_name == 'chromebook'): # windows
    dir_work = '/home/craigmatthewsmith/projects/'+project_name
    dir_scripts = '/home/craigmatthewsmith/scripts'
    dir_data_base = '/home/craigmatthewsmith/data'
    dir_shp = os.path.join(dir_data_base, 'shp_data')
    dir_figs = os.path.join(dir_scripts,'model_process')
     
sys.path.append(os.path.join(dir_scripts, 'function_library'))
from instantiate_logger             import instantiate_logger
from define_daylight_savings_or_not import define_daylight_savings_or_not
#from read_stn_metadata_from_csv     import read_stn_metadata_from_csv
from close_logger                   import close_logger
from remove_old_logs                import remove_old_logs 
from build_model_local_file_names                      import build_model_local_file_names
from read_stn_metadata_from_csv import read_stn_metadata_from_csv
from read_mesowest_api_csv_data import read_mesowest_api_csv_data
from define_datetime_axis import define_datetime_axis

os.chdir(dir_work) 
print ('dir_work is %s'  % (os.getcwd())) 
dir_data_sfc_obs = os.path.join(dir_data_base, 'sfc_obs')
dir_data_model   = os.path.join(dir_data_base, 'model_data')
dir_data_sfc_obs_ingest  = os.path.join(dir_data_sfc_obs, 'ingest')
dir_data_sfc_obs_archive = os.path.join(dir_data_sfc_obs, 'archive')
    
# module import and set directories
###############################################################################


###############################################################################
# define starting time 

print      ('define_cron_start_time ') 
dt_cron_start_utc = dt.utcnow()    
(utc_conversion, time_zone_label) = define_daylight_savings_or_not(dt_cron_start_utc) 
dt_cron_start_lt = dt.utcnow() - td(hours=utc_conversion)
utc_conversion = 8
       
# define starting time 
###############################################################################


###############################################################################
# instantiate logger 

print      ('instantiate_logger begin' ) 
process_name = 'compare_event_max_obs_all'
log_file_name = 'log_'+process_name+'_'+project_name+'_'+dt_cron_start_lt.strftime('%Y-%m-%d_%H-%M')+'.txt' 
log_name_full_file_path = os.path.join(dir_work, 'archive_logs', log_file_name) 
logger = instantiate_logger(log_name_full_file_path, dt_cron_start_lt) 
print      ('instantiate_logger end' ) 

# instantiate logger 
###############################################################################


###############################################################################
# define event and inits to use 

#event_list  = ['2018_10_14_event', '2018_11_08_event', '2019_10_09_event', '2019_10_23_event', '2019_10_27_event', '2017_10_08_event'] 
#event_ticks = ['10/14/2018',       '11/08/2018',       '10/09/2019',       '10/23/2019',       '10/27/2019',       '10/08/2017'] 

event_list  = ['2019_10_09_event', '2019_10_23_event', '2019_10_27_event'] 
event_ticks = ['10/09/2019',       '10/23/2019',       '10/27/2019',     ] 
# rbg

n_events = len(event_list)
event_axis = numpy.arange(0, n_events, 1)

# '2017_10_08_event'
# no model data 

# define event and inits to use 
###############################################################################

[ws_crit, wsgd_crit, wsgt_crit] = [25.0, 45.0, 55.0]



###############################################################################
# read stn_info 

use_stn = 'all'
#use_stn = 'mnet=2' # RAWS only  
print_stn_info = True
print      ('read stn_info start ' )
logger.info('read stn_info start ' ) 
(dict_stn_metadata) = read_stn_metadata_from_csv(dir_work, project_name, use_stn, print_stn_info)

# read stn_info 
###############################################################################


###############################################################################
# initialize obs arrays 

ws_max_obs_s_event  = numpy.full([dict_stn_metadata['n_stn'], n_events], numpy.nan, dtype='float') 
wsg_max_obs_s_event = numpy.full([dict_stn_metadata['n_stn'], n_events], numpy.nan, dtype='float') 
rh_min_obs_s_event  = numpy.full([dict_stn_metadata['n_stn'], n_events], numpy.nan, dtype='float') 

nt = 2400
ws_obs_s_t_event  = numpy.full([dict_stn_metadata['n_stn'], nt, n_events], numpy.nan, dtype='float') 
wsg_obs_s_t_event = numpy.full([dict_stn_metadata['n_stn'], nt, n_events], numpy.nan, dtype='float') 
rh_obs_s_t_event  = numpy.full([dict_stn_metadata['n_stn'], nt, n_events], numpy.nan, dtype='float') 
nt_max = 0

# initialize obs arrays 
###############################################################################

ws_units = 'mph'
temp_units = 'F'

###############################################################################
# read mesowest api sfc data 

print      ('processing sfc obs data ') 
logger.info('processing sfc obs data ') 

dt_start_temp = dt.now() 

dir_data_sfc_obs = os.path.join(dir_data_base, 'sfc_obs')


replace_nan_with_null = False

#s = 358
#f = 0

# representative stations pg132 and pg328 and plot_vs_time to confirm time window
s = 217 # concow road
s = 610 # mt st helena west
s = 360 # HWKC1

s = 100
e = 0
for e in range(0, n_events, 1):
    print      ('  processing e %s of %s ' % (e, n_events))
    logger.info('  processing e %s of %s ' % (e, n_events))
    #for s in range(45, 46, 1): 
    for s in range(0, dict_stn_metadata['n_stn'], 1): 
        #if ('PG328' in dict_stn_metadata['stn_id'][s]):
        print      ('    processing s %s, s = %s of %s ' % (dict_stn_metadata['stn_id'][s], s, dict_stn_metadata['n_stn']))  
        logger.info('    processing s %s, s = %s of %s ' % (dict_stn_metadata['stn_id'][s], s, dict_stn_metadata['n_stn']))  
        #print(s)
        file_name_full_path = os.path.join(dir_data_sfc_obs, event_list[e], 'stn_obs_'+dict_stn_metadata['stn_id'][s]+'.csv')    
        if not os.path.isfile(file_name_full_path):
            print      ('    ERROR - missing file ') 
            logger.info('    ERROR - missing file ') 
        else:    
            (stn_read_df) = read_mesowest_api_csv_data(file_name_full_path, replace_nan_with_null)
            # units conversion 
            if   (ws_units == 'mph'): 
                stn_read_df['ws']  = 2.2369*stn_read_df['ws']    
                stn_read_df['wsg'] = 2.2369*stn_read_df['wsg']    
            if   (temp_units == 'F'): # may need to convert K here 
                stn_read_df['temp'] = (stn_read_df['temp']*9.0/5.0)+32.0
            ws_read  = numpy.array(stn_read_df['ws'])
            wd_read  = numpy.array(stn_read_df['wd'])
            wsg_read = numpy.array(stn_read_df['wsg'])
            rh_read  = numpy.array(stn_read_df['rh'])
            ws_max_obs_s_event [s,e] = numpy.nanmax( ws_read)
            wsg_max_obs_s_event[s,e] = numpy.nanmax(wsg_read)
            rh_min_obs_s_event [s,e] = numpy.nanmin( rh_read)
            nt_temp = len(ws_read)
            if (nt_temp > nt_max):
                nt_max = nt_temp
            ws_obs_s_t_event [s,0:nt_temp, e] =  ws_read
            wsg_obs_s_t_event[s,0:nt_temp, e] = wsg_read
            rh_obs_s_t_event [s,0:nt_temp, e] =  rh_read
            #stn_read_df.index()
            dt_read_utc = stn_read_df.index
            dt_read_pst = dt_read_utc - td(hours=8)
                
            del ws_read, wsg_read, rh_read, wd_read, stn_read_df, dt_read_pst, dt_read_utc

# 
###############################################################################


###############################################################################
# plot_control
    

#[wsg_min, wsg_max, wsg_int] = [0.0, 45.0, 5.0]

width_line = 3.0 
size_marker = 10

if (ws_units == 'mph'): 
    ws_units_label = 'mph'
    #[ ws_min,  ws_max,  ws_int] = [15.0,   80.0,  5.0]
    #[wsg_min, wsg_max, wsg_int] = [35.0,  110.0,  5.0]
    #[ ws_min,  ws_max,  ws_int] = [0.0,  65.0,  10.0]
    #[wsg_min, wsg_max, wsg_int] = [0.0,  85.0,  5.0]
    [ ws_min,  ws_max,  ws_int] = [0.0, 80.0, 10.0] # was 0, 30, 5                                                                
    [wsg_min, wsg_max, wsg_int] = [0.0, 110.0, 20.0]
ws_ticks  = numpy.arange( ws_min,  ws_max+ ws_int,  ws_int)
wsg_ticks = numpy.arange(wsg_min, wsg_max+wsg_int, wsg_int)


[ele_min, ele_max, ele_int] = [0.0, 5500.0, 500.0]
ele_ticks = numpy.arange(ele_min, ele_max+ele_int, ele_int)

#[rh_min, rh_max, rh_int] = [0.0, 100.0, 10.0]
[rh_min, rh_max, rh_int] = [0.0, 20.0, 2.0]
rh_ticks = numpy.arange(rh_min, rh_max+rh_int, rh_int)


#[percent_min, percent_max, percent_int] = [0.0,  45.0,  10.0]
#percent_ticks = numpy.arange(percent_min, percent_max+percent_int, percent_int)


size_scatter = 50
color_list = ['r', 'b', 'g', 'c', 'm', 'y']
alpha_level = 0.5

# plot_control
###############################################################################




#plot_area = ['nor_ca', 'nor_bay', 'nor_sierra','bay', 'cen_sierra', 'nor_valley', 'nor_coast']
# nor_bay         
#[lon_min, lon_max, lon_int] = [-123.6, -121.9, 0.4]
#[lat_min, lat_max, lat_int] = [  37.8,   39.6, 0.2]
# no ca
#[lon_min, lon_max, lon_int] = [-124.5, -117.0, 1.0]
#[lat_min, lat_max, lat_int] = [  36.0,   42.2, 0.5]
# nor_sierra 
#[lon_min, lon_max, lon_int] = [-122.2, -120.0, 0.4] # -122.0, -117.5, 1.0
#[lat_min, lat_max, lat_int] = [  38.6,   40.2, 0.2] # 37.0,   41.0, 0.5

# napa and sonoma
[lon_min, lon_max, lon_int] = [-123.2, -122.1, 0.4]
[lat_min, lat_max, lat_int] = [  38.2,   39.2, 0.1]

mask_area = ((dict_stn_metadata['stn_lon'] > lon_min) & (dict_stn_metadata['stn_lon'] < lon_max) & (dict_stn_metadata['stn_lat'] > lat_min) & (dict_stn_metadata['stn_lat'] < lat_max))

#temp1 = dict_stn_metadata['stn_id'][mask_area]
#len(temp1)        


# mask out ocean
#mask_hgt = (hgt_2d < 10.0)


###############################################################################
# plot_scatter_vs_ele

########################################
# ws max
fig_num = 401 
fig = plt.figure(num=fig_num,figsize=(8,8)) 
plt.clf()
for e in range(0, n_events, 1):
    #plt.scatter(ws_max_obs_s_event[:,e], dict_stn_metadata['stn_ele'], s=size_scatter, marker='o',color=color_list[e], edgecolor='k',alpha=alpha_level)
    plt.scatter(ws_max_obs_s_event[mask_area,e], dict_stn_metadata['stn_ele'][mask_area], s=size_scatter, marker='o',color=color_list[e], edgecolor='k',alpha=alpha_level)
for dum in numpy.arange(ele_min, ele_max+ws_int, ele_int):
    plt.plot([ws_min, ws_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
for dum in numpy.arange(ws_min, ws_max+ws_int, ws_int):
    plt.plot([dum, dum], [ele_min, ele_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
#plt.plot([ws_min, ws_max], [ws_min, ws_max], 'k', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
plt.xticks(ws_ticks, fontsize=14)
plt.yticks(ele_ticks, fontsize=14, visible=True)
plt.xlim([ws_min, ws_max])
plt.ylim([ele_min, ele_max])
#plt.xlabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
#plt.ylabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.xlabel('event maximums ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.ylabel('station elevation [ft]', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.title('station elevation vs event max ws north bay only \n10/09/19 (r), 10/23/19 (b), 10/27/19 (g)' , \
    fontsize=14, loc='left', weight = 'bold')
plt.show()
plt.tight_layout()        
filename = 'scatter_ele_vs_ws' 
plot_name = os.path.join(dir_work, 'figs_vs_elevation', filename) 
dpi_level = 400 # 400        
#plt.savefig(plot_name)
plt.savefig(plot_name, dpi=dpi_level) 
#fig.clf()
#plt.close()        


########################################
# wsg max 
fig_num = 402 
fig = plt.figure(num=fig_num,figsize=(8,8)) 
plt.clf()
for e in range(0, n_events, 1):
    #plt.scatter(ws_max_obs_s_event[:,e], dict_stn_metadata['stn_ele'], s=size_scatter, marker='o',color=color_list[e], edgecolor='k',alpha=alpha_level)
    plt.scatter(wsg_max_obs_s_event[mask_area,e], dict_stn_metadata['stn_ele'][mask_area], s=size_scatter, marker='o',color=color_list[e], edgecolor='k',alpha=alpha_level)
for dum in numpy.arange(ele_min, ele_max+ws_int, ele_int):
    plt.plot([wsg_min, wsg_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
for dum in numpy.arange(wsg_min, wsg_max+wsg_int, wsg_int):
    plt.plot([dum, dum], [ele_min, ele_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
#plt.plot([ws_min, ws_max], [ws_min, ws_max], 'k', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
plt.xticks(wsg_ticks, fontsize=14)
plt.yticks(ele_ticks, fontsize=14, visible=True)
plt.xlim([wsg_min, wsg_max])
plt.ylim([ele_min, ele_max])
#plt.xlabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
#plt.ylabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.xlabel('event maximums wsg [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.ylabel('station elevation [ft]', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.title('station elevation vs event max wsg north bay only \n10/09/19 (r), 10/23/19 (b), 10/27/19 (g)' , \
    fontsize=14, loc='left', weight = 'bold')
plt.show()
plt.tight_layout()        
filename = 'scatter_ele_vs_wsg' 
plot_name = os.path.join(dir_work, 'figs_vs_elevation', filename) 
dpi_level = 400 # 400        
#plt.savefig(plot_name)
plt.savefig(plot_name, dpi=dpi_level) 
#fig.clf()
#plt.close()        


########################################
# rh min 
fig_num = 403 
fig = plt.figure(num=fig_num,figsize=(8,8)) 
plt.clf()
for e in range(0, n_events, 1):
    #plt.scatter(rh_max_obs_s_event[:,e], dict_stn_metadata['stn_ele'], s=size_scatter, marker='o',color=color_list[e], edgecolor='k',alpha=alpha_level)
    plt.scatter(rh_min_obs_s_event[mask_area,e], dict_stn_metadata['stn_ele'][mask_area], s=size_scatter, marker='o',color=color_list[e], edgecolor='k',alpha=alpha_level)
for dum in numpy.arange(ele_min, ele_max+rh_int, ele_int):
    plt.plot([rh_min, rh_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
for dum in numpy.arange(rh_min, rh_max+rh_int, rh_int):
    plt.plot([dum, dum], [ele_min, ele_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
#plt.plot([rh_min, rh_max], [rh_min, rh_max], 'k', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
plt.xticks(rh_ticks, fontsize=14)
plt.yticks(ele_ticks, fontsize=14, visible=True)
plt.xlim([rh_min, rh_max])
plt.ylim([ele_min, ele_max])
#plt.xlabel('rh [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
#plt.ylabel('rh [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.xlabel('event minimum rh [%]', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.ylabel('station elevation [ft]', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.title('station elevation vs event min rh north bay only \n10/09/19 (r), 10/23/19 (b), 10/27/19 (g)' , \
    fontsize=14, loc='left', weight = 'bold')
plt.show()
plt.tight_layout()        
filename = 'scatter_ele_vs_rh' 
plot_name = os.path.join(dir_work, 'figs_vs_elevation', filename) 
dpi_level = 400 # 400        
#plt.savefig(plot_name)
plt.savefig(plot_name, dpi=dpi_level) 
#fig.clf()
#plt.close()        




size_scatter = 10
alpha_level = 0.1

########################################
# ws all
fig_num = 411 
fig = plt.figure(num=fig_num,figsize=(8,8)) 
plt.clf()
for e in range(0, n_events, 1):
    for s in range(0, dict_stn_metadata['n_stn'], 1):
        if ((dict_stn_metadata['stn_lon'][s] > lon_min) & (dict_stn_metadata['stn_lon'][s] < lon_max) & (dict_stn_metadata['stn_lat'][s] > lat_min) & (dict_stn_metadata['stn_lat'][s] < lat_max)):
            plt.scatter(wsg_obs_s_t_event[s,:, e], numpy.full([nt], dict_stn_metadata['stn_ele'][s]), s=size_scatter, marker='o',color=color_list[e], edgecolor='k',alpha=alpha_level)
for dum in numpy.arange(ele_min, ele_max+ws_int, ele_int):
    plt.plot([ws_min, ws_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
for dum in numpy.arange(ws_min, ws_max+ws_int, ws_int):
    plt.plot([dum, dum], [ele_min, ele_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
#plt.plot([ws_min, ws_max], [ws_min, ws_max], 'k', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
plt.xticks(ws_ticks, fontsize=14)
plt.yticks(ele_ticks, fontsize=14, visible=True)
plt.xlim([ws_min, ws_max])
plt.ylim([ele_min, ele_max])
#plt.xlabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
#plt.ylabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.xlabel('event maximums ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.ylabel('station elevation [ft]', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.title('station elevation vs event max ws north bay only \n10/09/19 (r), 10/23/19 (b), 10/27/19 (g)' , \
    fontsize=14, loc='left', weight = 'bold')
plt.show()
plt.tight_layout()        
filename = 'scatter_ele_vs_ws_all' 
plot_name = os.path.join(dir_work, 'figs_vs_elevation', filename) 
dpi_level = 400 # 400        
#plt.savefig(plot_name)
plt.savefig(plot_name, dpi=dpi_level) 
#fig.clf()
#plt.close()        



# plot_scatter_event_intercomparison
###############################################################################


###############################################################################
# remove old log files 

print      ('remove old log files begin ')
logger.info('remove old log files begin ')
n_days_to_retain_logs = 7.0
remove_old_logs(log_name_full_file_path, process_name, project_name, n_days_to_retain_logs)
print      ('remove old log files end ')     
logger.info('remove old log files end ') 

# remove old log files 
###############################################################################


###############################################################################
# close logger 

print      ('close_logger begin ')
logger.info('close_logger begin ')
close_logger(logger, process_name, dt_cron_start_lt, utc_conversion, time_zone_label) 

# close logger 
###############################################################################
