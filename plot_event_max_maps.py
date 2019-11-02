
###############################################################################
# plot_max_ws_maps.py 
# author: Craig Smith 
# purpose: plot event max observed and forecast ws and wsg from hrrr and nam 
# revision history:  
#   10/05/2019 - original 
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
process_name = 'plot_max_ws_maps'
log_file_name = 'log_'+process_name+'_'+project_name+'_'+dt_cron_start_lt.strftime('%Y-%m-%d_%H-%M')+'.txt' 
log_name_full_file_path = os.path.join(dir_work, 'archive_logs', log_file_name) 
logger = instantiate_logger(log_name_full_file_path, dt_cron_start_lt) 
print      ('instantiate_logger end' ) 

# instantiate logger 
###############################################################################

# 2019 fires by PGE
# 2019/05/29 Spearhead fire in Fresno County
# 2019/05/30 Belridge Fire in Kern County
# 2019/09/16 Grove Fire in Maripose county
# 2019/09/28 Butte County Highway Fire

# forecast horizon
# hrrr is 36 hr 
# nam  is 84 hr 

# availability on nomads
# hrrr 1 day, today and yesterday only
# nam previous 7 days

# use PG132 to define event in North Bay
# use PG328 concow road 

###############################################################################
# parse command line options 

if (manual_mode): 
    
    ########################################
    # 2017/10/08 - obs only, no model data 
    #event = '2017_10_08_event'
    #dt_min_plot_utc_str = '2017-10-08_08'
    #dt_max_plot_utc_str = '2017-10-11_08'


    ########################################
    # 2018/10/14 - obs done, model init done, data clean up not done, plots not done 
    # model data avail, hrrr only, 2018_10_13_12, 2018_10_14_00
    #event = '2018_10_14_event'
    # PSPS time was  2018/10/14 20 - 2018/10/16 15, or 2018/10/17 06 PST 
    # plotting   2018-10-13_00 - 2018-10-16_08 PST
    # peak event 2018/10/14 12 - 2018/10/15 12 PST 
    #dt_min_plot_utc_str = '2018-10-13_08'
    #dt_max_plot_utc_str = '2018-10-16_16'
    #model_name = 'nam'
    # earliest possible, ends 2018-10-15_04 PST
    #dt_init_utc_str     = '2018-10-12_00'
    #dt_init_utc_str     = '2018-10-12_12'
    #dt_init_utc_str     = '2018-10-13_00'
    #dt_init_utc_str     = '2018-10-13_12'
    #dt_init_utc_str     = '2018-10-14_00'
    #dt_init_utc_str     = '2018-10-15_12'
    # latest possible,   starts  2018-10-14_16 PST
    #dt_init_utc_str     = '2018-10-15_00'
    #model_name = 'hrrr' 
    # probably too early, but will do anyways 
    #dt_init_utc_str     = '2018-10-13_12'
    # done
    #dt_init_utc_str     = '2018-10-14_00'
    # earliest possible, ends 2018-10-15_10 PST
    #dt_init_utc_str     = '2018-10-14_06'
    #dt_init_utc_str     = '2018-10-14_12'
    #dt_init_utc_str     = '2018-10-14_18'
    #dt_init_utc_str     = '2018-10-15_00'
    # latest possible,   starts  2018-10-14_16 PST
    #dt_init_utc_str     = '2018-10-15_00'

    ########################################
    # 2018/11/08 - obs done, model init done, data clean up not done, plots not done 
    # model data avail, hrrr only, 2018_11_07_12, 2018_11_08_00
    #event = '2018_11_08_event'
    # PSPS was not 2018/11/08 R 
    #plotting  2018-11-06_00 to 2018-11-10_08 PST
    #event max 2018-11-08_00 to 2018-11-09_00 PST
    #dt_min_plot_utc_str = '2018-11-06_08'
    #dt_max_plot_utc_str = '2018-11-10_16'
    #model_name = 'nam'
    # earliest possible, ends 2018-11-08_16 PST
    #dt_init_utc_str     = '2018-11-05_12'
    #dt_init_utc_str     = '2018-11-06_00'
    #dt_init_utc_str     = '2018-11-06_12'
    #dt_init_utc_str     = '2018-11-07_00'
    #dt_init_utc_str     = '2018-11-07_12'
    # latest possible,   starts 2018-11-07_14 PST 
    #dt_init_utc_str     = '2018-11-08_00'
    #model_name = 'hrrr' 
    # earliest possible, ends 2018-11-08_12 PST
    #dt_init_utc_str     = '2018-11-07_06'
    # done
    #dt_init_utc_str     = '2018-11-07_12'
    #dt_init_utc_str     = '2018-11-07_18'
    # done 
    #dt_init_utc_str     = '2018-11-08_00'
    # latest possible,   starts 2018-11-07_22 PST 
    #dt_init_utc_str     = '2018-11-08_06'
    
    ########################################
    # 2019/06/08 S - obs done, model init done, data clean up not done, plots not done 
    # no model data avail at all
    # note csmith - this event is wonky in that PSPS window was a full day too late 
    #event = '2019_06_08_event'
    #dt_min_plot_utc_str = '2019-06-07_08'
    #dt_max_plot_utc_str = '2019-06-10_08'
    # PSPS was 2019/06/09 6 am or 20 to 2019/06/09 12-15
    # plotting 2019-06-07_00 - 2019-06-10_00 PST
    # event max 06/08 00 to 06/08 18 
    #model_name = 'nam'
    # earliest possible, ends 2019-06-08_16 PST
    #dt_init_utc_str     = '2019-06-05_12'
    #dt_init_utc_str     = '2019-06-06_00'
    #dt_init_utc_str     = '2019-06-06_12'
    #dt_init_utc_str     = '2019-06-07_00'
    #dt_init_utc_str     = '2019-06-07_12'
    # latest possible,   starts  2019-06-07_16 PST
    #dt_init_utc_str     = '2019-06-08_00'
    #model_name = 'hrrr' 
    # earliest possible, ends 2019-06-08_16 PST
    #dt_init_utc_str     = '2019-06-07_12'
    #dt_init_utc_str     = '2019-06-07_18'
    #dt_init_utc_str     = '2019-06-08_00'
    # latest possible,   starts  2019-06-08_00 PST
    #dt_init_utc_str     = '2019-06-08_06'
    
    ########################################
    # 2019/09/24 - obs done, model init done, data clean not done, data transfer not done plots not done 
    # model data avail nam 2019-09-21_00 to 2019-09-26_00, hrrr 2019-09-24_00 to 2019-09-25_12 
    #event = '2019_09_24_event'
    #dt_min_plot_utc_str = '2019-09-23_08'
    #dt_max_plot_utc_str = '2019-09-27_08'
    # psps was ???
    # plotting 2019-09-23_00 - 2019-09-27_00 PST
    # event max 2019-09-25_00 PST 
    #model_name = 'nam'
    # earliest possible, ends 2019-09-25_16
    #dt_init_utc_str     = '2019-09-22_12'
    #dt_init_utc_str     = '2019-09-23_00'
    #dt_init_utc_str     = '2019-09-23_12'
    #dt_init_utc_str     = '2019-09-24_00'
    #dt_init_utc_str     = '2019-09-24_12'
    # latest possible,   starts 2019-09-24_16
    #dt_init_utc_str     = '2019-09-25_00'
    #model_name = 'hrrr' 
    # earliest possible, ends 2019-09-25_10 PST
    # done 
    #dt_init_utc_str     = '2019-09-24_06'
    # doing now 
    #dt_init_utc_str     = '2019-09-24_12'
    #dt_init_utc_str     = '2019-09-24_18'
    #dt_init_utc_str     = '2019-09-25_00'
    # latest possible,   starts  2019-09-24_22
    #dt_init_utc_str     = '2019-09-25_06'
 
    ########################################
    # 2019/10/06 - obs done, model init done, data clean up not done, plots not done 
    # model data avail hrrrr,  2019-10-05_00 to 2019-10-06_12    
    #event = '2019_10_05_event'
    #dt_min_plot_utc_str = '2019-10-04_08'
    #dt_max_plot_utc_str = '2019-10-07_08'
    # psps     2019-10-05_20 to 2019-10-06_06 PST
    # plotting 2019-10-04_00 to 2019-10-07_00 PST
    
    #model_name = 'nam'
    # earliest possible, ends 2019-10-06_04 PST
    #dt_init_utc_str     = '2019-10-03_00'
    #dt_init_utc_str     = '2019-10-03_12'
    #dt_init_utc_str     = '2019-10-04_00'
    #dt_init_utc_str     = '2019-10-04_12'
    # latest possible, starts 2019-10-04_16
    #dt_init_utc_str     = '2019-10-05_00'
    #model_name = 'hrrr' 
    # earliest possible, ends 2019-10-06_10 PST
    #dt_init_utc_str     = '2019-10-05_06'
    # done
    #dt_init_utc_str     = '2019-10-05_12'
    # done 
    #dt_init_utc_str     = '2019-10-05_18'
    #dt_init_utc_str     = '2019-10-06_00'
    # latest possible, starts 2019-10-05_22 PST 
    #dt_init_utc_str     = '2019-10-06_06'
       
    ########################################
    # 2019/10/09-10 - obs done, model init done, data clean up done, plots done 
    #event = '2019_10_09_event'
    # W 10/09 6 am PST - R 10/10 6 pm PST 
    # last forecast to grab is 10/11 12Z 
    # most important forecast is Tues 6 PM or W 10/09 00Z
    #dt_min_plot_utc_str = '2019-10-09_08'
    #dt_max_plot_utc_str = '2019-10-11_08'
    # plotting 2019-10-09_00 - 2019-10-11_00 PST 
    #model_name = 'nam'
    # earliest possible, ends 2019-10-10_16 PST
    # dt_init_utc_str     = '2019-10-07_12'
    # dt_init_utc_str     = '2019-10-08_00'
    # dt_init_utc_str     = '2019-10-08_12'
    # dt_init_utc_str     = '2019-10-09_00'
    # best / retain on local
    # dt_init_utc_str     = '2019-10-09_12'
    # latest_posibble ends 2019-10-13_04 PST
    # dt_init_utc_str     = '2019-10-10_00'
    #model_name = 'hrrr'
    # earliest possible, ends 2019-10-10_10 PST 
    # dt_init_utc_str     = '2019-10-09_06'
    # best / retain on local 
    #dt_init_utc_str     = '2019-10-09_12'
    # dt_init_utc_str     = '2019-10-09_18'
    # latest possible starts 2019-10-09_16
    # dt_init_utc_str     = '2019-10-10_00'


    ########################################
    # 2019/10/23-23 - obs not done, model init not done, data clean up not done, plots not done 
    #event = '2019_10_23_event'
    # W 10/23 6 am PST - R 10/24 6 pm PST 
    #dt_min_plot_utc_str = '2019-10-23_08'
    #dt_max_plot_utc_str = '2019-10-25_08'
    # plotting 2019-10-09_00 - 2019-10-11_00 PST 
    #model_name = 'nam'
    # earliest possible, ends 
    # best / retain on local
    # dt_init_utc_str     = '2019-10-09_00'
    # latest_posibble ends
    #model_name = 'hrrr'
    # earliest possible, ends 
    # best / retain on local
    #dt_init_utc_str     = '2019-10-23_12'
    # latest_posibble ends

    ########################################
    # blank template 
    # 2019/10/27 U - obs not done, model init not done, data clean up not done, plots not done 
    event = '2019_10_27_event'
    # U 10/27 1 am PST - U 10/27 23:59 pm PST 

    dt_min_plot_utc_str = '2019-10-26_08'
    dt_max_plot_utc_str = '2019-10-29_08'
    # plotting 2019-10-09_00 - 2019-10-11_00 PST 
    #model_name = 'nam'
    # earliest possible, ends 
    # best / retain on local
    #dt_init_utc_str     = '2019-10-26_00'
    # latest_posibble ends
    model_name = 'hrrr'
    # earliest possible, ends 2019/10/27 16 PST
    # best / retain on local
    #dt_init_utc_str     = '2019-10-26_12'
    # best / retain on local
    dt_init_utc_str     = '2019-10-27_00'
    # lasest possible start 2019/10/27 04 PST 
    #dt_init_utc_str     = '2019-10-27_12'
    # latest_posibble ends
   
