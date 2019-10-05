
###############################################################################
# download_dfm_from_daymet.py 
# purpose: download dfm data from daymet 
# author: Craig Smith 
# version history 
#   2019/09/30 - original 
# usage:  
#   cli 
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
import urllib.request
#import subprocess 

if (host_name == 'chromebook_csmith'):
    dir_base = '/home/craigmatthewsmith'
    dir_data    = os.path.join(dir_base, 'data/daymet')
    dir_scripts = os.path.join(dir_base, 'offshore_winds', 'offshore_winds')

dir_work = dir_data
os.chdir(dir_data)
    
sys.path.append(os.path.join(dir_scripts))
#sys.path.append(os.path.join(dir_base, 'scripts' ,'function_library'))
from define_daylight_savings_or_not   import define_daylight_savings_or_not
from instantiate_logger               import instantiate_logger
from define_datetime_axis import define_datetime_axis
#from read_stn_metadata_from_csv import read_stn_metadata_from_csv
#from map_stn_locations_to_grid_locations import map_stn_locations_to_grid_locations

# module import and set paths
###############################################################################


###############################################################################
# define starting time 

print      ('define_cron_start_time ') 
dt_cron_start_utc = dt.utcnow()    
dt_cron_start_lt = dt.now() # cluster time is LST 
          
# define starting time 
###############################################################################


###############################################################################
# instantiate logger 

log_file_name = 'log_download_daymet_%s.txt' % (dt_cron_start_lt.strftime('%Y-%m-%d_%H-%M')) 
dir_logs = os.path.join(dir_work, 'archive_logs')
if not os.path.isdir(dir_logs):
    os.system('mkdir -p '+dir_logs)
log_name = os.path.join(dir_work,'archive_logs',log_file_name) 
logger = instantiate_logger(log_name, dt_cron_start_lt) 

# instantiate logger 
###############################################################################


###############################################################################
# download data

var_list = ['fm100', 'fm1000']
n_vars = len(var_list)

[yy_start, yy_end] = [1979, 2019]
yy_axis = numpy.arange(yy_start, yy_end, 1)
n_yy = len(yy_axis)

yy = 10
v = 0
for yy in range(0, n_yy, 1):
    print      ('  yy %s of %s ' % (yy, n_yy))
    logger.info('  yy %s of %s ' % (yy, n_yy))
    yy_temp = yy_axis[yy]
    for v in range(0, n_vars, 1):
        var_temp = var_list[v]
        # wget -nc -c -nd http://www.northwestknowledge.net/metdata/data/fm1000_1989.nc 
        wget_command = 'wget -nc -c -nd http://www.northwestknowledge.net/metdata/data/'+var_temp+'_'+str(yy_temp)+'.nc' 
        print      ('wget_command is %s ' % (wget_command))
        logger.info('wget_command is %s ' % (wget_command)) 
        os.system(wget_command)

# download data
###############################################################################


###############################################################################
# read data


yy_temp = 1989
var_temp = 'fm1000'
file_name_read = os.path.join(dir_data,var_temp+'_'+str(yy_temp)+'.nc')

os.path.isfile(file_name_read) 
        
# get grid coordinates and subset 
ncfile_read  = Dataset(file_name_read,'r') 
ncfile_read.variables    

lat_1d = numpy.array(ncfile_read['lat'])
lon_1d = numpy.array(ncfile_read['lon'])    

nx 1386
ny 585

day_read = numpy.array(ncfile_read['day'])    
description: days since 1900-01-01
n_days = len(day_read)

# note cmsith - this is too big, need to subset
dfm_1000hr = numpy.array(ncfile_read['dead_fuel_moisture_1000hr'])
numpy.shape(dfm_1000hr)


  filling on, default _FillValue of 65535 used),
             ('', <class 'netCDF4._netCDF4.Variable'>
              uint16 dead_fuel_moisture_1000hr(day, lat, lon)
                  _FillValue: 32767
                  units: Percent
                  description: 1000 hour fuel moisture
                  long_name: fm1000
                  standard_name: fm1000
                  missing_value: 32767
                  dimensions: lon lat time
                  grid_mapping: crs
                  coordinate_system: WGS84,EPSG:4326
                  scale_factor: 0.1
                  add_offset: 0.0
                  coordinates: lon lat
                  _Unsigned: true
              unlimited dimensions: 
              current shape = (365, 585, 1386)
              filling on)])

    
    # ('crs', <class 'netCDF4._netCDF4.Variable'>
#  uint16 crs(crs)
#  grid_mapping_name: latitude_longitude
#  longitude_of_prime_meridian: 0.0
#  semi_major_axis: 6378137.0
#  long_name: WGS 84
#  inverse_flattening: 298.257223563
#  GeoTransform: -124.7666666333333 0.041666666666666 0  49.400000000000000 -0.041666666666666
#  spatial_ref: GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]
#  unlimited dimensions: 
#  current shape = (1,)

    

# read data
###############################################################################





