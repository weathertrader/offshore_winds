
###############################################################################
# deenenergization_analysis.py 
# purpose: analysis on 2019/10 power shutoffs 
# author: Craig Smith 
# version history 
#   2020/01/06 - original 
# usage:  
#   gui 
# notes:
#   - 
# to do: 
# - 
#
###############################################################################

host_name = 'chromebook' # macbook




###############################################################################
# module import 

import os 
#import datetime as dt
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


dir_work = '/home/craigmatthewsmith/offshore_winds/offshore_winds'
os.chdir(dir_work)

#dir_scripts = '/home/craigmatthewsmith/scripts'
#sys.path.append(os.path.join(dir_scripts, 'function_library'))
sys.path.append(dir_work)
from define_datetime_axis import define_datetime_axis


# module import 
###############################################################################


###############################################################################
#

# 2013/10/5 is first instance
dt_start = dt(2013, 1, 1)  
dt_end   = dt(2020, 1, 1)  
logger = None
interval_string = '1hr'
(dt_axis_hr_pst, n_hrs) = define_datetime_axis(logger, dt_start, dt_end, '1hr')


utility_list = ['SDG&E','PG&E','SCE']
n_utilities = len(utility_list)

#
###############################################################################


###############################################################################
# data read and analysis 

file_name = 'cpuc_deenergization_2019_11_22.xlsx'
file_name_full_path = os.path.join(dir_work, file_name)
os.path.isfile(file_name_full_path)

outage_df = pandas.read_excel(file_name_full_path,index_col=None, header=1)
#outage_df.head()

utility = outage_df['Utility']
dt_outage_start_read = outage_df['Outage Start']
dt_outage_end_read  = outage_df['Full Restoration ']

#outage_df['Outage Duration']
#outage_df['Outage Days']
#outage_df['Outage Hours']
customer_total = numpy.array(outage_df['TOTAL CUSTOMERS IMPACTED'])
customer_res   = numpy.array(outage_df['RESIDENTIAL CUSTOMERS'])
customer_com   = numpy.array(outage_df['COMMERCIAL/INDUSTRIAL CUSTOMERS'])
customer_med   = numpy.array(outage_df['MEDICAL BASELINE CUSTOMERS'])

n_events = len(customer_total)
for n in range(0, n_events, 1):
    if isinstance(customer_res[n], str):    
        customer_res[n] = 0.0
    else:
        if not (customer_res[n] > 0):
            customer_res[n] = 0.0
    if isinstance(customer_total[n], str):
        customer_total[n] = 0.0
    else:
        if not (customer_total[n] > 0):
            customer_total[n] = 0.0
    if isinstance(customer_com[n], str):    
        customer_com[n] = 0.0
    else:
        if not (customer_com[n] > 0):
            customer_com[n] = 0.0
    if isinstance(customer_med[n], str):    
        customer_med[n] = 0.0
    else:
        if not (customer_med[n] > 0):
            customer_med[n] = 0.0
        
#n_events = len(dt_start_read)
dt_outage_start_str = ["%s" % x for x in dt_outage_start_read] 
dt_outage_end_str   = ["%s" % x for x in dt_outage_end_read] 

mask = numpy.full([n_events], False, dtype=bool)
for n in range(0, n_events, 1):
    if not (('prior' in dt_outage_start_str[n]) or ('Permanently' in dt_outage_start_str[n]) or ('Out' in dt_outage_end_str[n]) or ('Out' in dt_outage_start_str[n]) or ('Idle' in dt_outage_start_str[n])):
        mask[n] = True

customer_total = customer_total[mask]
customer_res   = customer_res  [mask]
customer_com   = customer_com  [mask]
customer_med   = customer_med  [mask]

