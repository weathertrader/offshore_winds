
from me - grab csv of station data from diablo_stations.csv 

from john want
wd, in addition to ws, or u_ws and v_ws
rh, instead of t2 and td2


###############################################################################
# process_offshore_hits.py
# purpose: compute offshore wind events days in No CA 
# author: Craig Smith 
# version history 
#   2019/09/15 - original 
# usage:  
#   - 
# notes:
#   - 
# to do: 
# - 
#
###############################################################################


###############################################################################
# module import and set paths

host_name = 'chromebook_csmith' 

import os 
from datetime import datetime as dt
from datetime import timedelta as td
import time 
import numpy 
import glob
import pandas 
import sys 
from netCDF4 import Dataset 


import matplotlib
#if (run_mode == 'cron'): 
#    matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from matplotlib.dates import drange, DateFormatter
from matplotlib.ticker import MultipleLocator 

import matplotlib.ticker as mticker
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
import cartopy.feature as cfeature
from cartopy.io import shapereader
from cartopy.feature import ShapelyFeature
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

if (host_name == 'chromebook_csmith'):
    dir_base = '/home/craigmatthewsmith'
    dir_data    = os.path.join(dir_base, 'data/era5')
    dir_scripts = os.path.join(dir_base, 'offshore_winds', 'offshore_winds')

dir_work = dir_scripts
os.chdir(dir_scripts)
    
sys.path.append(os.path.join(dir_scripts))
sys.path.append(os.path.join(dir_base, 'scripts' ,'function_library'))
from define_daylight_savings_or_not   import define_daylight_savings_or_not
from instantiate_logger               import instantiate_logger
from define_datetime_axis import define_datetime_axis
from read_stn_metadata_from_csv import read_stn_metadata_from_csv
from map_stn_locations_to_grid_locations import map_stn_locations_to_grid_locations

#from function_library import instantiate_logger 
#from function_library import email_job_results 
#from function_library import define_daylight_savings_or_not
#from function_library import parse_firms_command_line_options
#from function_library import datetime_round_down_to_start_of_day
#from function_library import decompose_datetime_list
#from function_library import read_firms_data

#from function_library import read_wrf_profile_during_run
#from function_library import read_sfc_obs_mesowest_api
#from function_library import read_stn_metadata 
#from function_library import datematch_two_timeseries 
#from function_library import datematch_two_timeseries_multidimensional
#from function_library import convert_vel_to_dir
#from function_library import decompose_datetime_list
#from function_library import calc_skill

# module import and set paths
###############################################################################


###############################################################################
# set flags and options

ws_offshore_min = 5.0
rh_offshore_max = 20.0
[wd_offshore_min, wd_offshore_max] = [0.0, 135.0]
utc_conversion = 8

# set flags and options
###############################################################################


###############################################################################
# define starting time 

print      ('define_cron_start_time ') 
dt_cron_start_utc = dt.utcnow()    
dt_cron_start_lt = dt.now() # cluster time is LST 
          

# define starting time 
###############################################################################

location = 'diablo'


###############################################################################
# instantiate logger 


log_file_name = 'log_diablo_plot_obs_stn_times_series_%s_%s.txt' % (location, dt_cron_start_lt.strftime('%Y-%m-%d_%H-%M')) 
dir_logs = os.path.join(dir_work, 'archive_logs')
if not os.path.isdir(dir_logs):
    os.system('mkdir -p '+dir_logs)
log_name = os.path.join(dir_work,'archive_logs',log_file_name) 
logger = instantiate_logger(log_name, dt_cron_start_lt) 

# instantiate logger 
###############################################################################

# instantiate logger 
###############################################################################




###############################################################################
# plot_time_series
# plot time series at Hawkeye and Duncan for historical events

