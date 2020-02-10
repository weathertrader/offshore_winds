
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

# python /home/craigmatthewsmith/offshore_winds/offshore_winds/process_model_data_to_event_max.py --event='2019_10_09_event' --dt_min_plot_utc_str='2019-10-09_08' --dt_max_plot_utc_str='2019-10-11_08' --model_name='hrrr' --dt_init_utc_str='2019-10-07_12' 

# 2019-10-10_00


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
#from build_model_local_file_names                      import build_model_local_file_names
#from function_library import convert_wrf_datetime

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


###############################################################################
# parse command line options 

if (manual_mode): 
    
    model_name = 'rasmussen'

    ########################################
    # 2009/09/23 event 
    event = '2006_09_23_event'
    dt_min_plot_utc_str = '2006-09-21_08'
    dt_max_plot_utc_str = '2006-09-25_08'

    ########################################
    # 2012/12/01 event 
    #event = '2011_12_01_event'
    #dt_min_plot_utc_str = '2011-11-30_08'
    #dt_max_plot_utc_str = '2011-12-02_08'
   
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

dt_min_plot_utc = dt.strptime(dt_min_plot_utc_str,'%Y-%m-%d_%H')
dt_max_plot_utc = dt.strptime(dt_max_plot_utc_str,'%Y-%m-%d_%H')

dir_data_model_ingest = os.path.join(dir_data_model, model_name)

# set model data ingest and archive directories 
###############################################################################



#[lon_min, lon_max] = [-160.0, -110.0]
#[lat_min, lat_max] = [  25.0,   50.0]
# nor cal only 
#[lon_min, lon_max, lon_int] = [-124.5, -117.0, 1.0]
#[lat_min, lat_max, lat_int] = [  36.0,   42.2, 0.5]
# all ca
[lon_min, lon_max, lon_int] = [-124.5, -114.0, 1.0]
[lat_min, lat_max, lat_int] = [  32.0,   42.2, 0.5]


###############################################################################
# read_model_data

print      ('read_model_data begin')
logger.info('read_model_data begin')

file_name_read = os.path.join(dir_data_model_ingest,'RALconus4km_wrf_constants.nc')
ncfile_read = Dataset(file_name_read,'r') 
ncfile_read.variables
hgt_2d = numpy.array(ncfile_read.variables['HGT'][0])
ncfile_read.close()

#file_name_read = os.path.join(dir_data_model_ingest,'wrf2d_d01_CTRL_U10_201110-201112.nc')
file_name_read = os.path.join(dir_data_model_ingest,'wrf2d_d01_CTRL_U10_200607-200609.nc')
ncfile_read = Dataset(file_name_read,'r') 
lon_2d = numpy.array(ncfile_read.variables['XLONG'])
lat_2d = numpy.array(ncfile_read.variables['XLAT'])
[ny, nx] = numpy.shape(lon_2d)
times_wrf = ncfile_read.variables['Times']
utc_conversion = 0 # keep in UTC 
(datetime_wrf_utc_read) = convert_wrf_datetime(times_wrf, utc_conversion) 
index_min = (datetime_wrf_utc_read < dt_min_plot_utc).argmin()
index_max = (datetime_wrf_utc_read < dt_max_plot_utc).argmin()+1

datetime_wrf_utc_read[index_min]
datetime_wrf_utc_read[index_max]

datetime_wrf_utc = datetime_wrf_utc_read[index_min:index_max]


#datetime_wrf_utc[index_min:index_max]
u_ws10_2d_hr = numpy.array(ncfile_read.variables['U10'][index_min:index_max,:,:])
numpy.shape(u_ws10_2d_hr)
ncfile_read.close()

#file_name_read = os.path.join(dir_data_model_ingest,'wrf2d_d01_CTRL_V10_201110-201112.nc')
file_name_read = os.path.join(dir_data_model_ingest,'wrf2d_d01_CTRL_V10_200607-200609.nc')
ncfile_read = Dataset(file_name_read,'r') 
v_ws10_2d_hr = numpy.array(ncfile_read.variables['V10'][index_min:index_max,:,:])
ncfile_read.close()
 
print      ('process_to_max begin')
logger.info('process_to_max begin')

ws10_2d_hr = numpy.sqrt(u_ws10_2d_hr**2.0 + u_ws10_2d_hr**2.0)
ws10_max_2d  = numpy.full([ny, nx], numpy.nan, dtype=float)
for j in range(0, ny , 1):
    if (j%10 == 0):
        print('  processing j %s of %s' %(j, ny))
    for i in range(0, nx, 1):
        ws10_max_2d[j,i] = numpy.nanmax(ws10_2d_hr[:,j,i])
        
print      ('process_to_max end')
logger.info('process_to_max end')

# process to max 
###############################################################################


###############################################################################
# plot_maps 

[nt, ny, nx] = numpy.shape(u_ws10_2d_hr)

ws_units = 'mph'
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


width_roads = 1.0