n = 0
dt_outage_start = numpy.full([n_events], numpy.nan, dtype=object)
dt_outage_end   = numpy.full([n_events], numpy.nan, dtype=object)
for n in range(0, n_events, 1):
    if not (('prior' in dt_outage_start_str[n]) or ('Permanently' in dt_outage_start_str[n]) or ('Out' in dt_outage_end_str[n]) or ('Out' in dt_outage_start_str[n]) or ('Idle' in dt_outage_start_str[n])):
        try:
            dt_outage_start[n] = (dt.strptime(dt_outage_start_str[n],'%Y-%m-%d %H:%M:%S'))   
        except:
            dt_outage_start[n] = (dt.strptime(dt_outage_start_str[n],'%m/%d/%y %H:%M'))
        try:
            dt_outage_end  [n] = (dt.strptime(dt_outage_end_str  [n],'%Y-%m-%d %H:%M:%S'))     
        except:
            try:
                dt_outage_end  [n] = (dt.strptime(dt_outage_end_str  [n],'%m/%d/%y %H:%M')) 
            except:
                print(n)

del dt_outage_start_str, dt_outage_end_str

dt_outage_start = dt_outage_start[mask]
dt_outage_end   = dt_outage_end  [mask]

n_events = len(dt_outage_start)


customer_total_out_u_hr = numpy.full([n_utilities, n_hrs], 0.0, dtype=float)
customer_res_out_u_hr   = numpy.full([n_utilities, n_hrs], 0.0, dtype=float)
customer_com_out_u_hr   = numpy.full([n_utilities, n_hrs], 0.0, dtype=float)
customer_med_out_u_hr   = numpy.full([n_utilities, n_hrs], 0.0, dtype=float)
customer_total_out_hr = numpy.full([n_hrs], 0.0, dtype=float)

n = 860
for n in range(0, n_events, 1):
    #if not(numpy.isnan(dt_outage_start[n]) & numpy.isnan(dt_outage_end[n])): 
    index_min = (dt_outage_start[n] < dt_axis_hr_pst).argmax()-1
    index_max = (dt_outage_end  [n] < dt_axis_hr_pst).argmax()
    #index_min
    #index_max
    #dt_outage_start[n]
    #dt_outage_end  [n]
    #dt_axis_hr_pst[index_min]
    #dt_axis_hr_pst[index_max]
    u = (utility_list).index(utility[n])
    #utility_list[u]
    #utility[n]
    customer_total_out_u_hr[u,index_min:index_max] = customer_total_out_u_hr[u,index_min:index_max] + customer_total[n]
    customer_res_out_u_hr  [u,index_min:index_max] = customer_res_out_u_hr  [u,index_min:index_max] + customer_res  [n]
    customer_com_out_u_hr  [u,index_min:index_max] = customer_com_out_u_hr  [u,index_min:index_max] + customer_com  [n]
    customer_med_out_u_hr  [u,index_min:index_max] = customer_med_out_u_hr  [u,index_min:index_max] + customer_med  [n]
    
    
total_customer_hours_out = numpy.full([n_utilities], 0.0, dtype=float)    
for u in range(0, n_utilities, 1):
    total_customer_hours_out[u] = numpy.nansum(customer_total_out_u_hr[u,:])
    
total_customer_hours_out = total_customer_hours_out/1000.0    
    
# data read and analysis
###############################################################################
    

###############################################################################
# figs time series analysis 

color_list = ['r', 'b', 'g']
width_line = 3.0
size_marker = 0.0


