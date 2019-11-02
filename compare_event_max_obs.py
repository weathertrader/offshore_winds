
###############################################################################
# compare_event_max_obs.py 
# author: Craig Smith 
# purpose: compare ws max obs between two events 
# revision history:  
#   10/27/2019 - original 
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

import matplotlib
#if (manual_mode): 
#    matplotlib.use('Agg') 
#    matplotlib.use('TkAgg') # MUST BE CALLED BEFORE IMPORTING plt
import matplotlib.pyplot as plt
from matplotlib.dates import drange, DateFormatter
from matplotlib.ticker import MultipleLocator 

import matplotlib.ticker as mticker

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
from read_stn_metadata_from_csv import read_stn_metadata_from_csv
from read_mesowest_api_csv_data import read_mesowest_api_csv_data

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
process_name = 'compare_event_max_ws_obs'
log_file_name = 'log_'+process_name+'_'+project_name+'_'+dt_cron_start_lt.strftime('%Y-%m-%d_%H-%M')+'.txt' 
log_name_full_file_path = os.path.join(dir_work, 'archive_logs', log_file_name) 
logger = instantiate_logger(log_name_full_file_path, dt_cron_start_lt) 
print      ('instantiate_logger end' ) 

# instantiate logger 
###############################################################################


###############################################################################
# plot control  

size_scatter = 20           
size_font_scatter = 12
 
ws_units  = 'mph' # 'mph', or 'ms'
temp_units = 'C' # 'C', 'F', 'K' 

if   (ws_units == 'ms'): 
    ws_units_label = 'ms$^{-1}$'
    [wsg_min, wsg_max, wsg_int] = [0, 50, 10] # was 0, 50, 10                                                                
    [ ws_min,  ws_max,  ws_int] = [0, 25, 5] # was 0, 30, 5                                                                
    [ws_min_cont, ws_max_cont, ws_int_cont] = [0, 50, 4]
elif (ws_units == 'mph'): 
    ws_units_label = 'mph'
    #[ ws_min,  ws_max,  ws_int] = [15.0,   80.0,  5.0]
    #[wsg_min, wsg_max, wsg_int] = [35.0,  110.0,  5.0]
    #[ ws_min,  ws_max,  ws_int] = [0.0,   80.0,  5.0]
    #[wsg_min, wsg_max, wsg_int] = [0.0,  110.0,  5.0]
    [ ws_min,  ws_max,  ws_int] = [0.0,  65.0,  5.0]
    [wsg_min, wsg_max, wsg_int] = [0.0,  85.0,  5.0]

ws_ticks = numpy.arange(ws_min,ws_max+ws_int,ws_int)
wsg_ticks = numpy.arange(wsg_min,wsg_max+wsg_int,wsg_int)

[gf_min, gf_max, gf_int] = [0.0, 4.5, 0.5]

if   (temp_units == 'F'): 
    temp_units_label = '$^{o}$F'
    #[temp_min, temp_max, temp_int] = [30,110,10] 
    [temp_min, temp_max, temp_int] = [40,90,10] 
else: 
    temp_units_label = '$^{o}$C'
    [temp_min, temp_max, temp_int] = [0, 35, 10] # -10, 35, 10 
    [temp_min_cont, temp_max_cont, temp_int_cont] = [-5, 50, 5.0]
temp_ticks = numpy.arange(temp_min,temp_max+temp_int,temp_int)

colors_s = ['k', 'r', 'b', 'g', 'c', 'm', 'y',
            'k', 'r', 'b', 'g', 'c', 'm', 'y']

style_line = [ '-', '-', '-', '-', '-', '-', '-',
              '--','--','--','--','--','--','--',]

rh_units_label = '%'
#[rh_min, rh_max, rh_int] = [0.0, 100.5, 20.0]
[rh_min, rh_max, rh_int] = [0.0, 45.0, 5.0]
rh_ticks = numpy.arange(rh_min, rh_max+rh_int, rh_int)

wd_units_label = '$^{o}$'
[wd_min, wd_max, wd_int] = [0.0, 360.0, 45.0]
wd_ticks = numpy.arange(wd_min, wd_max+wd_int, wd_int)

# plot control  
###############################################################################

 
###############################################################################
# flags 

print_stn_info = True
use_stn = 'all' 

