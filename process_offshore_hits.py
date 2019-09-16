
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
    dir_scripts = os.path.join(dir_base, 'offshore_winds')
sys.path.append(os.path.join(dir_scripts)
#sys.path.append(os.path.join(dir_python_scripts,'function_library'))
from define_daylight_savings_or_not   import define_daylight_savings_or_not
from instantiate_logger               import instantiate_logger


from function_library import instantiate_logger 
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

ws_min = 5.0
rh_max = 20.0
[wd_min, wd_max] = [1.0, 100.0]

# set flags and options
###############################################################################


###############################################################################
# instantiate logger 


# instantiate logger 
###############################################################################


###############################################################################
# define datetime_axis 

utc_converstion = 8
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

    [ny_era, nx_era] = [100, 100] # need to know a-priori    
    file_name_base = 'era5_canv_'
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
# plot_time_series
# Plot time series at Hawkeye and Duncan for historical events

plot_time_series = False
if (plot_time_series):


# 
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








