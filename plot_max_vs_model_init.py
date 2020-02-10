
###############################################################################
# plot_max_vs_model_init.py
# author: Craig Smith 
# purpose: plot event max observed and forecast ws and wsg from hrrr and nam 
# revision history:  
#   11/02/2019 - original 
# data required: 
#   grib files from download_model_data.py 
# usage:  
#   python /home/craigmatthewsmith/scripts/model_process/plot_max_ws_maps.py --model_name='nam' --dt_init_utc_str='2019-10-05_12' --dt_min_plot_utc_str='2019-10-05_20' --dt_max_plot_utc_str='2019-10-06_20'
#   python /home/craigmatthewsmith/scripts/model_process/plot_max_ws_maps.py --model_name='hrrr' --dt_init_utc_str='2019-10-05_12' --dt_min_plot_utc_str='2019-10-05_20' --dt_max_plot_utc_str='2019-10-06_20'
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
manual_mode = True

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
dir_data_sfc_obs = os.path.join(dir_data_base, 'surface_data', 'mesowest_data', project_name)
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
process_name = 'plot_max_vs_model_init'
log_file_name = 'log_'+process_name+'_'+project_name+'_'+dt_cron_start_lt.strftime('%Y-%m-%d_%H-%M')+'.txt' 
log_name_full_file_path = os.path.join(dir_work, 'archive_logs', log_file_name) 
logger = instantiate_logger(log_name_full_file_path, dt_cron_start_lt) 
print      ('instantiate_logger end' ) 

# instantiate logger 
###############################################################################


###############################################################################
# define event and inits to use 

########################################
event = '2019_10_27_event'
# U 10/27 1 am PST - U 10/27 23:59 pm PST 
dt_min_plot_utc_str = '2019-10-26_08'
dt_max_plot_utc_str = '2019-10-29_08'
dt_init_utc_start = dt(2019, 10, 24, 12)
dt_init_utc_end   = dt(2019, 10, 28,  0)
# hrrr
# 2019-10-26_18 earliest, erase all before
# 2019-10-27_00 best, retain on local
# 2019-10-27_12 latest, erase all after 


######################################## 
#event = '2018_10_14_event'
# event max 2018/10/14 12 - 2018/10/15 12 PST 
#dt_min_plot_utc_str = '2018-10-13_08'
#dt_max_plot_utc_str = '2018-10-16_16'
#dt_init_utc_start = dt(2018, 10, 13, 12)
#dt_init_utc_end   = dt(2018, 10, 15, 12)

######################################## 
#event = '2018_11_08_event'
# event max 2018-11-08_00 to 2018-11-09_00 PST
#dt_min_plot_utc_str = '2018-11-06_08'
#dt_max_plot_utc_str = '2018-11-10_16'
#dt_init_utc_start = dt(2018, 11,  6, 12)
#dt_init_utc_end   = dt(2018, 11,  9, 00)

######################################## 
#event = '2019_10_09_event'
# W 10/09 6 am PST - R 10/10 6 pm PST 
#dt_min_plot_utc_str = '2019-10-09_08'
#dt_max_plot_utc_str = '2019-10-11_08'
#dt_init_utc_start = dt(2019, 10,  7,  0)
#dt_init_utc_end   = dt(2019, 10, 11,  0)
# hrrr
# 2019-10-09_06 earliest, erase all before
# 2019-10-09_12 best, retain on local
# 2019-10-10_00 latest, erase all after
#model_name = 'hrrr'
# earliest possible, ends 2019-10-10_10 PST 
# dt_init_utc_str     = '2019-10-09_06'
# best / retain on local 
#dt_init_utc_str     = '2019-10-09_12'
# dt_init_utc_str     = '2019-10-09_18'
# latest possible starts 2019-10-09_16
# dt_init_utc_str     = '2019-10-10_00'

######################################## 
#event = '2019_10_23_event'
# W 10/23 6 am PST - R 10/24 6 pm PST 
#dt_min_plot_utc_str = '2019-10-23_08'
#dt_max_plot_utc_str = '2019-10-25_08'
#dt_init_utc_start = dt(2019, 10, 19,  0)
#dt_init_utc_end   = dt(2019, 10, 25,  0)
# hrrr
# 2019-10-23_06 earliest, erase all before, or 10-23_12
# 2019-10-23_12 best, retain on local, somehow missing 10-23_18 (can look for on gcp)
# 2019-10-24_00 latest, erase all after, or 10-23_18 









