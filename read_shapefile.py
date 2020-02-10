
###############################################################################
# compare_all_events.py 
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



import shapely
# does not work 
# import fiona


dir_work = '/home/craigmatthewsmith/projects/'+project_name
os.chdir(dir_work) 


dir_shp = os.path.join(dir_work, 'psps_polygons')


shp_name = 'PUBLIC_PSPS 10-09-19 C-03_BaseLine_1007_1655'


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
process_name = 'event_intercomparison'
log_file_name = 'log_'+process_name+'_'+project_name+'_'+dt_cron_start_lt.strftime('%Y-%m-%d_%H-%M')+'.txt' 
log_name_full_file_path = os.path.join(dir_work, 'archive_logs', log_file_name) 
logger = instantiate_logger(log_name_full_file_path, dt_cron_start_lt) 
print      ('instantiate_logger end' ) 

# instantiate logger 
###############################################################################


###############################################################################
# define event and inits to use 

model_name = 'hrrr'
event_list  = ['2018_10_14_event', '2018_11_08_event', '2019_10_09_event', '2019_10_23_event', '2019_10_27_event', '2017_10_08_event'] 
event_ticks = ['10/14/2018',       '11/08/2018',       '10/09/2019',       '10/23/2019',       '10/27/2019',       '10/08/2017'] 
# 1
#init_list   = ['2018-10-14_12',    '2018-11-07_12',    '2019-10-09_12',    '2019-10-23_12',    '2019-10-27_00',    'none'] 
# 3
#init_list  = ['2018-10-14_12',    '2018-11-07_12',    '2019-10-09_12',    '2019-10-23_12',    '2019-10-27_00',    'none'] 
#4
init_list  = ['2018-10-14_12',    '2018-11-08_00',    '2019-10-09_12',    '2019-10-23_12',    '2019-10-27_00',    'none'] 

# events to compare
# '2019_10_09_event', '2019_10_23_event'
# '2018_10_14_event', '2018_11_08_event'
# '2017_10_08_event', '2019_10_27_event' # former has no hrrr


n_events = len(event_list)
event_axis = numpy.arange(0, n_events, 1)

# '2017_10_08_event'
# no model data 

# define event and inits to use 
###############################################################################

[ws_crit, wsgd_crit, wsgt_crit] = [25.0, 45.0, 55.0]



###############################################################################
# read stn_info 

#use_stn = 'all'
use_stn = 'mnet=2' # RAWS only  
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
            #stn_read_df.index()
            dt_read_utc = stn_read_df.index
            dt_read_pst = dt_read_utc - td(hours=8)
                
            del ws_read, wsg_read, rh_read, wd_read, stn_read_df, dt_read_pst, dt_read_utc

# 
###############################################################################


###############################################################################
# read_topo 
    
use_standalone_topo = False
if (use_standalone_topo):
    print      ('read_topo_data begin')
    logger.info('read_topo_data begin')
    
    #file_name_temp_ingest = os.path.join(dir_work, 'nam_static.grib2')
    file_name_temp_ingest = os.path.join(dir_work, 'hrrr_static.grib2')
    ds_sfc = xarray.open_dataset(file_name_temp_ingest, engine='cfgrib',
         backend_kwargs={'filter_by_keys': {'typeOfLevel': 'surface'}})
    lon_static_2d = numpy.array(ds_sfc['longitude'])
    # hrrr only
    lon_static_2d = lon_static_2d - 360.0        
    lat_static_2d = numpy.array(ds_sfc['latitude'])
    hgt_static_2d = numpy.array(ds_sfc['orog'])
    hgt_static_2d = hgt_static_2d*3.28084 # m to ft

#index_lon_min = (lon_static_2d > lon_min)
# & (lon_static_2d < lon_max) & (lat_static_2d > lat_min) & (lat_static_2d < lat_max))
# 1005 x 596, static_2d
# numpy.shape(hgt_static_2d)
#hgt_static_2d[mask_all]
#mask_all = ((lon_static_2d > lon_min) & (lon_static_2d < lon_max) & (lat_static_2d > lat_min) & (lat_static_2d < lat_max))
#mask_1 = ((lon_static_2d > lon_min) & (lon_static_2d < lon_max))
#mask_2 = ((lat_static_2d > lat_min) & (lat_static_2d < lat_max))
# 1059x1779, e=0
# 1005x596, e =1
# 49606
#temp1 = numpy.array(hgt_static_2d[mask_all])
#temp2 = hgt_static_2d[mask_1]
#temp3 = hgt_static_2d[mask_2]
#numpy.shape(temp1)
#numpy.shape(temp2)
#numpy.shape(temp3)


temp4 = numpy.argwhere(hgt_static_2d[mask_all])
numpy.shape(temp4)


1005 x 596

lon_2d_temp[ 0,0]
-123.13068
lat_2d_temp[0,0]
22.4848
lon_2d_temp = lon_2d
lat_2d_temp = lat_2d


lon_2d[ 0,0]
122.71953
lat_2d[ 0,0]

[ny_min, nx_min] = [301,100]
lon_2d_temp[ny_min, nx_min]
lat_2d_temp[ny_min, nx_min]


lon_2d_temp[301:303, nx_min]

