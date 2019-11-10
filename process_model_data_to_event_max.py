
###############################################################################
# process_model_data_to_event_max.py
# author: Craig Smith 
# purpose: reduce forecast data to event max and write 
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

# python /home/craigmatthewsmith/offshore_winds/offshore_winds/process_model_data_to_event_max.py --event='2019_10_09_event' --dt_min_plot_utc_str='2019-10-09_08' --dt_max_plot_utc_str='2019-10-11_08' --model_name='nam' --dt_init_utc_str='2019-10-07_12' 
# 2019-10-10_00


###############################################################################
# module import and set directories
 
manual_mode = False
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
process_name = 'process_to_event_max'
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
    event = '2018_10_14_event'
    # PSPS time was  2018/10/14 20 - 2018/10/16 15, or 2018/10/17 06 PST 
    # plotting   2018-10-13_00 - 2018-10-16_08 PST
    # peak event 2018/10/14 12 - 2018/10/15 12 PST 
    dt_min_plot_utc_str = '2018-10-13_08'
    dt_max_plot_utc_str = '2018-10-16_16'
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
    model_name = 'hrrr' 
    # probably too early, but will do anyways 
    dt_init_utc_str     = '2018-10-13_12'
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
    #event = '2019_10_27_event'
    # U 10/27 1 am PST - U 10/27 23:59 pm PST 

    #dt_min_plot_utc_str = '2019-10-26_08'
    #dt_max_plot_utc_str = '2019-10-29_08'
    # plotting 2019-10-09_00 - 2019-10-11_00 PST 
    #model_name = 'nam'
    # earliest possible, ends 
    # best / retain on local
    #dt_init_utc_str     = '2019-10-26_00'
    # latest_posibble ends
    #model_name = 'hrrr'
    # earliest possible, ends 2019/10/27 16 PST
    #dt_init_utc_str     = '2019-10-26_12'
    # best / retain on local
    #dt_init_utc_str     = '2019-10-27_00'
    # latest possible start 2019/10/27 04 PST 
    #dt_init_utc_str     = '2019-10-27_12'
    # latest_posibble ends
   
else:        
    parser = argparse.ArgumentParser(description='model to use')
    parser.add_argument('--event', type=str, help='event', required=True)    
    parser.add_argument('--model_name', type=str, help='model_name', required=True)    
    parser.add_argument('--dt_init_utc_str', type=str, help='dt_init_utc_str', required=True)    
    parser.add_argument('--dt_min_plot_utc_str', type=str, help='dt_min_plot_utc_str', required=True)    
    parser.add_argument('--dt_max_plot_utc_str', type=str, help='dt_max_plot_utc_str', required=True)
    args = parser.parse_args()
    event = args.event
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
# read_topo 

#print      ('read_topo_data begin')
#logger.info('read_topo_data begin')
#
#file_name_temp_ingest = os.path.join(dir_work, 'nam_static.grib2')
#ds_sfc = xarray.open_dataset(file_name_temp_ingest, engine='cfgrib',
#     backend_kwargs={'filter_by_keys': {'typeOfLevel': 'surface'}})
#lon_static_2d = numpy.array(ds_sfc['longitude'])
#lat_static_2d = numpy.array(ds_sfc['latitude'])
#hgt_static_2d = numpy.array(ds_sfc['orog'])
#hgt_static_2d = hgt_static_2d*3.28084 # m to ft

# read_topo 
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
    #(file_name_temp_ingest, file_name_temp_archive) = build_model_local_file_names(logger, model_name, dt_init_utc, dt_valid_temp, dir_data_model_raw_ingest, dir_data_model_raw_archive)
    # old format
    file_name = dt_init_utc.strftime('%Y%m%d%H')+'f'+str(hr).rjust(2,'0')+'_hrrrall.grib2'
    file_name_temp_ingest = os.path.join(dir_data_model_raw_ingest, file_name)
    # from gcp 
    # file_name_temp_ingest = os.path.join(dir_data_model_raw_ingest, 'hrrr.20181107_conus_hrrr.t12z.wrfsfcf27.grib2')
        
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
            #ds_sfc = xarray.open_dataset(file_name_temp_ingest, engine='cfgrib',
            #     backend_kwargs={'filter_by_keys': {'typeOfLevel': 'surface'}})
            ds_sfc = xarray.open_dataset(file_name_temp_ingest, engine='cfgrib',
                 backend_kwargs={'filter_by_keys': {'stepType': 'instant', 'typeOfLevel': 'surface'}})

            
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
    try:
        hgt_2d_write [:] =  hgt_2d
    except:
        pass
    
    ws10_max_2d_write    = ncfile_write.createVariable('ws10_max_2d',  numpy.dtype('float32').char,('y','x'))
    wsg10_max_2d_write   = ncfile_write.createVariable('wsg10_max_2d', numpy.dtype('float32').char,('y','x'))
    ws10_max_2d_write [:] =  ws10_max_2d[:,:]     
    wsg10_max_2d_write[:] = wsg10_max_2d[:,:]     

    del lon_2d_write, lat_2d_write, hgt_2d_write, ws10_max_2d_write, wsg10_max_2d_write
 
    ncfile_write.close()

# write_max_model_data 
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