u = 0
for u in range(0, n_utilities, 1):
    if   (u == 0): # sdg&e
        [yy_min, yy_max, yy_int] = [0, 26000, 5000]
        dt_min = dt_start
        dt_max = dt(2019, 11, 4)
    elif (u == 1): # pg&E
        [yy_min, yy_max, yy_int] = [0, 1000000, 100000]
        #dt_min = dt(2018, 10, 1)
        dt_min = dt(2019, 10, 1)
        dt_max = dt(2019, 11, 4)
    elif (u == 2): # sce
        [yy_min, yy_max, yy_int] = [0, 100000, 10000]
        dt_min = dt(2019, 10, 1)
        dt_max = dt(2019, 11, 5)
        #delta = td(hours=6) # 2, 6, 12
        #datetick_format = '%m/%d %H' 
        #date_ticks = matplotlib.dates.drange(dt_min_plot, dt_max_plot+delta, delta)
        #date_ticks = matplotlib.dates.drange(dt_min_plot+td(hours=12), dt_max_plot+delta, delta)
        #n_date_ticks = len(date_ticks) 
        
    yy_ticks = numpy.arange(yy_min, yy_max+yy_int, yy_int)
        
    fig_num = 201 
    fig = plt.figure(num=fig_num,figsize=(10,5)) 
    plt.clf() 
    plt.plot(dt_axis_hr_pst, customer_total_out_u_hr[u,:], color_list[u], linestyle='-', label=utility_list[u], linewidth=width_line, marker='o', markersize=size_marker, markeredgecolor='k')     
    #    plt.plot(dt_axis_hr_pst, customer_total_out_u_hr[u,:], color_list[u], linestyle='-', label=utility_list[u], linewidth=width_line, marker='o', markersize=size_marker, markeredgecolor='k') 
    #for dum in range(-6, 6, 1):
    #    plt.plot([0, 24], [dum, dum],  'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    #for dum in range(0, 24, 2):
    #    plt.plot([dum, dum], [-6, 6],  'gray', linestyle='-', linewidth=0.5, marker='o', markersize=0) 
    #plt.legend(loc=3,fontsize=10,ncol=1) 
    plt.title('customer outages vs date %s ' %(utility_list[u]),\
         fontsize=16, x=0.5, y=1.01,weight = 'bold')
    plt.xlabel('date',     fontsize=16,labelpad=0)
    plt.ylabel('customers affected',fontsize=16,labelpad=0)  
    plt.xlim([dt_min, dt_max])
                    
    #plt.xticks(numpy.arange(yy_min, yy_max, 2))                     
    #plt.xlim([yy_min-1, yy_max+1])
    #minorLocator = MultipleLocator(1)
    #plt.gca().yaxis.set_minor_locator(minorLocator)            
    plt.ylim([yy_min, yy_max]) 
    plt.yticks(yy_ticks, fontsize=14)             
    plt.show() 
    filename = 'outages_u_'+str(u)+'_vs_date.png'
    plot_name = os.path.join(dir_work, 'figs_outages', filename)
    plt.savefig(plot_name)



#1 hr fig to JA
#1 hr SDG&E




###############################################################################
# print powerline ignitions info to screen 

#n = 9
#mask = (cause_desc[:] == cause_desc_unique[n]) 
#fire_name_temp     =     fire_name[mask]
#fire_size_temp     =     fire_size[mask]
#ignition_date_temp = ignition_date[mask]
#n_powerline_ignitions = len(fire_name_temp)
#
#fire_size_min = 1000.0
#for n in range(0, n_powerline_ignitions, 1):
#    if (fire_size_temp[n] > fire_size_min):
#        print ('%s, %s, %7i, %s ' %(str(n).rjust(2,'0'), ignition_date_temp[n].strftime('%Y-%m-%d'), fire_size_temp[n], fire_name_temp[n]))
#
#n = 183872 # Butte fire 2015/09/10 listed as Missing/Undefined
#for n in range(0, n_ignitions, 1):
#    if (fire_name[n] == 'BUTTE'):
#        print ('%s, %s, %7i, %s ' %(str(n).rjust(2,'0'), ignition_date[n].strftime('%Y-%m-%d'), fire_size[n], fire_name[n]))

# print powerline ignitions info to screen 
###############################################################################

    

#plt.xticks(numpy.arange(yy_min, yy_max, 2))                     
#plt.xlim([yy_min-1, yy_max+1])
#minorLocator = MultipleLocator(1)
#plt.gca().yaxis.set_minor_locator(minorLocator)            