total_diff_2d = numpy.abs(lon_2d_temp - lon_min) + numpy.abs(lat_2d_temp - lat_min)
[j_loc_temp_min, i_loc_temp_min] = numpy.argwhere(total_diff_2d == numpy.min(total_diff_2d))[0]
total_diff_2d = numpy.abs(lon_2d_temp - lon_max) + numpy.abs(lat_2d_temp - lat_max)
[j_loc_temp_max, i_loc_temp_max] = numpy.argwhere(total_diff_2d == numpy.min(total_diff_2d))[0]

total_diff_2d = numpy.abs(lon_2d - lon_min) + numpy.abs(lat_2d - lat_min)
[j_loc_min, i_loc_min] = numpy.argwhere(total_diff_2d == numpy.min(total_diff_2d))[0]
total_diff_2d = numpy.abs(lon_2d - lon_max) + numpy.abs(lat_2d - lat_max)
[j_loc_max, i_loc_max] = numpy.argwhere(total_diff_2d == numpy.min(total_diff_2d))[0]



lon_2d_temp[j_loc_temp_min, i_loc_temp_min]
lat_2d_temp[j_loc_temp_min, i_loc_temp_min]

lon_2d[j_loc_min, i_loc_min]
lat_2d[j_loc_min, i_loc_min]

# read_topo 
###############################################################################


###############################################################################
# read_model_data

print      ('read_model_data begin')
logger.info('read_model_data begin')

initial_read = False

# hrrr [ny, nx] = [1005, 596]

[lon_min, lon_max, lon_int] = [-124.5, -117.0, 1.0]
[lat_min, lat_max, lat_int] = [  36.0,   42.2, 0.5]

ws10_mod_mean_event   = numpy.full([n_events], numpy.nan, dtype=float)
wsg10_mod_mean_event  = numpy.full([n_events], numpy.nan, dtype=float)
ws10_mod_crit_event   = numpy.full([n_events], numpy.nan, dtype=float)
wsgd10_mod_crit_event = numpy.full([n_events], numpy.nan, dtype=float)
wsgt10_mod_crit_event = numpy.full([n_events], numpy.nan, dtype=float)

#[ny, nx] = [169, 267]
[ny, nx] = [295, 391]
ws10_max_e_2d  = numpy.full([n_events, ny, nx], numpy.nan, dtype=float)
wsg10_max_e_2d = numpy.full([n_events, ny, nx], numpy.nan, dtype=float)


e = 0
for e in range(0, n_events, 1):
    dt_init_utc = init_list[e]
    file_name_read = os.path.join(dir_data_model, 'event_max', 'max_'+event_list[e]+'_model_'+model_name+'_init_'+init_list[e]+'.nc')
    if not os.path.isfile(file_name_read):
        print      ('  no max file found %s %s ' %(model_name, init_list[e]))
        logger.info('  no max file found %s %s ' %(model_name, init_list[e]))
    else:
        ncfile_read  = Dataset(file_name_read,'r') 
        #if not (initial_read):
        lon_2d = numpy.array(ncfile_read.variables['lon_2d'])
        lat_2d = numpy.array(ncfile_read.variables['lat_2d'])
        try:
            hgt_2d = numpy.array(ncfile_read.variables['hgt_2d'])
            hgt_2d = hgt_2d*3.28084 # m to ft            
        except:
            pass
        wsg10_max_2d = numpy.array(ncfile_read.variables['wsg10_max_2d'])
        ws10_max_2d  = numpy.array(ncfile_read.variables[ 'ws10_max_2d'])
        wsg10_max_2d = 2.23694*wsg10_max_2d
        ws10_max_2d  = 2.23694*ws10_max_2d        
        ncfile_read.close()
        print      ('  read file end ') 
        logger.info('  read file end ') 
        #[ny_temp, nx_temp] = numpy.shape(lon_2d)
        # match to static grid - not needed if i use gcp instead 
        #total_diff_2d = numpy.abs(lon_2d - lon_min) + numpy.abs(lat_2d - lat_min)
        #[j_loc_min, i_loc_min] = numpy.argwhere(total_diff_2d == numpy.min(total_diff_2d))[0]
        #total_diff_2d = numpy.abs(lon_2d - lon_max) + numpy.abs(lat_2d - lat_max)
        #[j_loc_max, i_loc_max] = numpy.argwhere(total_diff_2d == numpy.min(total_diff_2d))[0]
        #lon_2d = lon_2d[j_loc_min:j_loc_max, i_loc_min:i_loc_max]
        #lat_2d = lat_2d[j_loc_min:j_loc_max, i_loc_min:i_loc_max]
        #hgt_2d = hgt_2d[j_loc_min:j_loc_max, i_loc_min:i_loc_max]
        #ws10_max_e_2d [e,:,:] =  ws10_max_2d[j_loc_min:j_loc_max, i_loc_min:i_loc_max]
        #wsg10_max_e_2d[e,:,:] = wsg10_max_2d[j_loc_min:j_loc_max, i_loc_min:i_loc_max]
        ws10_max_e_2d [e,:,:] =  ws10_max_2d
        wsg10_max_e_2d[e,:,:] = wsg10_max_2d
        del ws10_max_2d, wsg10_max_2d
    del dt_init_utc, file_name_read
    

#mask_all = ((lon_2d > lon_min) & (lon_2d < lon_max) & (lat_2d > lat_min) & (lat_2d < lat_max))
# mask out ocean
mask_hgt = (hgt_2d < 10.0)
ws10_max_e_2d [:,mask_hgt] = numpy.nan
wsg10_max_e_2d[:,mask_hgt] = numpy.nan