else:        
    parser = argparse.ArgumentParser(description='model to use')
    parser.add_argument('--model_name', type=str, help='model_name', required=True)    
    parser.add_argument('--dt_init_utc_str', type=str, help='dt_init_utc_str', required=True)    
    parser.add_argument('--dt_min_plot_utc_str', type=str, help='dt_min_plot_utc_str', required=True)    
    parser.add_argument('--dt_max_plot_utc_str', type=str, help='dt_max_plot_utc_str', required=True)
    args = parser.parse_args()
    model_name = args.model_name
    dt_init_utc_str     = args.dt_init_utc_str
    dt_min_plot_utc_str = args.dt_min_plot_utc_str
    dt_max_plot_utc_str = args.dt_max_plot_utc_str

print      ('using model_name %s ' %(model_name))
     
# parse command line options 
###############################################################################


###############################################################################
# set model data ingest and archive directories 

dir_data_model_ingest  = os.path.join(dir_data_model, model_name, 'ingest')
dir_data_model_archive = os.path.join(dir_data_model, model_name, 'archive')
print      ('dir_data_model_ingest  is %s ' % (dir_data_model_ingest))
logger.info('dir_data_model_ingest  is %s ' % (dir_data_model_ingest))
print      ('dir_data_model_archive is %s ' % (dir_data_model_archive))
logger.info('dir_data_model_archive is %s ' % (dir_data_model_archive))

dir_data_model_raw_ingest       = os.path.join(dir_data_model_ingest,  'raw')
dir_data_model_raw_archive      = os.path.join(dir_data_model_archive, 'raw')
dir_data_model_grid_csv_ingest  = os.path.join(dir_data_model_ingest,  'grid_csv')
dir_data_model_grid_csv_archive = os.path.join(dir_data_model_archive, 'grid_csv')
dir_data_model_stn_csv_ingest   = os.path.join(dir_data_model_ingest,  'stn_csv')
dir_data_model_stn_csv_archive  = os.path.join(dir_data_model_archive, 'stn_csv')

# set model data ingest and archive directories 
###############################################################################


###############################################################################
# parse dates to read 