# flags 
###############################################################################


###############################################################################
# read stn_info 

print      ('read stn_info start ' )
logger.info('read stn_info start ' ) 
(dict_stn_metadata) = read_stn_metadata_from_csv(dir_work, project_name, use_stn, print_stn_info)

# read stn_info 
###############################################################################


###############################################################################
# define events to use 

n_events = 2
# done
#event_list = ['2017_10_08_event', '2019_10_27_event']
#event_list = ['2019_10_09_event', '2019_10_23_event']
event_list = ['2018_10_14_event', '2018_11_08_event']
#event = '2019_06_08_event'
#event = '2019_09_24_event'
#event = '2019_10_05_event'

# define events to use 
###############################################################################


#event_list = ['2017_10_08_event', '2018_10_14_event', '2018_11_08_event', '2019_10_09_event', '2019_10_23_event',  '2019_10_27_event']


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

# initialize obs arrays 
ws_max_obs_event_s  = numpy.full([n_events, dict_stn_metadata['n_stn']], numpy.nan, dtype='float') 
wsg_max_obs_event_s = numpy.full([n_events, dict_stn_metadata['n_stn']], numpy.nan, dtype='float') 
rh_min_obs_event_s  = numpy.full([n_events, dict_stn_metadata['n_stn']], numpy.nan, dtype='float') 
for ev in range(0, n_events, 1):
    event = event_list[ev]
    #for s in range(45, 46, 1): 
    for s in range(0, dict_stn_metadata['n_stn'], 1): 
        #if ('PG328' in dict_stn_metadata['stn_id'][s]):
        print      ('  processing s %s, s = %s of %s ' % (dict_stn_metadata['stn_id'][s], s, dict_stn_metadata['n_stn']))  
        logger.info('  processing s %s, s = %s of %s ' % (dict_stn_metadata['stn_id'][s], s, dict_stn_metadata['n_stn']))  
        #print(s)
        file_name_full_path = os.path.join(dir_data_sfc_obs, event, 'stn_obs_'+dict_stn_metadata['stn_id'][s]+'.csv')    
        if not os.path.isfile(file_name_full_path):
            print      ('  ERROR - missing file ') 
            logger.info('  ERROR - missing file ') 
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
            ws_max_obs_event_s [ev,s] = numpy.nanmax( ws_read)
            wsg_max_obs_event_s[ev,s] = numpy.nanmax(wsg_read)
            rh_min_obs_event_s [ev,s] = numpy.nanmin( rh_read)
            #stn_read_df.index()
            dt_read_utc = stn_read_df.index
            dt_read_pst = dt_read_utc - td(hours=8)
    
            del ws_read, wsg_read, rh_read, wd_read, stn_read_df, dt_read_pst, dt_read_utc
    
# 
###############################################################################


mask = ((ws_max_obs_event_s[0,:] == 0.0) | (ws_max_obs_event_s[1,:] == 0.0))
ws_max_obs_event_s[:,mask] = numpy.nan
mask = ((wsg_max_obs_event_s[0,:] == 0.0) | (wsg_max_obs_event_s[1,:] == 0.0))
wsg_max_obs_event_s[:,mask] = numpy.nan


###############################################################################
# scatter_event1_vs_event2

# nor bay
[lon_min, lon_max, lon_int] = [-123.6, -121.9, 0.4]
[lat_min, lat_max, lat_int] = [  37.8,   39.6, 0.2]
mask_nor_bay = ((dict_stn_metadata['stn_lon'] > lon_min) & (dict_stn_metadata['stn_lon'] < lon_max) & (dict_stn_metadata['stn_lat'] > lat_min) & (dict_stn_metadata['stn_lat'] < lat_max))


[figsize_x, figsize_y] = [8, 8]