model_list = ['hrrr']
#model_list = ['hrrr', 'nam']
n_models = len(model_list)

interval_string = '6hr'
(dt_axis_init_utc, n_inits)   = define_datetime_axis(logger, dt_init_utc_start, dt_init_utc_end, interval_string)

dt_min_plot_utc = dt.strptime(dt_min_plot_utc_str,'%Y-%m-%d_%H')
dt_max_plot_utc = dt.strptime(dt_max_plot_utc_str,'%Y-%m-%d_%H')
dt_min_plot_pst = dt_min_plot_utc - td(hours=utc_conversion)
dt_max_plot_pst = dt_max_plot_utc - td(hours=utc_conversion)

# define event and inits to use 
###############################################################################


###############################################################################
# read_topo 
    
use_standalone_topo = False
if (use_standalone_topo):
    print      ('read_topo_data begin')
    logger.info('read_topo_data begin')
    
    file_name_temp_ingest = os.path.join(dir_work, 'nam_static.grib2')
    ds_sfc = xarray.open_dataset(file_name_temp_ingest, engine='cfgrib',
         backend_kwargs={'filter_by_keys': {'typeOfLevel': 'surface'}})
    lon_static_2d = numpy.array(ds_sfc['longitude'])
    lat_static_2d = numpy.array(ds_sfc['latitude'])
    hgt_static_2d = numpy.array(ds_sfc['orog'])
    hgt_static_2d = hgt_static_2d*3.28084 # m to ft

# read_topo 
###############################################################################

[ws_crit, wsgd_crit, wsgt_crit] = [25.0, 45.0, 55.0]

###############################################################################
# read_model_data