for e in range(0, n_events, 1):
    #mask_ws   = (( ws10_max_2d >=   ws_crit) & (lon_2d > lon_min) & (lon_2d < lon_max) & (lat_2d > lat_min) & (lat_2d < lat_max))
    #mask_wsgd = ((wsg10_max_2d >= wsgd_crit) & (lon_2d > lon_min) & (lon_2d < lon_max) & (lat_2d > lat_min) & (lat_2d < lat_max))
    #mask_wsgt = ((wsg10_max_2d >= wsgt_crit) & (lon_2d > lon_min) & (lon_2d < lon_max) & (lat_2d > lat_min) & (lat_2d < lat_max))    
    mask_ws   = ( ws10_max_e_2d[e,:,:] >=   ws_crit)
    mask_wsgd = (wsg10_max_e_2d[e,:,:] >= wsgd_crit) 
    mask_wsgt = (wsg10_max_e_2d[e,:,:] >= wsgt_crit)
    ws10_mod_mean_event  [e] = numpy.nanmean( ws10_max_e_2d[e,:,:])
    wsg10_mod_mean_event [e] = numpy.nanmean(wsg10_max_e_2d[e,:,:])
    ws10_mod_crit_event  [e] = 100.0*float(len( ws10_max_e_2d[e,  mask_ws]))/float(ny*nx)
    wsgd10_mod_crit_event[e] = 100.0*float(len(wsg10_max_e_2d[e,mask_wsgd]))/float(ny*nx)
    wsgt10_mod_crit_event[e] = 100.0*float(len(wsg10_max_e_2d[e,mask_wsgt]))/float(ny*nx)
    
# reduce all events to 
ws10_crit_composite = numpy.full([ny, nx], numpy.nan, dtype=float)
for j in range(0, ny, 1):    
    for i in range(0, nx, 1):    
        mask_crit = (ws10_max_e_2d[:,j,i] > ws_crit)
        ws10_crit_composite[j,i] = len(ws10_max_e_2d[mask_crit,j,i])
        del mask_crit
    
# read_model_data
###############################################################################


###############################################################################
# reduce stn_obs to mean_per_event, and stns_exceeding criteria per event
# for all stn and for raws only 

ws10_obs_mean_event   = numpy.full([n_events], numpy.nan, dtype=float)
wsg10_obs_mean_event  = numpy.full([n_events], numpy.nan, dtype=float)
ws10_obs_crit_event   = numpy.full([n_events], numpy.nan, dtype=float)
wsgd10_obs_crit_event = numpy.full([n_events], numpy.nan, dtype=float)
wsgt10_obs_crit_event = numpy.full([n_events], numpy.nan, dtype=float)

#mask_raws = (dict_stn_metadata['stn_mnet_id'] == 2)
#dict_stn_metadata['stn_id'][mask_raws]

e = 2
for e in range(0, n_events, 1):
    ws10_obs_mean_event  [e] = numpy.nanmean( ws_max_obs_s_event[:,e])
    wsg10_obs_mean_event [e] = numpy.nanmean(wsg_max_obs_s_event[:,e])
    mask_ws   = ( ws_max_obs_s_event[:,e] >=   ws_crit)
    mask_wsgd = (wsg_max_obs_s_event[:,e] >= wsgd_crit)
    mask_wsgt = (wsg_max_obs_s_event[:,e] >= wsgt_crit)
    mask_ws_not_nan  = ~numpy.isnan( ws_max_obs_s_event[:,e])
    mask_wsg_not_nan = ~numpy.isnan(wsg_max_obs_s_event[:,e])
    ws10_obs_crit_event   [e] = 100.0*float(len( ws_max_obs_s_event[  mask_ws,e]))/float(len(ws_max_obs_s_event[mask_ws_not_nan,e]))
    wsgd10_obs_crit_event [e] = 100.0*float(len(wsg_max_obs_s_event[mask_wsgd,e]))/float(len(ws_max_obs_s_event[mask_ws_not_nan,e]))
    wsgt10_obs_crit_event [e] = 100.0*float(len(wsg_max_obs_s_event[mask_wsgt,e]))/float(len(ws_max_obs_s_event[mask_ws_not_nan,e]))
    del mask_ws, mask_wsgd, mask_wsgt, mask_ws_not_nan, mask_wsg_not_nan

# composite exceedance     
ws_exceedance_composite_obs_s = numpy.full([dict_stn_metadata['n_stn']], numpy.nan, dtype='float') 
for s in range(0, dict_stn_metadata['n_stn'], 1): 
    mask = (ws_max_obs_s_event[s,:] > ws_crit)
    ws_exceedance_composite_obs_s[s] = len(ws_max_obs_s_event[s,mask])
    
# reduce stn_obs to raws only 
###############################################################################


###############################################################################
# plot_control
    

#[wsg_min, wsg_max, wsg_int] = [0.0, 45.0, 5.0]

width_line = 3.0 
size_marker = 10

[ ws_min,  ws_max,  ws_int] = [0, 25, 5] # was 0, 30, 5                                                                
[wsg_min, wsg_max, wsg_int] = [0.0,  81.0,  10.0]
ws_ticks = numpy.arange(ws_min,ws_max+ws_int,ws_int)
wsg_ticks = numpy.arange(wsg_min,wsg_max+wsg_int,wsg_int)