fig = plt.figure(num=301,figsize=(figsize_x, figsize_y)) # 10x5, 10x6, 10x10 
plt.clf()
plt.scatter(ws_max_obs_event_s [0,:], ws_max_obs_event_s [1,:], s=40,marker='o',color='r', edgecolor='k',alpha=0.5)
for dum in numpy.arange(ws_min, ws_max+ws_int, ws_int):
    plt.plot([ws_min, ws_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    plt.plot([dum, dum], [ws_min, ws_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
plt.plot([ws_min, ws_max], [ws_min, ws_max], 'k', linestyle='-', linewidth=2.0, marker='o', markersize=0) 

plt.xticks(ws_ticks, fontsize=14)
plt.yticks(ws_ticks, fontsize=14)
plt.xlim([ws_min, ws_max])
plt.ylim([ws_min, ws_max])
plt.xlabel(event_list[0], fontsize=14, labelpad=0) # 10 is too small, 20 
plt.ylabel(event_list[1], fontsize=14, labelpad=0) # 10 is too small, 20 
plt.title('event maximum observed wind speed [mph] \n%s vs %s ' % (event_list[0], event_list[1]) , \
    fontsize=16, loc='left', weight = 'bold')   
plt.show()
plt.tight_layout()        
filename = 'compare_ws_max_%s_vs_%s.png' % (event_list[0], event_list[1])
plot_name = os.path.join(dir_work, 'figs_event_compare', filename) 
dpi_level = 400 # 400        
#plt.savefig(plot_name)
plt.savefig(plot_name, dpi=dpi_level) 
#fig.clf()
#plt.close()        


fig = plt.figure(num=302,figsize=(figsize_x, figsize_y)) # 10x5, 10x6, 10x10 
plt.clf()
plt.scatter(wsg_max_obs_event_s [0,:], wsg_max_obs_event_s [1,:], s=40,marker='o',color='r', edgecolor='k',alpha=0.5)
for dum in numpy.arange(wsg_min, wsg_max+wsg_int, wsg_int):
    plt.plot([wsg_min, wsg_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    plt.plot([dum, dum], [wsg_min, wsg_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
plt.plot([wsg_min, wsg_max], [wsg_min, wsg_max], 'k', linestyle='-', linewidth=2.0, marker='o', markersize=0) 

plt.xticks(wsg_ticks, fontsize=14)
plt.yticks(wsg_ticks, fontsize=14)
plt.xlim([wsg_min, wsg_max])
plt.ylim([wsg_min, wsg_max])
plt.xlabel(event_list[0], fontsize=14, labelpad=0) # 10 is too small, 20 
plt.ylabel(event_list[1], fontsize=14, labelpad=0) # 10 is too small, 20 
plt.title('event maximum observed wind gust [mph] \n%s vs %s ' % (event_list[0], event_list[1]) , \
    fontsize=16, loc='left', weight = 'bold')   
plt.show()
plt.tight_layout()        
filename = 'compare_wsg_max_%s_vs_%s.png' % (event_list[0], event_list[1])
plot_name = os.path.join(dir_work, 'figs_event_compare', filename) 
dpi_level = 400 # 400        
#plt.savefig(plot_name)
plt.savefig(plot_name, dpi=dpi_level) 
#fig.clf()
#plt.close()        


fig = plt.figure(num=303,figsize=(figsize_x, figsize_y)) # 10x5, 10x6, 10x10 
plt.clf()
plt.scatter(rh_min_obs_event_s [0,:], rh_min_obs_event_s [1,:], s=40,marker='o',color='r', edgecolor='k',alpha=0.5)
for dum in numpy.arange(rh_min, rh_max+rh_int, rh_int):
    plt.plot([rh_min, rh_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    plt.plot([dum, dum], [rh_min, rh_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
plt.plot([rh_min, rh_max], [rh_min, rh_max], 'k', linestyle='-', linewidth=2.0, marker='o', markersize=0) 

plt.ylim([rh_min, rh_max])
plt.xlim([rh_min, rh_max])
plt.xlabel(event_list[0], fontsize=12, labelpad=10) # 10 is too small, 20 
plt.ylabel(event_list[1], fontsize=12, labelpad=10) # 10 is too small, 20 
plt.title('event minimum observed relative humidity \n%s vs %s ' % (event_list[0], event_list[1]) , \
    fontsize=16, loc='left', weight = 'bold')   
plt.show()
plt.tight_layout()        
filename = 'compare_rh_max_%s_vs_%s.png' % (event_list[0], event_list[1])
plot_name = os.path.join(dir_work, 'figs_event_compare', filename) 
dpi_level = 400 # 400        
#plt.savefig(plot_name)
plt.savefig(plot_name, dpi=dpi_level) 
#fig.clf()
#plt.close()        

# plot_ws_vs_stn_ele
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