plot_area = ['nor_ca']
#plot_area = ['nor_ca', 'nor_bay', 'nor_sierra','bay', 'cen_sierra', 'nor_valley', 'nor_coast']
#plot_area = ['nor_bay']
n_areas = len(plot_area)



n = 48
a = 0
for n in range(0, nt, 1):
    print      ('  plotting n %s of %s ' % (n, nt))
    logger.info('  plotting n %s of %s ' % (n, nt))    
    dt_wrf_utc_temp = datetime_wrf_utc[n]  
    dt_wrf_pst_temp = dt_wrf_utc_temp + td(hours=8) 
    u_ws10_plot = 2.23694*u_ws10_2d_hr[n,:,:]
    v_ws10_plot = 2.23694*v_ws10_2d_hr[n,:,:]
    ws10_plot = numpy.sqrt(u_ws10_plot**2.0 + v_ws10_plot**2.0)
    
    for a in range(0, n_areas, 1):
        area_temp = plot_area[a]
        #print      ('  plotting area %s of %s ' % (a, n_areas))
        #logger.info('  plotting area %s of %s ' % (a, n_areas))    
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
    
        #hgt_lines = plt.contour (lon_static_2d, lat_static_2d, hgt_static_2d, levels=numpy.arange(hgt_min, hgt_max, hgt_int), colors='gray', linestyles='solid', linewidths=0.5)
        hgt_lines = plt.contour (lon_2d, lat_2d, hgt_2d, levels=numpy.arange(hgt_min, hgt_max, hgt_int), colors='gray', linestyles='solid', linewidths=0.5)
        im = plt.contourf(lon_2d, lat_2d, ws10_plot, numpy.arange(ws_min, ws_max, ws_int), cmap=cmap_ws, transform=ccrs.PlateCarree()) # jet, viridis 
       
        [quiv_interval, quiv_scale] = [5, 800] # 5, 400
        ax.quiver(lon_2d[::quiv_interval,::quiv_interval], lat_2d[::quiv_interval,::quiv_interval], u_ws10_plot[::quiv_interval,::quiv_interval], v_ws10_plot[::quiv_interval,::quiv_interval], scale=quiv_scale, color='b', transform=ccrs.PlateCarree())
        [ws_crit, wsg_crit, wsg_crit_t_line] = [25.0, 45.0, 55.0]
        #ws_lines = plt.contour(lon_2d, lat_2d, ws10_max_2d, levels = numpy.arange(ws_min, ws_max, ws_int), colors='k', linestyles='solid', linewidths=0.5)
        ws_line  = plt.contour(lon_2d, lat_2d, ws10_plot, levels = [ws_crit], colors='r', linestyles='solid',linewidths=2)
        im.set_clim(ws_min, ws_max) 
        cbar = fig.colorbar(im, shrink=0.6) # was 0.7 0.8
        #cbar = fig.colorbar(im)
        cbar.set_label('ws [mph]',fontsize=12,labelpad=00)                                
    
        plt.xlabel('longitude', fontsize=12, labelpad=10) # 10 is too small, 20 
        plt.ylabel('latitude',  fontsize=12, labelpad=10) # 30 is too small, 60 
        plt.title('ws max %s %s PST  ' % (model_name, dt_wrf_pst_temp.strftime('%Y-%m-%d_%H')) , \
            fontsize=12, loc='left', weight = 'bold')   
        plt.show()
        plt.tight_layout()        
        filename = 'ws_inst_%s_model_%s_time_%s.png' % (area_temp, model_name, dt_wrf_pst_temp.strftime('%Y-%m-%d_%H'))
        plot_name = os.path.join(dir_work, 'figs_ws_maps_inst', filename) 
        dpi_level = 400 # 400        
        #plt.savefig(plot_name)
        plt.savefig(plot_name, dpi=dpi_level) 
        #fig.clf()
        #plt.close()        
    

# plot_maps 
###############################################################################


###############################################################################
# write_max_model_data 

write_max_model_data = True

if (write_max_model_data):
        
    file_name_write = os.path.join(dir_data_model, 'event_max', 'max_'+event+'_model_'+model_name+'.nc')
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
    
    ws10_max_2d_write  = ncfile_write.createVariable('ws10_max_2d',  numpy.dtype('float32').char,('y','x'))
    #wsg10_max_2d_write = ncfile_write.createVariable('wsg10_max_2d', numpy.dtype('float32').char,('y','x'))
    #rh2_min_2d_write   = ncfile_write.createVariable('rh2_min_2d',   numpy.dtype('float32').char,('y','x'))
    ws10_max_2d_write [:] =  ws10_max_2d[:,:]     
    #wsg10_max_2d_write[:] = wsg10_max_2d[:,:]     
    #rh2_min_2d_write  [:] = wsg10_max_2d[:,:]     

    del lon_2d_write, lat_2d_write, hgt_2d_write, ws10_max_2d_write
    #del wsg10_max_2d_write, rh2_min_2d_write
 
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