dt_init_utc = dt.strptime(dt_init_utc_str,'%Y-%m-%d_%H')
dt_min_plot_utc = dt.strptime(dt_min_plot_utc_str,'%Y-%m-%d_%H')
dt_max_plot_utc = dt.strptime(dt_max_plot_utc_str,'%Y-%m-%d_%H')
dt_min_plot_pst = dt_min_plot_utc - td(hours=utc_conversion)
dt_max_plot_pst = dt_max_plot_utc - td(hours=utc_conversion)
print      ('plotting %s - %s UTC ' %(dt_min_plot_utc.strftime('%Y-%m-%d_%H'), dt_max_plot_utc.strftime('%Y-%m-%d_%H')))
logger.info('plotting %s - %s UTC ' %(dt_min_plot_utc.strftime('%Y-%m-%d_%H'), dt_max_plot_utc.strftime('%Y-%m-%d_%H')))
print      ('plotting %s - %s PST ' %(dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H')))
logger.info('plotting %s - %s PST ' %(dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H')))
print      ('processing forecast init %s UTC %s ' %(dt_init_utc.strftime('%Y-%m-%d_%H'), model_name))
logger.info('processing forecast init %s UTC %s ' %(dt_init_utc.strftime('%Y-%m-%d_%H'), model_name))
if   (model_name == 'hrrr'):
    model_forecast_horizon = 36 
elif (model_name == 'nam'):
    model_forecast_horizon = 84

dt_model_initial_pst = dt_init_utc - td(hours=utc_conversion)
dt_model_final_pst   = dt_model_initial_pst + td(hours=model_forecast_horizon)

print      ('model data avail %s - %s PST ' %(dt_model_initial_pst.strftime('%Y-%m-%d_%H'), dt_model_final_pst.strftime('%Y-%m-%d_%H')))
logger.info('model data avail %s - %s PST ' %(dt_model_initial_pst.strftime('%Y-%m-%d_%H'), dt_model_final_pst.strftime('%Y-%m-%d_%H')))

n_hrs = (dt_max_plot_utc - dt_min_plot_utc).days*24
#n_hrs = (dt_max_plot_utc - dt_min_plot_utc).days*24 + (dt_max_plot_utc - dt_min_plot_utc).seconds/3600

# parse dates to read 
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
    [ ws_min,  ws_max,  ws_int] = [0.0,  50.0,  5.0]
    [wsg_min, wsg_max, wsg_int] = [0.0,  81.0,  10.0]
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
[rh_min, rh_max, rh_int] = [0.0, 100.5, 20.0]
rh_ticks = numpy.arange(rh_min, rh_max+rh_int, rh_int)

wd_units_label = '$^{o}$'
[wd_min, wd_max, wd_int] = [0.0, 360.0, 45.0]
wd_ticks = numpy.arange(wd_min, wd_max+wd_int, wd_int)

# plot control  
###############################################################################

 
###############################################################################
# flags 

plot_time_series = True
plot_maps = True 
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
# initialize obs arrays 

ws_max_obs_s  = numpy.full([dict_stn_metadata['n_stn']], numpy.nan, dtype='float') 
wsg_max_obs_s = numpy.full([dict_stn_metadata['n_stn']], numpy.nan, dtype='float') 
rh_min_obs_s  = numpy.full([dict_stn_metadata['n_stn']], numpy.nan, dtype='float') 

# initialize obs arrays 
###############################################################################


n_days_temp = (dt_max_plot_pst - dt_min_plot_pst).days

delta       = td(hours=24)
delta_lines = td(hours=12)
datetick_format = '%m/%d %H'    
#datetick_format = '%H'    
date_ticks = drange(dt_min_plot_pst, dt_max_plot_pst+delta, delta)
n_date_ticks = len(date_ticks) 

########################################
# nightime shading 
# make 00z LST darker than the rest 
yy_temp = dt.strftime(dt_min_plot_pst-td(days=1),'%Y')
mo_temp = dt.strftime(dt_min_plot_pst-td(days=1),'%m')
dd_temp = dt.strftime(dt_min_plot_pst-td(days=1),'%d')
dt_min_00_lt = dt(int(yy_temp), int(mo_temp), int(dd_temp), 00, 00)          
# shading nighttime 
yy_temp = dt.strftime(dt_min_plot_pst-td(days=1),'%Y')
mo_temp = dt.strftime(dt_min_plot_pst-td(days=1),'%m')
dd_temp = dt.strftime(dt_min_plot_pst-td(days=1),'%d')
dt_min_19_lt = dt(int(yy_temp), int(mo_temp), int(dd_temp), 18, 00)
alpha_night = 0.5
            
var_list = ['ws', 'wsg', 'rh']
n_vars = len(var_list)

rh_units = '%'

 
#plot_vs_time = True
plot_vs_time = False


[ws_crit, wsg_crit, wsg_crit_t_line] = [25.0, 45.0, 55.0]


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
        ws_max_obs_s [s] = numpy.nanmax( ws_read)
        wsg_max_obs_s[s] = numpy.nanmax(wsg_read)
        rh_min_obs_s [s] = numpy.nanmin( rh_read)
        #stn_read_df.index()
        dt_read_utc = stn_read_df.index
        dt_read_pst = dt_read_utc - td(hours=8)

        if (plot_vs_time):
 
            ##################################
            # ws / wsg, wd, rh 
            fig_num = 131 
            fig = plt.figure(num=fig_num,figsize=(10,8)) 
            plt.clf()
            
            plt.subplot(3, 1, 1)
            width_line = 2.0             
            size_marker = 0
            plt.plot(dt_read_pst, ws_read,  'r', linestyle='-', label='ws obs',  linewidth=width_line, marker='o', markersize=size_marker, markeredgecolor='k') 
            plt.plot(dt_read_pst, wsg_read, 'b', linestyle='-', label='wsg obs', linewidth=width_line, marker='o', markersize=size_marker, markeredgecolor='k') 
            plt.plot([dt_min_plot_pst-td(hours=24), dt_max_plot_pst+td(hours=24)], [ ws_crit,  ws_crit], 'r', label='ws criteria',  linestyle='--', linewidth=1, marker='o', markersize=0) 
            plt.plot([dt_min_plot_pst-td(hours=24), dt_max_plot_pst+td(hours=24)], [wsg_crit, wsg_crit], 'b', label='wsg criteria', linestyle='--', linewidth=1, marker='o', markersize=0) 

            for dum in numpy.arange(wsg_min, wsg_max+wsg_int, wsg_int):
                plt.plot([dt_min_plot_pst-td(hours=24), dt_max_plot_pst+td(hours=24)], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
            for dum in matplotlib.dates.drange(dt_min_plot_pst, dt_max_plot_pst+4*delta_lines, delta_lines):
                plt.plot([dum, dum], [wsg_min, wsg_min], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
            for dum in numpy.arange(0, n_days_temp+3, 1):
                plt.plot([dt_min_00_lt+dum*td(hours=24), dt_min_00_lt+dum*td(hours=24)], [-50, 150], 'gray', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
            # add shading for nighttime
            for dum in numpy.arange(0, n_days_temp+3, 1):
                plt.axvspan(dt_min_19_lt+dum*td(hours=24), dt_min_19_lt+dum*td(hours=24)+td(hours=12), color='grey', alpha=alpha_night, linewidth=0)                
            plt.legend(loc=2,fontsize=8,ncol=1) 
            plt.title('%s, %s\n%s - %s' % (dict_stn_metadata['stn_name'][s], dict_stn_metadata['stn_id'][s], dt_min_plot_pst.strftime('%Y-%m-%d'), dt_max_plot_pst.strftime('%Y-%m-%d')), \
                 fontsize=12, loc='left')                     
            #plt.title('ws, wsg, wd, temp vs time \n%s - %s\n%s, %s' % (dt_min_plot_pst.strftime('%Y-%m-%d'), dt_max_plot_pst.strftime('%Y-%m-%d'), dict_stn_metadata['stn_name'][s], dict_stn_metadata['stn_id'][s]), \
            #     fontsize=12, loc='left')                     
            plt.ylabel('ws [mph]',fontsize=12,labelpad=0)            
            plt.yticks(numpy.arange(wsg_min, wsg_max+wsg_int, wsg_int))                     
            plt.ylim([wsg_min, wsg_max])
            plt.xlim([date_ticks[0], date_ticks[-1]])
            plt.gca().xaxis.set_major_formatter(DateFormatter(datetick_format))
            plt.xticks(date_ticks,visible=True) 

            plt.subplot(3, 1, 2)
            width_line = 2.0             
            size_marker = 4
            plt.plot(dt_read_pst, wd_read, 'r', linestyle='-', label='wd',  linewidth=0, marker='o', markersize=size_marker, markeredgecolor='k') 
            for dum in numpy.arange(wd_min, wd_max+wd_int, wd_int):
                plt.plot([dt_min_plot_pst-td(hours=24), dt_max_plot_pst+td(hours=24)], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
            for dum in matplotlib.dates.drange(dt_min_plot_pst, dt_max_plot_pst+4*delta_lines, delta_lines):
                plt.plot([dum, dum], [wd_min, wd_min], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
            for dum in numpy.arange(0, n_days_temp+3, 1):
                plt.plot([dt_min_00_lt+dum*td(hours=24), dt_min_00_lt+dum*td(hours=24)], [wd_min, wd_max], 'gray', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
            # add shading for nighttime
            for dum in numpy.arange(0, n_days_temp+3, 1):
                plt.axvspan(dt_min_19_lt+dum*td(hours=24), dt_min_19_lt+dum*td(hours=24)+td(hours=12), color='grey', alpha=alpha_night, linewidth=0)                
            plt.ylabel('wd ['+wd_units_label+']',fontsize=12,labelpad=0)                      
            plt.yticks(numpy.arange(wd_min, wd_max+wd_int, wd_int))                     
            plt.ylim([wd_min, wd_max])
            plt.xlim([date_ticks[0], date_ticks[-1]])
            plt.gca().xaxis.set_major_formatter(DateFormatter(datetick_format))
            plt.xticks(date_ticks,visible=True) 
 
            plt.subplot(3, 1, 3)
            width_line = 2.0             
            size_marker = 0
            plt.plot(dt_read_pst, rh_read, 'r', linestyle='-', label='rh', linewidth=width_line, marker='o', markersize=size_marker, markeredgecolor='k') 
            for dum in numpy.arange(rh_min, rh_max+rh_int, rh_int):
                plt.plot([dt_min_plot_pst-td(hours=24), dt_max_plot_pst+td(hours=24)], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
            for dum in matplotlib.dates.drange(dt_min_plot_pst, dt_max_plot_pst+4*delta_lines, delta_lines):
                plt.plot([dum, dum], [rh_min, rh_min], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
            for dum in numpy.arange(0, n_days_temp+3, 1):
                plt.plot([dt_min_00_lt+dum*td(hours=24), dt_min_00_lt+dum*td(hours=24)], [-50, 150], 'gray', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
            # add shading for nighttime
            for dum in numpy.arange(0, n_days_temp+3, 1):
                plt.axvspan(dt_min_19_lt+dum*td(hours=24), dt_min_19_lt+dum*td(hours=24)+td(hours=12), color='grey', alpha=alpha_night, linewidth=0)                
            plt.xlabel('date [PST]',fontsize=12,labelpad=00)
            plt.ylabel('rh [%]',fontsize=12,labelpad=0)                      
            plt.yticks(numpy.arange(rh_min, rh_max+rh_int, rh_int))                     
            plt.ylim([rh_min, rh_max])
            plt.xlim([date_ticks[0], date_ticks[-1]])
            plt.gca().xaxis.set_major_formatter(DateFormatter(datetick_format))
            plt.xticks(date_ticks,visible=True) 
 
            plt.show() 
            filename = 'var_vs_time_'+dict_stn_metadata['stn_id'][s]+'_'+event+'.png' 
            plot_name = os.path.join(dir_work,'figs_vs_time',filename)
            plt.savefig(plot_name) 
            
        del ws_read, wsg_read, rh_read, wd_read, stn_read_df, dt_read_pst, dt_read_utc

# 
###############################################################################


###############################################################################
# plot_ws_vs_stn_ele

plot_ws_vs_stn_ele = True

if (plot_ws_vs_stn_ele):

    [hgt_min, hgt_max, hgt_int] = [0, 10000, 1000]
    # nor bay
    [lon_min, lon_max, lon_int] = [-123.6, -121.9, 0.4]
    [lat_min, lat_max, lat_int] = [  37.8,   39.6, 0.2]
    mask_nor_bay = ((dict_stn_metadata['stn_lon'] > lon_min) & (dict_stn_metadata['stn_lon'] < lon_max) & (dict_stn_metadata['stn_lat'] > lat_min) & (dict_stn_metadata['stn_lat'] < lat_max))

    
    [figsize_x, figsize_y] = [8, 8]
    fig = plt.figure(num=201,figsize=(figsize_x, figsize_y)) # 10x5, 10x6, 10x10 
    plt.clf()
    plt.scatter(dict_stn_metadata['stn_ele'], ws_max_obs_s, s=40,marker='o',color='r', edgecolor='k',alpha=0.5)
    plt.scatter(dict_stn_metadata['stn_ele'][mask_nor_bay], ws_max_obs_s[mask_nor_bay], s=40,marker='o',color='b', edgecolor='k',alpha=0.5)
    for dum in numpy.arange(ws_min, ws_max+ws_int, ws_int):
        plt.plot([hgt_min, hgt_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    for dum in numpy.arange(hgt_min, hgt_max+hgt_int, hgt_int):
        plt.plot([dum, dum], [ws_min, ws_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    plt.ylim([0, ws_max])
    plt.xlim([hgt_min, hgt_max])                                 
    plt.xlabel('stn elevation [ft]', fontsize=12, labelpad=10) # 10 is too small, 20 
    plt.ylabel('ws [mph]',  fontsize=12, labelpad=10) # 30 is too small, 60 
    plt.title('ws max observed vs stn elevation \n%s - %s PST  ' % (dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H')) , \
        fontsize=12, loc='left', weight = 'bold')   
    plt.show()
    plt.tight_layout()        
    filename = 'ws_max_vs_elevation_time_%s_%s.png' % (dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H'))
    plot_name = os.path.join(dir_work, 'figs_ws_max_obs_maps', filename) 
    dpi_level = 400 # 400        
    #plt.savefig(plot_name)
    plt.savefig(plot_name, dpi=dpi_level) 
    #fig.clf()
    #plt.close()        

    fig = plt.figure(num=202,figsize=(figsize_x, figsize_y)) # 10x5, 10x6, 10x10 
    plt.clf()
    plt.scatter(dict_stn_metadata['stn_ele'], wsg_max_obs_s, s=40,marker='o',color='r', edgecolor='k',alpha=0.5)
    plt.scatter(dict_stn_metadata['stn_ele'][mask_nor_bay], wsg_max_obs_s[mask_nor_bay], s=40,marker='o',color='b', edgecolor='k',alpha=0.5)
    for dum in numpy.arange(wsg_min, wsg_max+ws_int, wsg_int):
        plt.plot([hgt_min, hgt_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    for dum in numpy.arange(hgt_min, hgt_max+hgt_int, hgt_int):
        plt.plot([dum, dum], [wsg_min, wsg_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    plt.ylim([0, wsg_max])
    plt.xlim([hgt_min, hgt_max])                                 
    plt.xlabel('stn elevation [ft]', fontsize=12, labelpad=10) # 10 is too small, 20 
    plt.ylabel('wsg [mph]',  fontsize=12, labelpad=10) # 30 is too small, 60 
    plt.title('ws gust max observed vs stn elevation \n%s - %s PST  ' % (dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H')) , \
        fontsize=12, loc='left', weight = 'bold')   
    plt.show()
    plt.tight_layout()        
    filename = 'wsg_max_vs_elevation_time_%s_%s.png' % (dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H'))
    plot_name = os.path.join(dir_work, 'figs_ws_max_obs_maps', filename) 
    dpi_level = 400 # 400        
    #plt.savefig(plot_name)
    plt.savefig(plot_name, dpi=dpi_level) 
    #fig.clf()
    #plt.close()        

# plot_ws_vs_stn_ele
###############################################################################


###############################################################################
# read_topo 

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


if (ws_units == 'mph'): 
    ws_units_label = 'mph'
    [ ws_min,  ws_max,  ws_int] = [15.0,   80.0,  5.0]
    [wsg_min, wsg_max, wsg_int] = [35.0,  110.0,  5.0]
ws_ticks  = numpy.arange( ws_min,  ws_max,  ws_int)
wsg_ticks = numpy.arange(wsg_min, wsg_max, wsg_int)

n_cmap_ws  = len(ws_ticks)
n_cmap_wsg = len(wsg_ticks)

cmap_ws  = plt.get_cmap('afmhot_r', n_cmap_ws) 
cmap_wsg = plt.get_cmap('afmhot_r', n_cmap_wsg) 

# 'afmhot_r', 'viridis', 'jet'

# wget https://www2.census.gov/geo/tiger/TIGER2013/PRIMARYROADS/tl_2013_us_primaryroads.zip
# wget http://www2.census.gov/geo/tiger/TIGER2013/PRISECROADS/tl_2013_06_prisecroads.zip
# wget ftp://ftp2.census.gov/geo/tiger/TIGER2014/COUNTY/tl_2014_us_county.zip

plot_counties = False

country_provinces = cfeature.NaturalEarthFeature(category='cultural',
                                                 name='admin_0_boundary_lines_land',
                                                 scale='50m',
                                                 facecolor='none')
states_provinces = cfeature.NaturalEarthFeature(category='cultural',
                                                name='admin_1_states_provinces_lines',
                                                scale='50m',
                                                facecolor='none')


width_roads = 2.0

plot_area = ['nor_ca', 'nor_bay', 'nor_sierra','bay', 'cen_sierra', 'nor_valley', 'nor_coast']
n_areas = len(plot_area)




###############################################################################
# plot_ws_max_maps_obs_only 

plot_ws_max_maps_obs_only = True
if (plot_ws_max_maps_obs_only): 

    plot_legend = True
    
    a = 0
    a = 1
    # dont do
    a = 2
    a = 3
    a = 4
    a = 5
    a = 6
    for a in range(0, n_areas, 1):
        area_temp = plot_area[a]
        print      ('  plotting area %s of %s ' % (a, n_areas))
        logger.info('  plotting area %s of %s ' % (a, n_areas))    
        area_temp = plot_area[a]
        if (area_temp == 'nor_ca'):
            [hgt_min, hgt_max, hgt_int] = [-500, 13000, 1000]        
            # ca and nv
            #[lon_min, lon_max, lon_int] = [-125.0, -114.0, 2.0]
            #[lat_min, lat_max, lat_int] = [  32.0,   42.2, 1.0]
            # no ca
            [lon_min, lon_max, lon_int] = [-124.5, -117.0, 1.0]
            [lat_min, lat_max, lat_int] = [  36.0,   42.2, 0.5]
        elif (area_temp == 'nor_bay'):        
            [hgt_min, hgt_max, hgt_int] = [-500, 13000, 500]        
            [lon_min, lon_max, lon_int] = [-123.6, -121.9, 0.4]
            [lat_min, lat_max, lat_int] = [  37.8,   39.6, 0.2]
        elif (area_temp == 'nor_sierra'):
            [hgt_min, hgt_max, hgt_int] = [-500, 13000, 1000]        
            [lon_min, lon_max, lon_int] = [-122.2, -120.0, 0.4] # -122.0, -117.5, 1.0
            [lat_min, lat_max, lat_int] = [  38.6,   40.2, 0.2] # 37.0,   41.0, 0.5
        elif (area_temp == 'bay'):
            [hgt_min, hgt_max, hgt_int] = [-500, 13000, 500]        
            [lon_min, lon_max, lon_int] = [-122.8, -121.2, 0.4] 
            [lat_min, lat_max, lat_int] = [  36.8,   38.4, 0.2] 
        elif (area_temp == 'nor_valley'):
            [hgt_min, hgt_max, hgt_int] = [-500, 13000, 1000]        
            [lon_min, lon_max, lon_int] = [-123.2, -120.8, 0.4] 
            [lat_min, lat_max, lat_int] = [  39.4,   41.2, 0.2] 
        elif (area_temp == 'nor_coast'):
            [hgt_min, hgt_max, hgt_int] = [-500, 13000, 500]        
            [lon_min, lon_max, lon_int] = [-124.5, -123.0, 0.2] 
            [lat_min, lat_max, lat_int] = [  39.4,   41.6, 0.2] 
        elif (area_temp == 'cen_sierra'):
            [hgt_min, hgt_max, hgt_int] = [-500, 13000, 1000]        
            [lon_min, lon_max, lon_int] = [-121.2, -118.6, 0.4] 
            [lat_min, lat_max, lat_int] = [  36.0,   38.8, 0.2] 
    
            
        if (area_temp == 'nor_ca'):
            size_marker = 3
            [lon_legend_start, lat_legend_start, lat_legend_int] = [lon_min+0.05, lat_min+0.1, 0.1]
        else:
            size_marker = 10
            [lon_legend_start, lat_legend_start, lat_legend_int] = [lon_min+0.05, lat_min+0.1, 0.05]
             
        [figsize_x, figsize_y] = [8, 8]
            
        fig = plt.figure(num=110,figsize=(figsize_x, figsize_y)) # 10x5, 10x6, 10x10 
        plt.clf()
        ax = plt.axes(projection=ccrs.PlateCarree())
        #ax = plt.axes(projection=ccrs.LambertConformal())
        ax.set_extent([lon_min, lon_max, lat_min, lat_max])        
        ax.set_xticks(numpy.arange(lon_min, lon_max, lon_int), crs=ccrs.PlateCarree())
        ax.set_yticks(numpy.arange(lat_min, lat_max, lat_int), crs=ccrs.PlateCarree())
        lon_formatter = LongitudeFormatter(number_format='.1f',dateline_direction_label=True)
        lat_formatter = LatitudeFormatter(number_format='.1f')                 
        #ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, linewidth=0.5, color='gray', alpha=1.0, linestyle='-')
        ax.add_feature(states_provinces, edgecolor='k', linewidth=2.0)
        ax.add_feature(country_provinces, edgecolor='k', linewidth=2.0)
        ax.coastlines(resolution='10m', color='k', linewidth=2.0) # 10m, 50m, 110m
    
        shape_file_name = os.path.join(dir_shp, 'highways', 'tl_2013_us_primaryroads')
        shape_feature = ShapelyFeature(shapereader.Reader(shape_file_name).geometries(), ccrs.PlateCarree())
        ax.add_feature(shape_feature, edgecolor='g', linewidth=width_roads, facecolor='none')
        shape_file_name = os.path.join(dir_shp, 'highways', 'tl_2013_06_prisecroads')
        shape_feature = ShapelyFeature(shapereader.Reader(shape_file_name).geometries(), ccrs.PlateCarree())
        ax.add_feature(shape_feature, edgecolor='g', linewidth=width_roads, facecolor='none')
        if (plot_counties):
            shape_file_name = os.path.join(dir_shp, 'counties', 'tl_2014_us_county')
            shape_feature = ShapelyFeature(shapereader.Reader(shape_file_name).geometries(), ccrs.PlateCarree())
            ax.add_feature(shape_feature, edgecolor='m', linewidth=1.0, facecolor='none')
    
        hgt_lines = plt.contour (lon_static_2d, lat_static_2d, hgt_static_2d, levels=numpy.arange(hgt_min, hgt_max, hgt_int), colors='gray', linestyles='solid', linewidths=0.5)
    
        # plot sfc obs
        alpha_level = 1.0 # 0.3
        s = 358
        for s in range(0, dict_stn_metadata['n_stn'], 1):
            #ax.plot(dict_stn_metadata['stn_lon'][s], dict_stn_metadata['stn_lat'][s], marker='o', markersize=size_marker, markerfacecolor='w', markeredgecolor='k', transform=ccrs.PlateCarree())
         
            #if (hit_diablo_event_sum_per_year_s[s] > hit_diablo_map_plot_min): # 0.2
            if not numpy.isnan(ws_max_obs_s[s]):
                if (ws_max_obs_s[s] > ws_crit):
                    marker_edge_color = 'r'
                    marker_edge_width = 2.0 # 0.5 # 2.0
                else:
                    marker_edge_color = 'k'
                    marker_edge_width = 1.0 # 0.5 # 1.0
                     
                frac_temp = (ws_max_obs_s [s] - ws_min)/(ws_max-ws_min)
                index_cmap_temp = int(round(n_cmap_ws*frac_temp,0))
                if (index_cmap_temp >= n_cmap_ws): 
                    index_cmap_temp = n_cmap_ws - 1 
                color_temp = cmap_ws(index_cmap_temp)
                ax.plot(dict_stn_metadata['stn_lon'][s], dict_stn_metadata['stn_lat'][s], marker='o', markersize=size_marker, markerfacecolor=color_temp, markeredgecolor=marker_edge_color, markeredgewidth=marker_edge_width, alpha=alpha_level, transform=ccrs.PlateCarree())
                del frac_temp, index_cmap_temp, color_temp          
        
        # plot legend
        if (plot_legend):
            n = 4
            for n in range(0, n_cmap_ws, 1): 
                frac_temp = float(n/n_cmap_ws)
                index_cmap_temp = n
                #if (index_cmap_temp >= n_cmap_ws): 
                #    index_cmap_temp = n_cmap_ws - 1 
                color_temp = cmap_ws(index_cmap_temp)                     
                ws_temp = ws_ticks[n]
                if (ws_temp > ws_crit):
                    marker_edge_color = 'r'
                    marker_edge_width = 2.0 # 4 is too big
                else:
                    marker_edge_color = 'k'
                    marker_edge_width = 1.0        
                ax.plot(lon_legend_start, lat_legend_start+n*lat_legend_int, marker='o', markersize=size_marker, markerfacecolor=color_temp, markeredgecolor=marker_edge_color, markeredgewidth=marker_edge_width, alpha=alpha_level, transform=ccrs.PlateCarree())
                ax.text(lon_legend_start+0.03, lat_legend_start+n*lat_legend_int-lat_legend_int*0.25, str(ws_temp).rjust(2,'0'), color='k', fontsize=8, ha='left', alpha=alpha_level, transform=ccrs.PlateCarree())
    
        plt.xlabel('longitude', fontsize=12, labelpad=10) # 10 is too small, 20 
        plt.ylabel('latitude',  fontsize=12, labelpad=10) # 30 is too small, 60 
        plt.title('ws max observed \n%s - %s PST  ' % (dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H')) , \
            fontsize=12, loc='left', weight = 'bold')   
        plt.show()
        plt.tight_layout()        
        filename = 'ws_max_%s_time_%s_%s.png' % (area_temp, dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H'))
        plot_name = os.path.join(dir_work, 'figs_ws_max_obs_maps', filename) 
        dpi_level = 400 # 400        
        #plt.savefig(plot_name)
        plt.savefig(plot_name, dpi=dpi_level) 
        #fig.clf()
        #plt.close()        
    
        
        fig = plt.figure(num=111,figsize=(figsize_x, figsize_y)) # 10x5, 10x6, 10x10 
        plt.clf()
        ax = plt.axes(projection=ccrs.PlateCarree())
        #ax = plt.axes(projection=ccrs.LambertConformal())
        ax.set_extent([lon_min, lon_max, lat_min, lat_max])        
        ax.set_xticks(numpy.arange(lon_min, lon_max, lon_int), crs=ccrs.PlateCarree())
        ax.set_yticks(numpy.arange(lat_min, lat_max, lat_int), crs=ccrs.PlateCarree())
        lon_formatter = LongitudeFormatter(number_format='.1f',dateline_direction_label=True)
        lat_formatter = LatitudeFormatter(number_format='.1f')                 
        #ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, linewidth=0.5, color='gray', alpha=1.0, linestyle='-')
        ax.add_feature(states_provinces, edgecolor='k', linewidth=2.0)
        ax.add_feature(country_provinces, edgecolor='k', linewidth=2.0)
        ax.coastlines(resolution='10m', color='k', linewidth=2.0) # 10m, 50m, 110m
    
        shape_file_name = os.path.join(dir_shp, 'highways', 'tl_2013_us_primaryroads')
        shape_feature = ShapelyFeature(shapereader.Reader(shape_file_name).geometries(), ccrs.PlateCarree())
        ax.add_feature(shape_feature, edgecolor='g', linewidth=width_roads, facecolor='none')
        shape_file_name = os.path.join(dir_shp, 'highways', 'tl_2013_06_prisecroads')
        shape_feature = ShapelyFeature(shapereader.Reader(shape_file_name).geometries(), ccrs.PlateCarree())
        ax.add_feature(shape_feature, edgecolor='g', linewidth=width_roads, facecolor='none')
        if (plot_counties):
            shape_file_name = os.path.join(dir_shp, 'counties', 'tl_2014_us_county')
            shape_feature = ShapelyFeature(shapereader.Reader(shape_file_name).geometries(), ccrs.PlateCarree())
            ax.add_feature(shape_feature, edgecolor='m', linewidth=1.0, facecolor='none')
        if (plot_counties):
            shape_file_name = os.path.join(dir_shp, 'counties', 'tl_2014_us_county')
            shape_feature = ShapelyFeature(shapereader.Reader(shape_file_name).geometries(), ccrs.PlateCarree())
            ax.add_feature(shape_feature, edgecolor='m', linewidth=1.0, facecolor='none')
        
        hgt_lines = plt.contour (lon_static_2d, lat_static_2d, hgt_static_2d, levels=numpy.arange(hgt_min, hgt_max, hgt_int), colors='gray', linestyles='solid', linewidths=0.5)
     
        # plot sfc_obs
        alpha_level = 1.0 # 0.3
        s = 358
        for s in range(0, dict_stn_metadata['n_stn'], 1):
            #ax.plot(dict_stn_metadata['stn_lon'][s], dict_stn_metadata['stn_lat'][s], marker='o', markersize=size_marker, markerfacecolor='w', markeredgecolor='k', transform=ccrs.PlateCarree())
         
            #if (hit_diablo_event_sum_per_year_s[s] > hit_diablo_map_plot_min): # 0.2
            if not numpy.isnan(wsg_max_obs_s[s]):
                if (wsg_max_obs_s[s] > wsg_crit):
                    marker_edge_color = 'r'
                    marker_edge_width = 2.0 # 0.5 # 2.0 # 4 is too big
                else:
                    marker_edge_color = 'k'
                    marker_edge_width = 1.0 # 0.5 # 1.0
                     
                frac_temp = (wsg_max_obs_s [s] - wsg_min)/(wsg_max-wsg_min)
                index_cmap_temp = int(round(n_cmap_wsg*frac_temp,0))
                if (index_cmap_temp >= n_cmap_ws): 
                    index_cmap_temp = n_cmap_wsg - 1 
                color_temp = cmap_wsg(index_cmap_temp)
                ax.plot(dict_stn_metadata['stn_lon'][s], dict_stn_metadata['stn_lat'][s], marker='o', markersize=size_marker, markerfacecolor=color_temp, markeredgecolor=marker_edge_color, markeredgewidth=marker_edge_width, alpha=alpha_level, transform=ccrs.PlateCarree())
                del frac_temp, index_cmap_temp, color_temp          
        
        # plot legend
        if (plot_legend):
            n = 4
            for n in range(0, n_cmap_ws, 1): 
                frac_temp = float(n/n_cmap_ws)
                index_cmap_temp = n
                #if (index_cmap_temp >= n_cmap_ws): 
                #    index_cmap_temp = n_cmap_ws - 1 
                color_temp = cmap_wsg(index_cmap_temp)                     
                wsg_temp = wsg_ticks[n]
                if (wsg_temp > wsg_crit):
                    marker_edge_color = 'r'
                    marker_edge_width = 2.0 # 4 is too big
                else:
                    marker_edge_color = 'k'
                    marker_edge_width = 1.0        
                ax.plot(lon_legend_start, lat_legend_start+n*lat_legend_int, marker='o', markersize=size_marker, markerfacecolor=color_temp, markeredgecolor=marker_edge_color, markeredgewidth=marker_edge_width, alpha=alpha_level, transform=ccrs.PlateCarree())
                ax.text(lon_legend_start+0.03, lat_legend_start+n*lat_legend_int-lat_legend_int*0.25, str(wsg_temp).rjust(2,'0'), color='k', fontsize=8, ha='left', alpha=alpha_level, transform=ccrs.PlateCarree())
    
        plt.xlabel('longitude', fontsize=12, labelpad=10) # 10 is too small, 20 
        plt.ylabel('latitude',  fontsize=12, labelpad=10) # 30 is too small, 60 
        plt.title('wsg max observed \n%s - %s PST  ' % (dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H')) , \
            fontsize=12, loc='left', weight = 'bold')   
        plt.show()
        plt.tight_layout()        
        filename = 'wsg_max_%s_time_%s_%s.png' % (area_temp, dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H'))
        plot_name = os.path.join(dir_work, 'figs_ws_max_obs_maps', filename) 
        dpi_level = 400 # 400        
        #plt.savefig(plot_name)
        plt.savefig(plot_name, dpi=dpi_level) 
        #fig.clf()
        #plt.close()        
    
# plot_ws_max_maps_obs_only 
###############################################################################


###############################################################################
# read_model_data

print      ('read_model_data begin')
logger.info('read_model_data begin')

# old runs
#[ny, nx] = [1059, 839] # must know a priori
# new 
#[ny, nx] = [1059, 596] # must know a priori
# new 
#[ny, nx] = [940, 357] # must know a priori

initial_read = False
hr = 0
for hr in range(0, n_hrs, 1):
    dt_valid_temp = dt_min_plot_utc + td(hours=hr)
    print      ('  reading %s UTC ' %(dt_valid_temp.strftime('%Y-%m-%d_%H')))
    logger.info('  reading %s UTC ' %(dt_valid_temp.strftime('%Y-%m-%d_%H')))
    # new format
    (file_name_temp_ingest, file_name_temp_archive) = build_model_local_file_names(logger, model_name, dt_init_utc, dt_valid_temp, dir_data_model_raw_ingest, dir_data_model_raw_archive)
    # old format
    #file_name = dt_init_utc.strftime('%Y%m%d%H')+'f'+str(hr).rjust(2,'0')+'_hrrrall.grib2'
    #file_name_temp_ingest = os.path.join(dir_data_model_raw_ingest, file_name)
    os.path.isfile(file_name_temp_ingest)    
    #if not (os.path.isfile(file_name_temp_ingest)) or (os.path.isfile(file_name_temp_archive)):
    if not (os.path.isfile(file_name_temp_ingest)):
        print      ('  ERROR missing file ')
        logger.info('  ERROR missing file ')
        #sys.exit()
    else: # file exists
        # ds = xarray.open_dataset(file_name_temp_ingest, engine='cfgrib')
        #ds_sfc = xarray.open_dataset(file_name_temp_ingest, engine='cfgrib',
        #      backend_kwargs={'filter_by_keys': {'typeOfLevel': 'heightAboveGround', 'level': 'surface'}})
        ds_2m = xarray.open_dataset(file_name_temp_ingest, engine='cfgrib',
              backend_kwargs={'filter_by_keys': {'typeOfLevel': 'heightAboveGround', 'level': 2}})
        ds_10m = xarray.open_dataset(file_name_temp_ingest, engine='cfgrib',
             backend_kwargs={'filter_by_keys': {'typeOfLevel': 'heightAboveGround', 'level': 10}})
        #ds_sfc
        #ds_2m
        #ds_10m
        if not (initial_read):
            lon_2d = numpy.array(ds_10m['longitude'])
            lat_2d = numpy.array(ds_10m['latitude'])
            #hgt_2d = numpy.array(ds_sfc['orog'])
            #hgt_2d = hgt_2d*3.28084 # m to ft
            [ny, nx] = numpy.shape(lon_2d)
            ws10_2d_hr  = numpy.full([ny, nx, n_hrs], numpy.nan, dtype=float)
            wsg10_2d_hr = numpy.full([ny, nx, n_hrs], numpy.nan, dtype=float)
            initial_read = True    
        u_ws10_2d = numpy.array(ds_10m['u10'])
        v_ws10_2d = numpy.array(ds_10m['v10'])
        ws10_2d = numpy.sqrt(u_ws10_2d**2.0 + v_ws10_2d**2.0)
        ws10_2d_hr [:,:,hr] = ws10_2d 
        try:
            ds_sfc = xarray.open_dataset(file_name_temp_ingest, engine='cfgrib',
                 backend_kwargs={'filter_by_keys': {'typeOfLevel': 'surface'}})
            wsg10_2d = numpy.array(ds_sfc['gust'])
            wsg10_2d_hr[:,:,hr] = wsg10_2d 
            hgt_2d = numpy.array(ds_sfc['orog'])
            del wsg10_2d
        except:
            pass
        del u_ws10_2d, v_ws10_2d, ws10_2d

lon_2d = lon_2d - 360.0        
print      ('read_data end')
logger.info('read_data end')

# read_model_data
###############################################################################


###############################################################################
# process to max 

print      ('process_to_max begin')
logger.info('process_to_max begin')

ws10_max_2d  = numpy.full([ny, nx], numpy.nan, dtype=float)
wsg10_max_2d = numpy.full([ny, nx], numpy.nan, dtype=float)
for j in range(0, ny , 1):
    for i in range(0, nx, 1):
        ws10_max_2d [j,i] = numpy.nanmax( ws10_2d_hr[j,i,:])
        wsg10_max_2d[j,i] = numpy.nanmax(wsg10_2d_hr[j,i,:])

print      ('process_to_max end')
logger.info('process_to_max end')

# process to max 
###############################################################################


###############################################################################
# write_max_model_data 

write_max_model_data = True

if (write_max_model_data):
        
    file_name_write = os.path.join(dir_data_model, 'event_max', 'max_'+event+'_model_'+model_name+'_init_'+dt_init_utc.strftime('%Y-%m-%d_%H')+'.nc')
    print      ('  file_name_write is %s ' % (file_name_write)) 
    logger.info('  file_name_write is %s ' % (file_name_write)) 
    if (os.path.isfile(file_name_write)):
        os.system('rm -f '+file_name_write)
    ncfile_write = Dataset(file_name_write, 'w',format='NETCDF4_CLASSIC')

    ncfile_write.createDimension('y', ny)
    ncfile_write.createDimension('x', nx)

    lon_2d_write = ncfile_write.createVariable('lon_2d', numpy.dtype('float32').char,('y','x'))
    lat_2d_write = ncfile_write.createVariable('lat_2d', numpy.dtype('float32').char,('y','x'))
    hgt_2d_write = ncfile_write.createVariable('hgt_2d', numpy.dtype('float32').char,('y','x'))
    lon_2d_write [:] =  lon_2d
    lat_2d_write [:] =  lat_2d
    hgt_2d_write [:] =  hgt_2d
    
    ws10_max_2d_write    = ncfile_write.createVariable('ws10_max_2d',  numpy.dtype('float32').char,('y','x'))
    wsg10_max_2d_write   = ncfile_write.createVariable('wsg10_max_2d', numpy.dtype('float32').char,('y','x'))
    ws10_max_2d_write [:] =  ws10_max_2d[:,:]     
    wsg10_max_2d_write[:] = wsg10_max_2d[:,:]     

    del lon_2d_write, lat_2d_write, hgt_2d_write, ws10_max_2d_write, wsg10_max_2d_write
 
    ncfile_write.close()

# write_max_model_data 
###############################################################################


#read_max_model_data 
print      (' read file begin ') 
logger.info(' read file begin ') 

file_name_read = os.path.join(dir_data_model, 'event_max', 'max_'+event+'_model_'+model_name+'_init_'+dt_init_utc.strftime('%Y-%m-%d_%H')+'.nc')
ncfile_read  = Dataset(file_name_read,'r') 
lon_2d = numpy.array(ncfile_read.variables['lon_2d'])
lat_2d = numpy.array(ncfile_read.variables['lat_2d'])
hgt_2d = numpy.array(ncfile_read.variables['hgt_2d'])
wsg10_max_2d = numpy.array(ncfile_read.variables['wsg10_max_2d'])
ws10_max_2d  = numpy.array(ncfile_read.variables[' ws10_max_2d'])
ncfile_read.close()
print      (' read file end ') 
logger.info(' read file end ') 


    

###############################################################################
# units_conversion

print      ('units_conversion start')
logger.info('units_conversion start')

ws_units= 'mph'
#ws_units_label = 'ms$^{-1}$'
ws_units_label = 'mph'

wsg10_max_2d = 2.23694*wsg10_max_2d
ws10_max_2d  = 2.23694*ws10_max_2d

#numpy.nanmin(wsg10_max_2d)
#numpy.nanmax(wsg10_max_2d)
#numpy.nanmin(ws10_max_2d)
#numpy.nanmax(ws10_max_2d)

print      ('units_conversion end')
logger.info('units_conversion end')

# units_conversion
###############################################################################


###############################################################################
# plot 

plot_legend = False

a = 0
a = 1
a = 2
a = 3
a = 4
a = 5
a = 6
for a in range(0, n_areas, 1):
    area_temp = plot_area[a]
    print      ('  plotting area %s of %s ' % (a, n_areas))
    logger.info('  plotting area %s of %s ' % (a, n_areas))    
    area_temp = plot_area[a]
    if (area_temp == 'nor_ca'):
        [hgt_min, hgt_max, hgt_int] = [-500, 13000, 1000]        
        # ca and nv
        #[lon_min, lon_max, lon_int] = [-125.0, -114.0, 2.0]
        #[lat_min, lat_max, lat_int] = [  32.0,   42.2, 1.0]
        # no ca
        [lon_min, lon_max, lon_int] = [-124.5, -117.0, 1.0]
        [lat_min, lat_max, lat_int] = [  36.0,   42.2, 0.5]
    elif (area_temp == 'nor_bay'):        
        [hgt_min, hgt_max, hgt_int] = [-500, 13000, 500]        
        [lon_min, lon_max, lon_int] = [-123.6, -121.9, 0.4]
        [lat_min, lat_max, lat_int] = [  37.8,   39.6, 0.2]
    elif (area_temp == 'nor_sierra'):
        [hgt_min, hgt_max, hgt_int] = [-500, 13000, 1000]        
        [lon_min, lon_max, lon_int] = [-122.2, -120.0, 0.4] # -122.0, -117.5, 1.0
        [lat_min, lat_max, lat_int] = [  38.6,   40.2, 0.2] # 37.0,   41.0, 0.5
    elif (area_temp == 'bay'):
        [hgt_min, hgt_max, hgt_int] = [-500, 13000, 500]        
        [lon_min, lon_max, lon_int] = [-122.8, -121.2, 0.4] 
        [lat_min, lat_max, lat_int] = [  36.8,   38.4, 0.2] 
    elif (area_temp == 'nor_valley'):
        [hgt_min, hgt_max, hgt_int] = [-500, 13000, 1000]        
        [lon_min, lon_max, lon_int] = [-123.2, -120.8, 0.4] 
        [lat_min, lat_max, lat_int] = [  39.4,   41.2, 0.2] 
    elif (area_temp == 'nor_coast'):
        [hgt_min, hgt_max, hgt_int] = [-500, 13000, 500]        
        [lon_min, lon_max, lon_int] = [-124.5, -123.0, 0.2] 
        [lat_min, lat_max, lat_int] = [  39.4,   41.6, 0.2] 
    elif (area_temp == 'cen_sierra'):
        [hgt_min, hgt_max, hgt_int] = [-500, 13000, 1000]        
        [lon_min, lon_max, lon_int] = [-121.2, -118.6, 0.4] 
        [lat_min, lat_max, lat_int] = [  36.0,   38.8, 0.2] 

        
    if (area_temp == 'nor_ca'):
        size_marker = 3
        [lon_legend_start, lat_legend_start, lat_legend_int] = [lon_min+0.05, lat_min+0.1, 0.1]
    else:
        size_marker = 10
        [lon_legend_start, lat_legend_start, lat_legend_int] = [lon_min+0.05, lat_min+0.1, 0.05]
         
    [figsize_x, figsize_y] = [8, 8]
        
    fig = plt.figure(num=110,figsize=(figsize_x, figsize_y)) # 10x5, 10x6, 10x10 
    plt.clf()
    ax = plt.axes(projection=ccrs.PlateCarree())
    #ax = plt.axes(projection=ccrs.LambertConformal())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])        
    ax.set_xticks(numpy.arange(lon_min, lon_max, lon_int), crs=ccrs.PlateCarree())
    ax.set_yticks(numpy.arange(lat_min, lat_max, lat_int), crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(number_format='.1f',dateline_direction_label=True)
    lat_formatter = LatitudeFormatter(number_format='.1f')                 
    #ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, linewidth=0.5, color='gray', alpha=1.0, linestyle='-')
    ax.add_feature(states_provinces, edgecolor='k', linewidth=2.0)
    ax.add_feature(country_provinces, edgecolor='k', linewidth=2.0)
    ax.coastlines(resolution='10m', color='k', linewidth=2.0) # 10m, 50m, 110m

    shape_file_name = os.path.join(dir_shp, 'highways', 'tl_2013_us_primaryroads')
    shape_feature = ShapelyFeature(shapereader.Reader(shape_file_name).geometries(), ccrs.PlateCarree())
    ax.add_feature(shape_feature, edgecolor='g', linewidth=width_roads, facecolor='none')
    shape_file_name = os.path.join(dir_shp, 'highways', 'tl_2013_06_prisecroads')
    shape_feature = ShapelyFeature(shapereader.Reader(shape_file_name).geometries(), ccrs.PlateCarree())
    ax.add_feature(shape_feature, edgecolor='g', linewidth=width_roads, facecolor='none')
    if (plot_counties):
        shape_file_name = os.path.join(dir_shp, 'counties', 'tl_2014_us_county')
        shape_feature = ShapelyFeature(shapereader.Reader(shape_file_name).geometries(), ccrs.PlateCarree())
        ax.add_feature(shape_feature, edgecolor='m', linewidth=1.0, facecolor='none')

    hgt_lines = plt.contour (lon_static_2d, lat_static_2d, hgt_static_2d, levels=numpy.arange(hgt_min, hgt_max, hgt_int), colors='gray', linestyles='solid', linewidths=0.5)
    im = plt.contourf(lon_2d, lat_2d, ws10_max_2d, numpy.arange(ws_min, ws_max, ws_int), cmap=cmap_ws, transform=ccrs.PlateCarree()) # jet, viridis 
    #ws_lines = plt.contour(lon_2d, lat_2d, ws10_max_2d, levels = numpy.arange(ws_min, ws_max, ws_int), colors='k', linestyles='solid', linewidths=0.5)
    ws_line  = plt.contour(lon_2d, lat_2d, ws10_max_2d, levels = [ws_crit], colors='r', linestyles='solid',linewidths=2)
    im.set_clim(ws_min, ws_max) 
    cbar = fig.colorbar(im, shrink=0.6) # was 0.7 0.8
    #cbar = fig.colorbar(im)
    cbar.set_label('ws [mph]',fontsize=12,labelpad=00)                                

    # plot sfc obs
    alpha_level = 1.0 # 0.3
    s = 358
    for s in range(0, dict_stn_metadata['n_stn'], 1):
        #ax.plot(dict_stn_metadata['stn_lon'][s], dict_stn_metadata['stn_lat'][s], marker='o', markersize=size_marker, markerfacecolor='w', markeredgecolor='k', transform=ccrs.PlateCarree())
     
        #if (hit_diablo_event_sum_per_year_s[s] > hit_diablo_map_plot_min): # 0.2
        if not numpy.isnan(ws_max_obs_s[s]):
            if (ws_max_obs_s[s] > ws_crit):
                marker_edge_color = 'r'
                marker_edge_width = 2.0 # 4 is too big
            else:
                marker_edge_color = 'k'
                marker_edge_width = 1.0
                 
            frac_temp = (ws_max_obs_s [s] - ws_min)/(ws_max-ws_min)
            index_cmap_temp = int(round(n_cmap_ws*frac_temp,0))
            if (index_cmap_temp >= n_cmap_ws): 
                index_cmap_temp = n_cmap_ws - 1 
            color_temp = cmap_ws(index_cmap_temp)
            ax.plot(dict_stn_metadata['stn_lon'][s], dict_stn_metadata['stn_lat'][s], marker='o', markersize=size_marker, markerfacecolor=color_temp, markeredgecolor=marker_edge_color, markeredgewidth=marker_edge_width, alpha=alpha_level, transform=ccrs.PlateCarree())
            del frac_temp, index_cmap_temp, color_temp          
    
    # plot legend
    if (plot_legend):
        n = 4
        for n in range(0, n_cmap_ws, 1): 
            frac_temp = float(n/n_cmap_ws)
            index_cmap_temp = n
            #if (index_cmap_temp >= n_cmap_ws): 
            #    index_cmap_temp = n_cmap_ws - 1 
            color_temp = cmap_ws(index_cmap_temp)                     
            ws_temp = ws_ticks[n]
            if (ws_temp > ws_crit):
                marker_edge_color = 'r'
                marker_edge_width = 2.0 # 4 is too big
            else:
                marker_edge_color = 'k'
                marker_edge_width = 1.0        
            ax.plot(lon_legend_start, lat_legend_start+n*lat_legend_int, marker='o', markersize=size_marker, markerfacecolor=color_temp, markeredgecolor=marker_edge_color, markeredgewidth=marker_edge_width, alpha=alpha_level, transform=ccrs.PlateCarree())
            ax.text(lon_legend_start+0.03, lat_legend_start+n*lat_legend_int-lat_legend_int*0.25, str(ws_temp).rjust(2,'0'), color='k', fontsize=8, ha='left', alpha=alpha_level, transform=ccrs.PlateCarree())

    # plot ignitions 
    # kincade fire in no bay 
    if ((event == '2019_10_09_event') and (a == 1)):
        ax.plot(-122.780053, 38.792458, marker='+', markersize=20, markerfacecolor='m', markeredgecolor='m', markeredgewidth=3.0, alpha=1.0, transform=ccrs.PlateCarree())
    # lafayette, bothel etc 
    if ((event == '2019_10_27_event') and (a == 3)):
        #lafayette x2, oakley, bothel, milpitas
        ax.plot(-122.123333, 37.895000, marker='+', markersize=20, markerfacecolor='m', markeredgecolor='m', markeredgewidth=3.0, alpha=1.0, transform=ccrs.PlateCarree())
        ax.plot(-122.118611, 37.895833, marker='+', markersize=20, markerfacecolor='m', markeredgecolor='m', markeredgewidth=3.0, alpha=1.0, transform=ccrs.PlateCarree())
        ax.plot(-121.658333, 38.028333, marker='+', markersize=20, markerfacecolor='m', markeredgecolor='m', markeredgewidth=3.0, alpha=1.0, transform=ccrs.PlateCarree())    
        ax.plot(-121.678333, 38.000000, marker='+', markersize=20, markerfacecolor='m', markeredgecolor='m', markeredgewidth=3.0, alpha=1.0, transform=ccrs.PlateCarree())    
        ax.plot(-121.874444, 37.456111, marker='+', markersize=20, markerfacecolor='m', markeredgecolor='m', markeredgewidth=3.0, alpha=1.0, transform=ccrs.PlateCarree())    

    plt.xlabel('longitude', fontsize=12, labelpad=10) # 10 is too small, 20 
    plt.ylabel('latitude',  fontsize=12, labelpad=10) # 30 is too small, 60 
    plt.title('ws max %s %s UTC init \n%s - %s PST  ' % (model_name, dt_init_utc.strftime('%Y-%m-%d_%H'), dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H')) , \
        fontsize=12, loc='left', weight = 'bold')   
    plt.show()
    plt.tight_layout()        
    filename = 'ws_max_%s_model_%s_init_%s_time_%s_%s.png' % (area_temp, model_name, dt_init_utc.strftime('%Y-%m-%d_%H'), dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H'))
    plot_name = os.path.join(dir_work, 'figs_ws_max_maps', filename) 
    dpi_level = 400 # 400        
    #plt.savefig(plot_name)
    plt.savefig(plot_name, dpi=dpi_level) 
    #fig.clf()
    #plt.close()        

    
    fig = plt.figure(num=111,figsize=(figsize_x, figsize_y)) # 10x5, 10x6, 10x10 
    plt.clf()
    ax = plt.axes(projection=ccrs.PlateCarree())
    #ax = plt.axes(projection=ccrs.LambertConformal())
    ax.set_extent([lon_min, lon_max, lat_min, lat_max])        
    ax.set_xticks(numpy.arange(lon_min, lon_max, lon_int), crs=ccrs.PlateCarree())
    ax.set_yticks(numpy.arange(lat_min, lat_max, lat_int), crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(number_format='.1f',dateline_direction_label=True)
    lat_formatter = LatitudeFormatter(number_format='.1f')                 
    #ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False, linewidth=0.5, color='gray', alpha=1.0, linestyle='-')
    ax.add_feature(states_provinces, edgecolor='k', linewidth=2.0)
    ax.add_feature(country_provinces, edgecolor='k', linewidth=2.0)
    ax.coastlines(resolution='10m', color='k', linewidth=2.0) # 10m, 50m, 110m

    shape_file_name = os.path.join(dir_shp, 'highways', 'tl_2013_us_primaryroads')
    shape_feature = ShapelyFeature(shapereader.Reader(shape_file_name).geometries(), ccrs.PlateCarree())
    ax.add_feature(shape_feature, edgecolor='g', linewidth=width_roads, facecolor='none')
    shape_file_name = os.path.join(dir_shp, 'highways', 'tl_2013_06_prisecroads')
    shape_feature = ShapelyFeature(shapereader.Reader(shape_file_name).geometries(), ccrs.PlateCarree())
    ax.add_feature(shape_feature, edgecolor='g', linewidth=width_roads, facecolor='none')
    if (plot_counties):
        shape_file_name = os.path.join(dir_shp, 'counties', 'tl_2014_us_county')
        shape_feature = ShapelyFeature(shapereader.Reader(shape_file_name).geometries(), ccrs.PlateCarree())
        ax.add_feature(shape_feature, edgecolor='m', linewidth=1.0, facecolor='none')
    if (plot_counties):
        shape_file_name = os.path.join(dir_shp, 'counties', 'tl_2014_us_county')
        shape_feature = ShapelyFeature(shapereader.Reader(shape_file_name).geometries(), ccrs.PlateCarree())
        ax.add_feature(shape_feature, edgecolor='m', linewidth=1.0, facecolor='none')
    
    hgt_lines = plt.contour (lon_static_2d, lat_static_2d, hgt_static_2d, levels=numpy.arange(hgt_min, hgt_max, hgt_int), colors='gray', linestyles='solid', linewidths=0.5)
    im = plt.contourf(lon_2d, lat_2d, wsg10_max_2d, numpy.arange(wsg_min, wsg_max, wsg_int), cmap=cmap_wsg, transform=ccrs.PlateCarree()) # jet, viridis 
    #wsg_lines = plt.contour(lon_2d, lat_2d, wsg10_max_2d, levels = numpy.arange(wsg_min, wsg_max, wsg_int), colors='k', linestyles='solid', linewidths=0.5)
    wsg_line        = plt.contour(lon_2d, lat_2d, wsg10_max_2d, levels = [wsg_crit], colors='r', linestyles='solid',linewidths=2)
    wsg_line_t_line = plt.contour(lon_2d, lat_2d, wsg10_max_2d, levels = [wsg_crit_t_line], colors='m', linestyles='solid',linewidths=2)
    im.set_clim(wsg_min, wsg_max) 
    cbar = fig.colorbar(im, shrink=0.6) # 0.8
    #cbar = fig.colorbar(im)
    #cbar.set_label('ws [mph]',fontsize=12,labelpad=00)                                
    cbar.set_label('wsg [mph]',fontsize=12,labelpad=00)                                

    # plot sfc_obs
    alpha_level = 1.0 # 0.3
    s = 358
    for s in range(0, dict_stn_metadata['n_stn'], 1):
        #ax.plot(dict_stn_metadata['stn_lon'][s], dict_stn_metadata['stn_lat'][s], marker='o', markersize=size_marker, markerfacecolor='w', markeredgecolor='k', transform=ccrs.PlateCarree())
     
        #if (hit_diablo_event_sum_per_year_s[s] > hit_diablo_map_plot_min): # 0.2
        if not numpy.isnan(wsg_max_obs_s[s]):
            if (wsg_max_obs_s[s] > wsg_crit):
                marker_edge_color = 'r'
                marker_edge_width = 2.0 # 4 is too big
            else:
                marker_edge_color = 'k'
                marker_edge_width = 1.0
                 
            frac_temp = (wsg_max_obs_s [s] - wsg_min)/(wsg_max-wsg_min)
            index_cmap_temp = int(round(n_cmap_wsg*frac_temp,0))
            if (index_cmap_temp >= n_cmap_wsg): 
                index_cmap_temp = n_cmap_wsg - 1 
            color_temp = cmap_wsg(index_cmap_temp)
            ax.plot(dict_stn_metadata['stn_lon'][s], dict_stn_metadata['stn_lat'][s], marker='o', markersize=size_marker, markerfacecolor=color_temp, markeredgecolor=marker_edge_color, markeredgewidth=marker_edge_width, alpha=alpha_level, transform=ccrs.PlateCarree())
            del frac_temp, index_cmap_temp, color_temp          
    
    # plot legend
    if (plot_legend):
        n = 4
        for n in range(0, n_cmap_ws, 1): 
            frac_temp = float(n/n_cmap_wsg)
            index_cmap_temp = n
            #if (index_cmap_temp >= n_cmap_ws): 
            #    index_cmap_temp = n_cmap_ws - 1 
            color_temp = cmap_wsg(index_cmap_temp)
            wsg_temp = wsg_ticks[n]
            if (wsg_temp > wsg_crit):
                marker_edge_color = 'r'
                marker_edge_width = 2.0 # 4 is too big
            else:
                marker_edge_color = 'k'
                marker_edge_width = 1.0        
            ax.plot(lon_legend_start, lat_legend_start+n*lat_legend_int, marker='o', markersize=size_marker, markerfacecolor=color_temp, markeredgecolor=marker_edge_color, markeredgewidth=marker_edge_width, alpha=alpha_level, transform=ccrs.PlateCarree())
            ax.text(lon_legend_start+0.03, lat_legend_start+n*lat_legend_int-lat_legend_int*0.25, str(wsg_temp).rjust(2,'0'), color='k', fontsize=8, ha='left', alpha=alpha_level, transform=ccrs.PlateCarree())

    # plot ignitions 
    # kincade fire in no bay 
    if ((event == '2019_10_09_event') and (a == 1)):
        ax.plot(-122.780053, 38.792458, marker='+', markersize=20, markerfacecolor='m', markeredgecolor='m', markeredgewidth=3.0, alpha=1.0, transform=ccrs.PlateCarree())
    # lafayette, bothel etc 
    if ((event == '2019_10_27_event') and (a == 3)):
        #lafayette x2, oakley, bothel, milpitas
        ax.plot(-122.123333, 37.895000, marker='+', markersize=20, markerfacecolor='m', markeredgecolor='m', markeredgewidth=3.0, alpha=1.0, transform=ccrs.PlateCarree())
        ax.plot(-122.118611, 37.895833, marker='+', markersize=20, markerfacecolor='m', markeredgecolor='m', markeredgewidth=3.0, alpha=1.0, transform=ccrs.PlateCarree())
        ax.plot(-121.658333, 38.028333, marker='+', markersize=20, markerfacecolor='m', markeredgecolor='m', markeredgewidth=3.0, alpha=1.0, transform=ccrs.PlateCarree())    
        ax.plot(-121.678333, 38.000000, marker='+', markersize=20, markerfacecolor='m', markeredgecolor='m', markeredgewidth=3.0, alpha=1.0, transform=ccrs.PlateCarree())    
        ax.plot(-121.874444, 37.456111, marker='+', markersize=20, markerfacecolor='m', markeredgecolor='m', markeredgewidth=3.0, alpha=1.0, transform=ccrs.PlateCarree())    

    plt.xlabel('longitude', fontsize=12, labelpad=10) # 10 is too small, 20 
    plt.ylabel('latitude',  fontsize=12, labelpad=10) # 30 is too small, 60 
    plt.title('wsg max %s %s UTC init \n%s - %s PST  ' % (model_name, dt_init_utc.strftime('%Y-%m-%d_%H'), dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H')) , \
        fontsize=12, loc='left', weight = 'bold')   
    plt.show()
    plt.tight_layout()        
    filename = 'wsg_max_%s_model_%s_init_%s_time_%s_%s.png' % (area_temp, model_name, dt_init_utc.strftime('%Y-%m-%d_%H'), dt_min_plot_pst.strftime('%Y-%m-%d_%H'), dt_max_plot_pst.strftime('%Y-%m-%d_%H'))
    plot_name = os.path.join(dir_work, 'figs_ws_max_maps', filename) 
    dpi_level = 400 # 400        
    #plt.savefig(plot_name)
    plt.savefig(plot_name, dpi=dpi_level) 
    #fig.clf()
    #plt.close()        
    
# plot 
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