plot_time_series = True
if (plot_time_series):

    file_name_base = 'era5_canv_'
    #yy_new = 2011    
    #yy_new = 2013    
    #yy_new = 2017    
    yy_new = 2018    
    file_name_tair = os.path.join(dir_data, file_name_base+'tair_'+str(yy_new)+'.nc')
    file_name_tdew = os.path.join(dir_data, file_name_base+'tdew_'+str(yy_new)+'.nc')
    file_name_ws   = os.path.join(dir_data, file_name_base+'vs_'+str(yy_new)+'.nc')
    file_name_wd   = os.path.join(dir_data, file_name_base+'th_'+str(yy_new)+'.nc')
    
    ncfile_read  = Dataset(file_name_wd,'r') 
    ncfile_read.variables
    wd10_hr_2d = numpy.array(ncfile_read['wind_from_direction'])
    ncfile_read.close()
    
    ncfile_read  = Dataset(file_name_tair,'r') 
    ncfile_read.variables
    t2_hr_k_2d = numpy.array(ncfile_read['air_temperature'])
    t2_hr_2d  =  t2_hr_k_2d - 273.0
    del t2_hr_k_2d
    ncfile_read.close()
    
    ncfile_read  = Dataset(file_name_tdew,'r') 
    ncfile_read.variables
    td2_hr_k_2d = numpy.array(ncfile_read['dewpooint_temperature'])
    td2_hr_2d = td2_hr_k_2d - 273.0
    del td2_hr_k_2d
    ncfile_read.close()
    
    ncfile_read  = Dataset(file_name_ws,'r') 
    # ncfile_read.variables
    ws10_hr_2d = numpy.array(ncfile_read['wind_speed'])
    # numpy.shape(ws_hr_2d)

    lon_1d = numpy.array(ncfile_read['lon'])
    lat_1d = numpy.array(ncfile_read['lat'])
    numpy.shape(lat_1d)
    [lon_2d, lat_2d] = numpy.meshgrid(lon_1d, lat_1d)
    del lon_1d, lat_1d
    
    hr_read = numpy.array(ncfile_read['day'])
    numpy.shape(hr_read)
    hr_read = hr_read - hr_read[0]
    n_hrs = len(hr_read)
    dt_hr_utc = numpy.full([n_hrs], numpy.nan, dtype=object)
    dt_hr_utc[0] = dt(yy_new, 1, 1, 0, 0, 0)
    for hr in range(0, n_hrs, 1):
        dt_hr_utc[hr] = dt_hr_utc[0] + td(hours=hr)
    dt_hr_pst = dt_hr_utc - td(utc_conversion)
        
    ncfile_read.close()
    
    # compute rh
    es_hr_2d = 6.11*10.0**((7.5* t2_hr_2d)/(237.7+ t2_hr_2d))
    e_hr_2d  = 6.11*10.0**((7.5*td2_hr_2d)/(237.7+td2_hr_2d))
    rh2_hr_2d = 100.0*(e_hr_2d/es_hr_2d)
    del es_hr_2d, e_hr_2d

    
    
    #########################################
    # read station locations, Duncan, Jarbo, Knoxville, Hawkeye
    print_stn_info = True
    #use_stn = '85, 87, 92, 103, 112, 117, 142, 189, 200, 224, 233, 240, 242, 243, 265, 286, 293, 302, 330, 356, 378' 
    use_stn = '87, 92, 233, 243' 
    (dict_stn_metadata) = read_stn_metadata_from_csv(dir_work, location, use_stn, print_stn_info) 
    # map station locations to grid indices
    print_flag = True
    (j_loc_s, i_loc_s) = map_stn_locations_to_grid_locations(logger, dict_stn_metadata, lon_2d, lat_2d, print_flag)

    ws10_hr_s = ws10_hr_2d[:,i_loc_s,j_loc_s]
    wd10_hr_s = wd10_hr_2d[:,i_loc_s,j_loc_s]
    rh2_hr_s  = rh2_hr_2d [:,i_loc_s,j_loc_s]
    #ws10_hr_s = ws10_hr_2d[:,j_loc_s,i_loc_s]
    #wd10_hr_s = wd10_hr_2d[:,j_loc_s,i_loc_s]
    #rh2_hr_s  = rh2_hr_2d [:,j_loc_s,i_loc_s]
    
    



    #dt_min_plot = dt(2011, 11, 25)
    #dt_max_plot = dt(2011, 12,  6)
    #dt_min_plot = dt(2013, 11, 20)
    #dt_max_plot = dt(2013, 11, 30)
    #dt_min_plot = dt(2017, 10, 6)
    #dt_max_plot = dt(2017, 10, 13)
    dt_min_plot = dt(2018, 11, 1)
    dt_max_plot = dt(2018, 11, 15)
    
    
    n_days_temp = (dt_max_plot - dt_min_plot).days 
    
    delta = td(hours=24)
    delta_lines = td(hours=24)
    
    datetick_format = '%m/%d %H'    
    #datetick_format = '%H'    
    #if (date_temp.hour  == 0):
    date_ticks = drange(dt_min_plot-td(hours=12), dt_max_plot+delta, delta)
    #elif(date_temp.hour == 12): 
    #date_ticks = drange(dt_min_plot, dt_max_plot+delta, delta)
    n_date_ticks = len(date_ticks) 
    
    #index_min = (dt_axis_master_hr_pst <= dt_min_plot).argmin()-1
    #index_max = (dt_axis_master_hr_pst <= dt_max_plot).argmin()
    index_min = (dt_hr_pst <= dt_min_plot-td(days=1)).argmin()-1
    index_max = (dt_hr_pst <= dt_max_plot+td(days=1)).argmin()
       
    
    ########################################
    # nightime shading 
    
    # make 00z LST darker than the rest 
    yy_temp = dt.strftime(dt_min_plot-td(days=1),'%Y')
    mo_temp = dt.strftime(dt_min_plot-td(days=1),'%m')
    dd_temp = dt.strftime(dt_min_plot-td(days=1),'%d')
    dt_min_00_lt = dt(int(yy_temp), int(mo_temp), int(dd_temp), 00, 00)
              
    # shading nighttime 
    yy_temp = dt.strftime(dt_min_plot-td(days=1),'%Y')
    mo_temp = dt.strftime(dt_min_plot-td(days=1),'%m')
    dd_temp = dt.strftime(dt_min_plot-td(days=1),'%d')
    dt_min_19_lt = dt(int(yy_temp), int(mo_temp), int(dd_temp), 18, 00)
    alpha_night = 0.5
    
    
    size_marker = 0
    
    [ws_min, ws_max, ws_int] = [0.0, 10.0, 2.0]
    [wd_min, wd_max, wd_int] = [0.0, 360.0, 90.0]
    [rh_min, rh_max, rh_int] = [0.0, 100.0, 20.0]
    ws_units_label = 'ms-1'
    
    colors_s = ['r', 'b', 'g', 'c']
    
    ##############################################
    # ws bay, ws sierra, rh bay rh sierra all stns  
    fig_num = 151
    fig = plt.figure(num=fig_num,figsize=(10,7)) # 10,10 
    plt.clf()
    
    #########################################
    # ws 
    plt.subplot(3, 1, 1)
    
    size_marker = 0
    s = 0
    for s in range(0, dict_stn_metadata['n_stn'], 1): 
        plt.plot(dt_hr_pst[index_min:index_max], ws10_hr_s[index_min:index_max,s], color=colors_s[s], linestyle='-', linewidth=2.0, marker='o', markersize=size_marker, markeredgecolor='k', label=dict_stn_metadata['stn_name'][s])
        #plt.plot(dt_hr_pst, ws10_hr_s[:,s], color=colors_s[s], linestyle='-', linewidth=2.0, marker='o', markersize=size_marker, markeredgecolor='k', label=dict_stn_metadata['stn_name'][s])
    
    for dum in numpy.arange(ws_min, ws_max+ws_int, ws_int):
        plt.plot([dt_min_plot-td(hours=24), dt_max_plot+td(hours=24)], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    for dum in matplotlib.dates.drange(dt_min_plot, dt_max_plot+4*delta_lines, delta_lines):
        plt.plot([dum, dum], [-50, 150], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    for dum in range(0, n_days_temp+3, 1):
        plt.plot([dt_min_00_lt+dum*td(hours=24), dt_min_00_lt+dum*td(hours=24)], [-50, 150], 'gray', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
    # add shading for nighttime
    for dum in range(0, n_days_temp+3, 1):
        plt.axvspan(dt_min_19_lt+dum*td(hours=24), dt_min_19_lt+dum*td(hours=24)+td(hours=12), color='grey', alpha=alpha_night, linewidth=0)    
    plt.plot([dt_min_plot-td(hours=24), dt_max_plot+td(hours=24)], [ws_offshore_min, ws_offshore_min], 'k', linestyle='-', linewidth=1.0, marker='o', markersize=0) 
    
    plt.legend(loc=2,fontsize=10,ncol=1) 
    plt.title('ws, wd, rh %s %s ' % (dt_min_plot.strftime('%Y-%m-%d'), dt_max_plot.strftime('%Y-%m-%d')), \
         fontsize=12, x=0.5, y=1.01)                     
    #plt.xlabel('date [PST]',fontsize=12,labelpad=00)
    plt.ylabel('ws ['+ws_units_label+']',fontsize=12,labelpad=10)
    plt.yticks(numpy.arange(ws_min, ws_max+ws_int, ws_int))
    plt.ylim([ws_min, ws_max])
    plt.xlim([date_ticks[0], date_ticks[-1]])
    plt.gca().xaxis.set_major_formatter(DateFormatter(datetick_format))
    #plt.xticks(date_ticks,visible=True) 
    plt.xticks(date_ticks,visible=False) 
     
    #########################################
    # wd 
    plt.subplot(3, 1, 2)  
    
    size_marker = 4 # 2, 6
    s = 0
    for s in range(0, dict_stn_metadata['n_stn'], 1): 
        plt.plot(dt_hr_pst[index_min:index_max], wd10_hr_s[index_min:index_max,s], color=colors_s[s], linestyle='-', linewidth=0.0, marker='o', markersize=size_marker, markeredgecolor='k', label=dict_stn_metadata['stn_name'][s])
    
    for dum in numpy.arange(wd_min, wd_max+wd_int, wd_int):
        plt.plot([dt_min_plot-td(hours=24), dt_max_plot+td(hours=24)], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    for dum in matplotlib.dates.drange(dt_min_plot, dt_max_plot+4*delta_lines, delta_lines):
        plt.plot([dum, dum], [0, 360], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    for dum in range(0, n_days_temp+3, 1):
        plt.plot([dt_min_00_lt+dum*td(hours=24), dt_min_00_lt+dum*td(hours=24)], [0, 360], 'gray', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
    # add shading for nighttime
    for dum in range(0, n_days_temp+3, 1):
        plt.axvspan(dt_min_19_lt+dum*td(hours=24), dt_min_19_lt+dum*td(hours=24)+td(hours=12), color='grey', alpha=alpha_night, linewidth=0)    
    plt.plot([dt_min_plot-td(hours=24), dt_max_plot+td(hours=24)], [wd_offshore_min, wd_offshore_min], 'k', linestyle='-', linewidth=1.0, marker='o', markersize=0) 
    plt.plot([dt_min_plot-td(hours=24), dt_max_plot+td(hours=24)], [wd_offshore_max, wd_offshore_max], 'k', linestyle='-', linewidth=1.0, marker='o', markersize=0) 
    
    
    plt.ylabel('wd [^o]',fontsize=12,labelpad=10)
    plt.yticks(numpy.arange(wd_min, wd_max+wd_int, wd_int))
    plt.ylim([wd_min, wd_max])
    plt.xlim([date_ticks[0], date_ticks[-1]])
    plt.gca().xaxis.set_major_formatter(DateFormatter(datetick_format))
    plt.xticks(date_ticks,visible=False) 
    
    #########################################
    # rh
    plt.subplot(3, 1, 3)  
    
    size_marker = 0
    s = 0
    for s in range(0, dict_stn_metadata['n_stn'], 1): 
        plt.plot(dt_hr_pst[index_min:index_max], rh2_hr_s[index_min:index_max,s], color=colors_s[s], linestyle='-', linewidth=2.0, marker='o', markersize=size_marker, markeredgecolor='k', label=dict_stn_metadata['stn_name'][s])
    
    for dum in numpy.arange(rh_min, rh_max+rh_int, rh_int):
        plt.plot([dt_min_plot-td(hours=24), dt_max_plot+td(hours=24)], [dum, dum], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    for dum in matplotlib.dates.drange(dt_min_plot, dt_max_plot+4*delta_lines, delta_lines):
        plt.plot([dum, dum], [0, 360], 'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    for dum in range(0, n_days_temp+3, 1):
        plt.plot([dt_min_00_lt+dum*td(hours=24), dt_min_00_lt+dum*td(hours=24)], [0, 360], 'gray', linestyle='-', linewidth=2.0, marker='o', markersize=0) 
    # add shading for nighttime
    for dum in range(0, n_days_temp+3, 1):
        plt.axvspan(dt_min_19_lt+dum*td(hours=24), dt_min_19_lt+dum*td(hours=24)+td(hours=12), color='grey', alpha=alpha_night, linewidth=0)    
    plt.plot([dt_min_plot-td(hours=24), dt_max_plot+td(hours=24)], [rh_offshore_max, rh_offshore_max], 'k', linestyle='-', linewidth=1.0, marker='o', markersize=0) 
    
    plt.ylabel('rh [%]',fontsize=12,labelpad=10)
    plt.yticks(numpy.arange(rh_min, rh_max+rh_int, rh_int))
    plt.ylim([rh_min, rh_max])
    plt.xlim([date_ticks[0], date_ticks[-1]])
    plt.gca().xaxis.set_major_formatter(DateFormatter(datetick_format))
    plt.xticks(date_ticks,visible=True) 
    
    plt.show() 
    filename = 'time_series_era5_'+dt_min_plot.strftime('%Y-%m-%d')+'.png' 
    plot_name = os.path.join(dir_work,'figs',filename)
    plt.savefig(plot_name) 
    #plt.close()
 



# ('crs', <class 'netCDF4._netCDF4.Variable'>
#  uint16 crs(crs)
#  grid_mapping_name: latitude_longitude
#  longitude_of_prime_meridian: 0.0
#  semi_major_axis: 6378137.0
#  long_name: WGS 84
#  inverse_flattening: 298.257223563
#  spatial_ref: GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]
#  unlimited dimensions: 
#  current shape = (1,)
#  filling on, default _FillValue of 65535 used),


# read station locations

# maps station location to grid_indices

# extract time series at grid locations 




# 
###############################################################################




###############################################################################
# define datetime_axis 

dt_start = dt(1979, 1, 1)
dt_end   = dt(2019, 1, 1)
interval_string = '1d'
(dt_axis_day_pst, n_days) = define_datetime_axis(logger, dt_start, dt_end, '1d')

# define datetime_axis 
###############################################################################





###############################################################################
# read shapefile polygons and define area masks 


# read shapefile polygons and define area masks 
###############################################################################



###############################################################################
# process_daily_hits_from_grids

process_daily_hits_from_grids = True
if (process_daily_hits_from_grids):

    file_name_base = 'era5_canv_'

    [ny_era, nx_era] = [100, 100] # need to know a-priori    
    yy_old = 1978
    for d in range(0, n_days, 1):
        dt_temp_pst = dt_axis_day_pst[d]
        print      ('  processing d %s %s ' % (str(d).rjust(4,'0', dt_axis_day_pst[d].strftime('%Y-%m-%d'))) 
        ws_era5_day_2d   = numpy.float([24, ny_era, nx_era], numpy.nan, dtype=float)
        wd_era5_day_2d   = numpy.float([24, ny_era, nx_era], numpy.nan, dtype=float)
        rh_era5_day_2d   = numpy.float([24, ny_era, nx_era], numpy.nan, dtype=float)
        hits_era5_day_2d = numpy.float([24, ny_era, nx_era], numpy.nan, dtype=float)
        ws_era5_sum_hits_2d = numpy.float([ny_era, nx_era], numpy.nan, dtype=float)
        wd_era5_sum_hits_2d = numpy.float([ny_era, nx_era], numpy.nan, dtype=float)
        rh_era5_sum_hits_2d = numpy.float([ny_era, nx_era], numpy.nan, dtype=float)
        for hr in range(0, 24, 1):
            dt_temp_utc = dt_temp_pst - td(hours=utc_conversion) + td(hours=hr)
            yy_new = dt_temp_utc.year 
            if (yy_new > yy_old): # increment to next year and read new data 
                file_name_tair = os.path.join(dir_data, file_name_base+'tair_'+str(yy_new)+'.nc')
                file_name_tdew = os.path.join(dir_data, file_name_base+'tdew_'+str(yy_new)+'.nc')
                file_name_ws   = os.path.join(dir_data, file_name_base+'vs_'+str(yy_new)+'.nc')
                if not((os.path.isfile(file_name_tair) and (os.path.isfile(file_name_tdew) (os.path.isfile(file_name_ws))):
                    print('ERROR: misssing file')

read_new_data        
era5_canv_tair_2013.nc  era5_canv_tdew_2013.nc  era5_canv_vs_2013.nc        
Read single


for j in range(0, ny_era, 1):
    for i in range(0, nx_era, 1):

        
for hr in range(0, 24, 1):
    mask = ws_era5_day_2d[:,j,i]
        
        if (ws_era5_day_2d[hr,j,i], numpy.nan, dtype=float)
        )
hits_era5_day_2d[hr,j,i]        
        
Read full day in PST
And define hits - ws, wd, rh 
Aggregate to daily (>3hrs hit)
Calc hits per cell
Write # of cells hit per day to a single day text file
Loop over all 


# process by day 
###############################################################################


###############################################################################
# aggregate_all_daily_hits
Aggregate all txt files to a single csv, write and read  


aggregate_all_daily_hits = True
if (aggregate_all_daily_hits):
    
    

    
    
# 
###############################################################################


###############################################################################
# read daily hits 


# 
###############################################################################


###############################################################################
# plot_daily_hits 
plot_daily_hits = False
if(plot_daily_hits):

# 
###############################################################################