[percent_min, percent_max, percent_int] = [0.0,  45.0,  10.0]
percent_ticks = numpy.arange(percent_min, percent_max+percent_int, percent_int)


size_scatter = 20
color_list = ['r', 'b', 'g', 'c', 'm', 'y']
alpha_level = 0.5

# plot_control
###############################################################################


###############################################################################
# plot_scatter_event_intercomparison

[ ws_min,  ws_max,  ws_int] = [0.0,  65.0,  10.0]
[wsg_min, wsg_max, wsg_int] = [0.0,  85.0,  5.0]
ws_ticks = numpy.arange(ws_min,ws_max+ws_int,ws_int)
wsg_ticks = numpy.arange(wsg_min,wsg_max+wsg_int,wsg_int)

plot_scatter_event_intercomparison = True
if (plot_scatter_event_intercomparison):
    

    ########################################
    # scatter ws obs 
    fig_num = 401 
    fig = plt.figure(num=fig_num,figsize=(11,4)) 
    plt.clf()
    
    plt.subplot(1, 3, 1)
    [e_x, e_y] = [0,1]
    plt.scatter(ws_max_obs_s_event[:,e_x], ws_max_obs_s_event[:,e_y], s=size_scatter, marker='o',color='r', edgecolor='k',alpha=alpha_level)
    for dum in numpy.arange(ws_min, ws_max+ws_int, ws_int):
        plt.plot([ws_min, ws_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
        plt.plot([dum, dum], [ws_min, ws_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    plt.plot([ws_min, ws_max], [ws_min, ws_max], 'k', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
    plt.xticks(ws_ticks, fontsize=14)
    plt.yticks(ws_ticks, fontsize=14)
    plt.xlim([ws_min, ws_max])
    plt.ylim([ws_min, ws_max])
    #plt.xlabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
    #plt.ylabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
    plt.xlabel(event_ticks[e_x], fontsize=14, labelpad=0) # 10 is too small, 20 
    plt.ylabel(event_ticks[e_y], fontsize=14, labelpad=0) # 10 is too small, 20 
    #plt.title('%s vs %s ' % (event_ticks[e_x], event_ticks[e_y]) , \
    #    fontsize=14, loc='left', weight = 'bold')   
        
    plt.subplot(1, 3, 2)
    [e_x, e_y] = [2,3]
    plt.scatter(ws_max_obs_s_event[:,e_x], ws_max_obs_s_event[:,e_y], s=size_scatter, marker='o',color='r', edgecolor='k',alpha=alpha_level)
    for dum in numpy.arange(ws_min, ws_max+ws_int, ws_int):
        plt.plot([ws_min, ws_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
        plt.plot([dum, dum], [ws_min, ws_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    plt.plot([ws_min, ws_max], [ws_min, ws_max], 'k', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
    plt.xticks(ws_ticks, fontsize=14)
    plt.yticks(ws_ticks, fontsize=14, visible=True)
    plt.xlim([ws_min, ws_max])
    plt.ylim([ws_min, ws_max])
    #plt.xlabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
    #plt.ylabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
    plt.xlabel(event_ticks[e_x], fontsize=14, labelpad=0) # 10 is too small, 20 
    plt.ylabel(event_ticks[e_y], fontsize=14, labelpad=0) # 10 is too small, 20 
    #plt.title('%s vs %s ' % (event_ticks[e_x], event_ticks[e_y]) , \
    #    fontsize=14, loc='left', weight = 'bold')   
    plt.title('ws max obs event intercomparison' , \
        fontsize=14, loc='center', weight = 'bold')   

    plt.subplot(1, 3, 3)
    [e_x, e_y] = [4,5]
    plt.scatter(ws_max_obs_s_event[:,e_x], ws_max_obs_s_event[:,e_y], s=size_scatter, marker='o',color='r', edgecolor='k',alpha=alpha_level)
    for dum in numpy.arange(ws_min, ws_max+ws_int, ws_int):
        plt.plot([ws_min, ws_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
        plt.plot([dum, dum], [ws_min, ws_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    plt.plot([ws_min, ws_max], [ws_min, ws_max], 'k', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
    plt.xticks(ws_ticks, fontsize=14)
    plt.yticks(ws_ticks, fontsize=14, visible=True)
    plt.xlim([ws_min, ws_max])
    plt.ylim([ws_min, ws_max])
    #plt.xlabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
    #plt.ylabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
    plt.xlabel(event_ticks[e_x], fontsize=14, labelpad=0) # 10 is too small, 20 
    plt.ylabel(event_ticks[e_y], fontsize=14, labelpad=0) # 10 is too small, 20 
    #plt.title('%s vs %s ' % (event_ticks[e_x], event_ticks[e_y]) , \
    #    fontsize=14, loc='left')   

    plt.show()
    plt.tight_layout()        
    filename = 'scatter_ws_max_obs_x3' 
    plot_name = os.path.join(dir_work, 'figs_event_compare', filename) 
    dpi_level = 400 # 400        
    #plt.savefig(plot_name)
    plt.savefig(plot_name, dpi=dpi_level) 
    #fig.clf()
    #plt.close()        

    ########################################
    # scatter ws hrrr 

    alpha_level = 0.1

    fig_num = 402 
    fig = plt.figure(num=fig_num,figsize=(11,4)) 
    plt.clf()
    
    plt.subplot(1, 3, 1)
    [e_x, e_y] = [0,1]
    plt.scatter(ws10_max_e_2d [e_x,:,:], ws10_max_e_2d [e_y,:,:], s=size_scatter, marker='o',color='r', edgecolor='k',alpha=alpha_level)
    for dum in numpy.arange(ws_min, ws_max+ws_int, ws_int):
        plt.plot([ws_min, ws_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
        plt.plot([dum, dum], [ws_min, ws_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    plt.plot([ws_min, ws_max], [ws_min, ws_max], 'k', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
    plt.xticks(ws_ticks, fontsize=14)
    plt.yticks(ws_ticks, fontsize=14)
    plt.xlim([ws_min, ws_max])
    plt.ylim([ws_min, ws_max])
    #plt.xlabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
    #plt.ylabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
    plt.xlabel(event_ticks[e_x], fontsize=14, labelpad=0) # 10 is too small, 20 
    plt.ylabel(event_ticks[e_y], fontsize=14, labelpad=0) # 10 is too small, 20 
    #plt.title('%s vs %s ' % (event_ticks[e_x], event_ticks[e_y]) , \
    #    fontsize=14, loc='left', weight = 'bold')   
        
    plt.subplot(1, 3, 2)
    [e_x, e_y] = [2,3]
    plt.scatter(ws10_max_e_2d [e_x,:,:], ws10_max_e_2d [e_y,:,:], s=size_scatter, marker='o',color='r', edgecolor='k',alpha=alpha_level)
    for dum in numpy.arange(ws_min, ws_max+ws_int, ws_int):
        plt.plot([ws_min, ws_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
        plt.plot([dum, dum], [ws_min, ws_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    plt.plot([ws_min, ws_max], [ws_min, ws_max], 'k', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
    plt.xticks(ws_ticks, fontsize=14)
    plt.yticks(ws_ticks, fontsize=14, visible=True)
    plt.xlim([ws_min, ws_max])
    plt.ylim([ws_min, ws_max])
    #plt.xlabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
    #plt.ylabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
    plt.xlabel(event_ticks[e_x], fontsize=14, labelpad=0) # 10 is too small, 20 
    plt.ylabel(event_ticks[e_y], fontsize=14, labelpad=0) # 10 is too small, 20 
    #plt.title('%s vs %s ' % (event_ticks[e_x], event_ticks[e_y]) , \
    #    fontsize=14, loc='left', weight = 'bold')   
    plt.title('ws max hrrr event intercomparison' , \
        fontsize=14, loc='center', weight = 'bold')   

    plt.subplot(1, 3, 3)
    [e_x, e_y] = [4,5]
    plt.scatter(ws10_max_e_2d [e_x,:,:], ws10_max_e_2d [e_y,:,:], s=size_scatter, marker='o',color='r', edgecolor='k',alpha=alpha_level)
    for dum in numpy.arange(ws_min, ws_max+ws_int, ws_int):
        plt.plot([ws_min, ws_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
        plt.plot([dum, dum], [ws_min, ws_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    plt.plot([ws_min, ws_max], [ws_min, ws_max], 'k', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
    plt.xticks(ws_ticks, fontsize=14)
    plt.yticks(ws_ticks, fontsize=14, visible=True)
    plt.xlim([ws_min, ws_max])
    plt.ylim([ws_min, ws_max])
    #plt.xlabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
    #plt.ylabel('ws [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
    plt.xlabel(event_ticks[e_x], fontsize=14, labelpad=0) # 10 is too small, 20 
    plt.ylabel(event_ticks[e_y], fontsize=14, labelpad=0) # 10 is too small, 20 
    #plt.title('%s vs %s ' % (event_ticks[e_x], event_ticks[e_y]) , \
    #    fontsize=14, loc='left')   

    plt.show()
    plt.tight_layout()        
    filename = 'scatter_ws_max_obs_x3' 
    plot_name = os.path.join(dir_work, 'figs_event_compare', filename) 
    dpi_level = 400 # 400        
    #plt.savefig(plot_name)
    plt.savefig(plot_name, dpi=dpi_level) 
    #fig.clf()
    #plt.close()        


# plot_scatter_event_intercomparison
###############################################################################

alpha_level = 0.5

bar_width = 0.2

########################################
# bar mean ws
fig_num = 201 
fig = plt.figure(num=fig_num,figsize=(10,5)) 
plt.clf()

plt.bar(event_axis+0.0*bar_width,  ws10_mod_mean_event, color='r', width=bar_width, edgecolor='k', label= 'ws hrrr')
plt.bar(event_axis+1.0*bar_width,  ws10_obs_mean_event, color='b', width=bar_width, edgecolor='k', label= 'ws obs')
#plt.bar(event_axis+2.0*bar_width, wsg10_mod_mean_event, color='g', width=bar_width, edgecolor='k', label='wsg hrrr')
#plt.bar(event_axis+3.0*bar_width, wsg10_obs_mean_event, color='m', width=bar_width, edgecolor='k', label='wsg obs')

plt.legend(loc=2,fontsize=14,ncol=1) 
plt.title('all event mean ws and wsg' , \
     fontsize=14, loc='left')                     
plt.xlabel('event ',fontsize=14,labelpad=0)            
plt.ylabel('ws [mph]',fontsize=14,labelpad=0)            
plt.yticks(numpy.arange(0, 30, 5), fontsize=14)                     
plt.ylim([5, 25])
plt.xlim([-0.2, 4.9])
plt.xticks(numpy.arange(0.5, 6.5, 1.0), event_ticks, fontsize=14) 
plt.show() 
filename = 'ws_mean_bar_all_event.png' 
plot_name = os.path.join(dir_work,'figs_vs_event',filename)
plt.savefig(plot_name) 

########################################
# bar exceedance
fig_num = 202 
fig = plt.figure(num=fig_num,figsize=(10,5)) 
plt.clf()

plt.bar(event_axis+0.0*bar_width,   ws10_mod_crit_event, color='r', width=bar_width, edgecolor='k', label= 'ws hrrr')
plt.bar(event_axis+1.0*bar_width,   ws10_obs_crit_event, color='b', width=bar_width, edgecolor='k', label= 'ws obs')
#plt.bar(event_axis+2.0*bar_width, wsgd10_mod_crit_event, color='g', width=bar_width, edgecolor='k', label='wsg hrrr')
#plt.bar(event_axis+3.0*bar_width, wsgd10_obs_crit_event, color='m', width=bar_width, edgecolor='k', label='wsg obs')

plt.legend(loc=2,fontsize=14,ncol=1) 
plt.title('all event percent exceedance' , \
     fontsize=14, loc='left')                     
plt.xlabel('event ',fontsize=14,labelpad=0)            
plt.ylabel('percent in exceeedance [%]',fontsize=14,labelpad=0)            
#plt.yticks(numpy.arange(wsg_min, wsg_max+wsg_int, wsg_int), fontsize=14)                     
#plt.ylim([wsg_min, wsg_max])
plt.xlim([-0.2, 4.9])
plt.xticks(numpy.arange(0.5, 6.5, 1.0), event_ticks, fontsize=14)                     
plt.show() 
filename = 'ws_exceedance_bar_all_event.png' 
plot_name = os.path.join(dir_work,'figs_vs_event',filename)
plt.savefig(plot_name) 


########################################
# scatter mean ws

size_scatter = 60
alpha_level = 0.8

fig_num = 301 
fig = plt.figure(num=fig_num,figsize=(10,6)) 
plt.clf()

plt.subplot(1, 2, 1)
for e in range(0, n_events, 1):
    plt.scatter(ws10_mod_mean_event[e], ws10_obs_mean_event[e], s=size_scatter, marker='o', color=color_list[e], edgecolor='k', alpha=alpha_level)
for dum in numpy.arange(ws_min, ws_max+ws_int, ws_int):
    plt.plot([ws_min, ws_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
for dum in numpy.arange(ws_min, ws_max+ws_int, ws_int):
    plt.plot([dum, dum], [ws_min, ws_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
plt.xticks(ws_ticks, fontsize=14)                     
plt.yticks(ws_ticks, fontsize=14)                     
plt.xlim([0, ws_max])
plt.ylim([0, ws_max])
plt.xlabel('ws hrrr [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.ylabel('ws obs  [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.title('mean ws (left) and wsg (right) all events hrrr vs obs ' , \
    fontsize=14, loc='left', weight = 'bold')   

plt.subplot(1, 2, 2)
for e in range(0, n_events, 1):
    plt.scatter(wsg10_mod_mean_event[e], wsg10_obs_mean_event[e], s=size_scatter, marker='o', color=color_list[e], edgecolor='k', alpha=alpha_level)
for dum in numpy.arange(wsg_min, wsg_max+wsg_int, wsg_int):
    plt.plot([wsg_min, wsg_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
for dum in numpy.arange(wsg_min, wsg_max+wsg_int, wsg_int):
    plt.plot([dum, dum], [wsg_min, wsg_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
plt.xticks(wsg_ticks, fontsize=14)                     
plt.yticks(wsg_ticks, fontsize=14)                     
plt.xlim([0, wsg_max])
plt.ylim([0, wsg_max])
plt.xlabel('wsg hrrr [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.ylabel('wsg obs  [mph]', fontsize=14, labelpad=0) # 10 is too small, 20 

plt.show() 
filename = 'ws_mean_scatter_all_event.png' 
plot_name = os.path.join(dir_work,'figs_vs_event',filename)
plt.savefig(plot_name) 

########################################
# scatter exceedance
fig_num = 302 
fig = plt.figure(num=fig_num,figsize=(10,6)) 
plt.clf()

plt.subplot(1, 2, 1)
for e in range(0, n_events, 1):
    plt.scatter(ws10_mod_crit_event[e], ws10_obs_crit_event[e], s=size_scatter, marker='o', color=color_list[e], edgecolor='k', alpha=alpha_level)
for dum in numpy.arange(percent_min, percent_max+percent_int, percent_int):
    plt.plot([percent_min, percent_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
for dum in numpy.arange(percent_min, percent_max+percent_int, percent_int):
    plt.plot([dum, dum], [percent_min, percent_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
plt.xticks(percent_ticks, fontsize=14)                     
plt.yticks(percent_ticks, fontsize=14)                     
plt.xlim([0, percent_max])
plt.ylim([0, percent_max])
plt.xlabel('% hrrr ', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.ylabel('% obs ', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.title('percent exceedance ws (left) and wsg (right) all events hrrr vs obs ' , \
    fontsize=14, loc='left', weight = 'bold')   

plt.subplot(1, 2, 2)
for e in range(0, n_events, 1):
    plt.scatter(wsgd10_mod_crit_event[e], wsgd10_obs_crit_event[e], s=size_scatter, marker='o', color=color_list[e], edgecolor='k', alpha=alpha_level)
for dum in numpy.arange(percent_min, percent_max+percent_int, percent_int):
    plt.plot([percent_min, percent_max], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
for dum in numpy.arange(percent_min, percent_max+percent_int, percent_int):
    plt.plot([dum, dum], [percent_min, percent_max], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
plt.xticks(percent_ticks, fontsize=14)                     
plt.yticks(percent_ticks, fontsize=14)                     
plt.xlim([0, percent_max])
plt.ylim([0, percent_max])
plt.xlabel('% hrrr ', fontsize=14, labelpad=0) # 10 is too small, 20 
plt.ylabel('% obs ',  fontsize=14, labelpad=0) # 10 is too small, 20 

plt.show() 
filename = 'ws_exceedance_scatter_all_event.png' 
plot_name = os.path.join(dir_work,'figs_vs_event',filename)
plt.savefig(plot_name) 

# plots 
###############################################################################


plot_counties = False

country_provinces = cfeature.NaturalEarthFeature(category='cultural',
                                                 name='admin_0_boundary_lines_land',
                                                 scale='50m',
                                                 facecolor='none')
states_provinces = cfeature.NaturalEarthFeature(category='cultural',
                                                name='admin_1_states_provinces_lines',
                                                scale='50m',
                                                facecolor='none')



plot_area = ['nor_ca', 'nor_bay', 'nor_sierra','bay', 'cen_sierra', 'nor_valley', 'nor_coast']
n_areas = len(plot_area)

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

[crit_min, crit_max, crit_int] = [0, 6, 1]
crit_ticks = numpy.arange(crit_min, crit_max, crit_int)
n_cmap_crit = len(crit_ticks)
cmap_crit  = plt.get_cmap('afmhot_r', n_cmap_crit) 
plot_ws_obs_composite = False


###############################################################################
# plot exceedance maps 

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
    width_roads = 2.0
    if (area_temp == 'nor_ca'):
        width_roads = 0.5
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
        
    fig = plt.figure(num=112,figsize=(figsize_x, figsize_y)) # 10x5, 10x6, 10x10 
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

    #hgt_lines = plt.contour (lon_static_2d, lat_static_2d, hgt_static_2d, levels=numpy.arange(hgt_min, hgt_max, hgt_int), colors='gray', linestyles='solid', linewidths=0.5)
    hgt_lines = plt.contour (lon_2d, lat_2d, hgt_2d, levels=numpy.arange(hgt_min, hgt_max, hgt_int), colors='gray', linestyles='solid', linewidths=0.5)
    im = plt.contourf(lon_2d, lat_2d, ws10_crit_composite, numpy.arange(crit_min, crit_max, crit_int), cmap=cmap_crit, transform=ccrs.PlateCarree()) # jet, viridis 
    im.set_clim(crit_min, crit_max) 
    cbar = fig.colorbar(im, shrink=0.6) # was 0.7 0.8
    cbar.set_label('# of events',fontsize=12,labelpad=00)                                

    if (plot_ws_obs_composite):
        # plot sfc obs
        alpha_level = 1.0 # 0.3
        s = 358
        for s in range(0, dict_stn_metadata['n_stn'], 1):
            #ax.plot(dict_stn_metadata['stn_lon'][s], dict_stn_metadata['stn_lat'][s], marker='o', markersize=size_marker, markerfacecolor='w', markeredgecolor='k', transform=ccrs.PlateCarree())
         
            #if (hit_diablo_event_sum_per_year_s[s] > hit_diablo_map_plot_min): # 0.2
            if not numpy.isnan(ws_exceedance_composite_obs_s[s]):
                marker_edge_color = 'k'
                marker_edge_width = 1.0 # 0.5 # 1.0
                #if (ws_exceedance_composite_obs_s[s] >= 2):
                #    marker_edge_color = 'r'
                #    marker_edge_width = 2.0 # 0.5 # 2.0
                #else:
                #    marker_edge_color = 'k'
                #    marker_edge_width = 1.0 # 0.5 # 1.0
                     
                frac_temp = (ws_exceedance_composite_obs_s[s] - crit_min)/(crit_max - crit_min)
                index_cmap_temp = int(round(n_cmap_crit*frac_temp,0))
                if (index_cmap_temp >= n_cmap_crit): 
                    index_cmap_temp = n_cmap_crit - 1 
                color_temp = cmap_crit(index_cmap_temp)
                ax.plot(dict_stn_metadata['stn_lon'][s], dict_stn_metadata['stn_lat'][s], marker='o', markersize=size_marker, markerfacecolor=color_temp, markeredgecolor=marker_edge_color, markeredgewidth=marker_edge_width, alpha=alpha_level, transform=ccrs.PlateCarree())
                del frac_temp, index_cmap_temp, color_temp          
    
    plt.xlabel('longitude', fontsize=12, labelpad=10) # 10 is too small, 20 
    plt.ylabel('latitude',  fontsize=12, labelpad=10) # 30 is too small, 60 
    plt.title('events exceeding criteria %s ' % (model_name) , \
        fontsize=12, loc='left', weight = 'bold')   
    plt.show()
    plt.tight_layout()        
    filename = 'ws_crit_exceedance_%s_%s.png' % (area_temp, model_name)
    plot_name = os.path.join(dir_work, 'figs_ws_max_maps', filename) 
    dpi_level = 400 # 400        
    #plt.savefig(plot_name)
    plt.savefig(plot_name, dpi=dpi_level) 
    #fig.clf()
    #plt.close()        
    
    
    [e1, e2] = [0, 1]
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

    #hgt_lines = plt.contour (lon_static_2d, lat_static_2d, hgt_static_2d, levels=numpy.arange(hgt_min, hgt_max, hgt_int), colors='gray', linestyles='solid', linewidths=0.5)
    hgt_lines = plt.contour (lon_2d, lat_2d, hgt_2d, levels=numpy.arange(hgt_min, hgt_max, hgt_int), colors='gray', linestyles='solid', linewidths=0.5)
    #im = plt.contourf(lon_2d, lat_2d, ws10_max_e_2d[0,:,:], numpy.arange(ws_min, ws_max, ws_int), cmap=cmap_ws, transform=ccrs.PlateCarree()) # jet, viridis 
    #for e in range(0, n_events, 1):
    #    plt.contour(lon_2d, lat_2d, ws10_max_e_2d[e,:,:], levels = [ws_crit], colors=color_list[e], linestyles='solid',linewidths=2)
    plt.contour(lon_2d, lat_2d, ws10_max_e_2d[e1,:,:], levels = [ws_crit], colors='r', linestyles='solid',linewidths=2)
    plt.contour(lon_2d, lat_2d, ws10_max_e_2d[e2,:,:], levels = [ws_crit], colors='b', linestyles='solid',linewidths=2)
    #im.set_clim(ws_min, ws_max) 
    #cbar = fig.colorbar(im, shrink=0.6) # was 0.7 0.8
    #cbar = fig.colorbar(im)
    #cbar.set_label('ws [mph]',fontsize=12,labelpad=00)                                

    plt.xlabel('longitude', fontsize=12, labelpad=10) # 10 is too small, 20 
    plt.ylabel('latitude',  fontsize=12, labelpad=10) # 30 is too small, 60 
    plt.title('ws max exceedance %s \n%s (r) and %s (b)  ' % (model_name, event_ticks[e1], event_ticks[e2]) , \
        fontsize=12, loc='left', weight = 'bold')   
    plt.show()
    plt.tight_layout()        
    filename = 'ws_max_exceedance_%s_%s_%s_vs_%s.png' % (area_temp, model_name, event_list[e1], event_list[e2])
    plot_name = os.path.join(dir_work, 'figs_ws_max_maps', filename) 
    dpi_level = 400 # 400        
    #plt.savefig(plot_name)
    plt.savefig(plot_name, dpi=dpi_level) 
    #fig.clf()
    #plt.close()        


    [e1, e2] = [2, 3]
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

    #hgt_lines = plt.contour (lon_static_2d, lat_static_2d, hgt_static_2d, levels=numpy.arange(hgt_min, hgt_max, hgt_int), colors='gray', linestyles='solid', linewidths=0.5)
    hgt_lines = plt.contour (lon_2d, lat_2d, hgt_2d, levels=numpy.arange(hgt_min, hgt_max, hgt_int), colors='gray', linestyles='solid', linewidths=0.5)
    #im = plt.contourf(lon_2d, lat_2d, ws10_max_e_2d[0,:,:], numpy.arange(ws_min, ws_max, ws_int), cmap=cmap_ws, transform=ccrs.PlateCarree()) # jet, viridis 
    #for e in range(0, n_events, 1):
    #    plt.contour(lon_2d, lat_2d, ws10_max_e_2d[e,:,:], levels = [ws_crit], colors=color_list[e], linestyles='solid',linewidths=2)
    plt.contour(lon_2d, lat_2d, ws10_max_e_2d[e1,:,:], levels = [ws_crit], colors='r', linestyles='solid',linewidths=2)
    plt.contour(lon_2d, lat_2d, ws10_max_e_2d[e2,:,:], levels = [ws_crit], colors='b', linestyles='solid',linewidths=2)
    #im.set_clim(ws_min, ws_max) 
    #cbar = fig.colorbar(im, shrink=0.6) # was 0.7 0.8
    #cbar = fig.colorbar(im)
    #cbar.set_label('ws [mph]',fontsize=12,labelpad=00)                                

    plt.xlabel('longitude', fontsize=12, labelpad=10) # 10 is too small, 20 
    plt.ylabel('latitude',  fontsize=12, labelpad=10) # 30 is too small, 60 
    plt.title('ws max exceedance %s \n%s (r) and %s (b)  ' % (model_name, event_ticks[e1], event_ticks[e2]) , \
        fontsize=12, loc='left', weight = 'bold')   
    plt.show()
    plt.tight_layout()        
    filename = 'ws_max_exceedance_%s_%s_%s_vs_%s.png' % (area_temp, model_name, event_list[e1], event_list[e2])
    plot_name = os.path.join(dir_work, 'figs_ws_max_maps', filename) 
    dpi_level = 400 # 400        
    #plt.savefig(plot_name)
    plt.savefig(plot_name, dpi=dpi_level) 
    #fig.clf()
    #plt.close()        

# plot exceedance maps 
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