print      ('read_model_data begin')
logger.info('read_model_data begin')
print      ('plotting %s - %s PST ' %(dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H')))
logger.info('plotting %s - %s PST ' %(dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H')))

initial_read = False

# hrrr [ny, nx] = [1005, 596]

[lon_min, lon_max, lon_int] = [-124.5, -117.0, 1.0]
[lat_min, lat_max, lat_int] = [  36.0,   42.2, 0.5]

ws10_mean_model_init   = numpy.full([n_models, n_inits], numpy.nan, dtype=float)
wsg10_mean_model_init  = numpy.full([n_models, n_inits], numpy.nan, dtype=float)
ws10_crit_model_init   = numpy.full([n_models, n_inits], numpy.nan, dtype=float)
wsgd10_crit_model_init = numpy.full([n_models, n_inits], numpy.nan, dtype=float)
wsgt10_crit_model_init = numpy.full([n_models, n_inits], numpy.nan, dtype=float)

m = 0
f = 6
for m in range(0, n_models, 1):
    model_name = model_list[m]
    if   (model_name == 'hrrr'):
        model_forecast_horizon = 36 
    elif (model_name == 'nam'):
        model_forecast_horizon = 84    
    for f in range(0, n_inits, 1):
        dt_init_utc = dt_axis_init_utc[f]
        dt_model_initial_pst = dt_init_utc - td(hours=utc_conversion)
        dt_model_final_pst   = dt_model_initial_pst + td(hours=model_forecast_horizon)
        print      ('  %s init %s UTC,  %s - %s PST ' %(model_name, dt_init_utc.strftime('%Y-%m-%d_%H'), dt_model_initial_pst.strftime('%Y-%m-%d_%H'), dt_model_final_pst.strftime('%Y-%m-%d_%H')))
        logger.info('  %s init %s UTC,  %s - %s PST ' %(model_name, dt_init_utc.strftime('%Y-%m-%d_%H'), dt_model_initial_pst.strftime('%Y-%m-%d_%H'), dt_model_final_pst.strftime('%Y-%m-%d_%H')))
        file_name_read = os.path.join(dir_data_model, 'event_max', 'max_'+event+'_model_'+model_name+'_init_'+dt_init_utc.strftime('%Y-%m-%d_%H')+'.nc')
        if not os.path.isfile(file_name_read):
            print      ('  no max file found %s %s ' %(model_name, dt_init_utc.strftime('%Y-%m-%d_%H')))
            logger.info('  no max file found %s %s ' %(model_name, dt_init_utc.strftime('%Y-%m-%d_%H')))
        else:
            ncfile_read  = Dataset(file_name_read,'r') 
            #if not (initial_read):
            lon_2d = numpy.array(ncfile_read.variables['lon_2d'])
            lat_2d = numpy.array(ncfile_read.variables['lat_2d'])
            hgt_2d = numpy.array(ncfile_read.variables['hgt_2d'])
            hgt_2d = hgt_2d*3.28084 # m to ft            
            [ny, nx] = numpy.shape(lon_2d)
            mask_all = ((lon_2d > lon_min) & (lon_2d < lon_max) & (lat_2d > lat_min) & (lat_2d < lat_max) & (hgt_2d > 10.0))
            wsg10_max_2d = numpy.array(ncfile_read.variables['wsg10_max_2d'])
            ws10_max_2d  = numpy.array(ncfile_read.variables[ 'ws10_max_2d'])
            wsg10_max_2d = 2.23694*wsg10_max_2d
            ws10_max_2d  = 2.23694*ws10_max_2d        
            ncfile_read.close()
            print      ('  read file end ') 
            logger.info('  read file end ') 
            mask_ws   = (( ws10_max_2d >=   ws_crit) & (lon_2d > lon_min) & (lon_2d < lon_max) & (lat_2d > lat_min) & (lat_2d < lat_max) & (hgt_2d > 10.0))
            mask_wsgd = ((wsg10_max_2d >= wsgd_crit) & (lon_2d > lon_min) & (lon_2d < lon_max) & (lat_2d > lat_min) & (lat_2d < lat_max) & (hgt_2d > 10.0))
            mask_wsgt = ((wsg10_max_2d >= wsgt_crit) & (lon_2d > lon_min) & (lon_2d < lon_max) & (lat_2d > lat_min) & (lat_2d < lat_max) & (hgt_2d > 10.0))    
            ws10_mean_model_init [m,f] = numpy.nanmean( ws10_max_2d[mask_all])
            wsg10_mean_model_init[m,f] = numpy.nanmean(wsg10_max_2d[mask_all])
            ws10_crit_model_init  [m,f] = 100.0*float(len(ws10_max_2d[mask_ws  ]))/float(len(ws10_max_2d[mask_all]))
            wsgd10_crit_model_init[m,f] = 100.0*float(len(ws10_max_2d[mask_wsgd]))/float(len(ws10_max_2d[mask_all]))
            wsgt10_crit_model_init[m,f] = 100.0*float(len(ws10_max_2d[mask_wsgt]))/float(len(ws10_max_2d[mask_all]))
            del lon_2d, lat_2d, hgt_2d, ny, nx, mask_all, wsg10_max_2d, ws10_max_2d, mask_ws, mask_wsgd, mask_wsgt
        del dt_init_utc, file_name_read
    del model_name

# read_model_data
###############################################################################


###############################################################################
# plots 
    
dt_min_plot_utc = dt_init_utc_start - td(hours=0)
dt_max_plot_utc = dt_init_utc_end   + td(hours=0)

n_days_temp = (dt_max_plot_utc - dt_min_plot_utc).days

delta       = td(hours=24)
delta_lines = td(hours=12)
datetick_format = '%m/%d %H'    
#datetick_format = '%H'    
date_ticks = drange(dt_min_plot_utc, dt_max_plot_utc+delta, delta)
n_date_ticks = len(date_ticks) 

[wsg_min, wsg_max, wsg_int] = [0.0, 45.0, 5.0]

width_line = 3.0 
size_marker = 10


##################################
# 
fig_num = 201 
fig = plt.figure(num=fig_num,figsize=(10,5)) 
plt.clf()

plt.plot(dt_axis_init_utc, ws10_mean_model_init [0,:], 'r', linestyle='-', label='ws hrrr',  linewidth=width_line, marker='o', markersize=size_marker, markeredgecolor='k') 
#plt.plot(dt_axis_init_utc, ws10_mean_model_init [1,:], 'b', linestyle='-', label='ws nam',  linewidth=width_line, marker='o', markersize=size_marker, markeredgecolor='k') 
plt.plot(dt_axis_init_utc, wsg10_mean_model_init[0,:], 'g', linestyle='-', label='wsg hrrr',  linewidth=width_line, marker='o', markersize=size_marker, markeredgecolor='k') 
#plt.plot(dt_axis_init_utc, wsg10_mean_model_init[1,:], 'c', linestyle='-', label='wsg nam',  linewidth=width_line, marker='o', markersize=size_marker, markeredgecolor='k') 

for dum in numpy.arange(wsg_min, wsg_max+wsg_int, wsg_int):
    plt.plot([dt_min_plot_utc-td(hours=24), dt_max_plot_utc+td(hours=24)], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
for dum in matplotlib.dates.drange(dt_min_plot_utc, dt_max_plot_utc+4*delta_lines, delta_lines):
    plt.plot([dum, dum], [wsg_min, wsg_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 

plt.legend(loc=2,fontsize=12,ncol=1) 
plt.title('%s mean ws and wsg' % (event), \
     fontsize=14, loc='left')                     
plt.xlabel('model initialization [UTC]',fontsize=14,labelpad=0)            
plt.ylabel('ws [mph]',fontsize=14,labelpad=0)            
plt.yticks(numpy.arange(wsg_min, wsg_max+wsg_int, wsg_int))                     
plt.ylim([wsg_min, wsg_max])
plt.xlim([date_ticks[0], date_ticks[-1]])
plt.gca().xaxis.set_major_formatter(DateFormatter(datetick_format))
plt.xticks(date_ticks,visible=True) 
plt.show() 
filename = 'ws_mean_'+event+'.png' 
plot_name = os.path.join(dir_work,'figs_vs_init',filename)
plt.savefig(plot_name) 



##################################
# 
fig_num = 202 
fig = plt.figure(num=fig_num,figsize=(10,5)) 
plt.clf()

plt.plot(dt_axis_init_utc, ws10_crit_model_init  [0,:], 'r', linestyle='-', label='ws hrrr',        linewidth=width_line, marker='o', markersize=size_marker, markeredgecolor='k') 
plt.plot(dt_axis_init_utc, wsgd10_crit_model_init[0,:], 'b', linestyle='-', label='wsg dist hrrr',  linewidth=width_line, marker='o', markersize=size_marker, markeredgecolor='k') 
#plt.plot(dt_axis_init_utc, wsgt10_crit_model_init[0,:], 'g', linestyle='-', label='wsg trans hrrr', linewidth=width_line, marker='o', markersize=size_marker, markeredgecolor='k') 
#plt.plot(dt_axis_init_utc, ws10_crit_model_init  [1,:], 'c', linestyle='-', label='ws nam',         linewidth=width_line, marker='o', markersize=size_marker, markeredgecolor='k') 
#plt.plot(dt_axis_init_utc, wsgd10_crit_model_init[1,:], 'm', linestyle='-', label='wsg dist nam',   linewidth=width_line, marker='o', markersize=size_marker, markeredgecolor='k') 
#plt.plot(dt_axis_init_utc, wsgt10_crit_model_init[1,:], 'k', linestyle='-', label='wsg trans nam',  linewidth=width_line, marker='o', markersize=size_marker, markeredgecolor='k') 

for dum in numpy.arange(wsg_min, wsg_max+wsg_int, wsg_int):
    plt.plot([dt_min_plot_utc-td(hours=24), dt_max_plot_utc+td(hours=24)], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
for dum in matplotlib.dates.drange(dt_min_plot_utc, dt_max_plot_utc+4*delta_lines, delta_lines):
    plt.plot([dum, dum], [wsg_min, wsg_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 

plt.legend(loc=2,fontsize=12,ncol=1) 
plt.title('%s percent cells exceedance ' % (event), \
     fontsize=14, loc='left')                     
plt.xlabel('model initialization [UTC]',fontsize=14,labelpad=0)            
plt.ylabel('% exceedance',fontsize=14,labelpad=0)            
plt.yticks(numpy.arange(wsg_min, wsg_max+wsg_int, wsg_int))                     
plt.ylim([wsg_min, wsg_max])
plt.xlim([date_ticks[0], date_ticks[-1]])
plt.gca().xaxis.set_major_formatter(DateFormatter(datetick_format))
plt.xticks(date_ticks,visible=True) 
plt.show() 
filename = 'n_crit_'+event+'.png' 
plot_name = os.path.join(dir_work,'figs_vs_init',filename)
plt.savefig(plot_name) 

# plots 
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
