    
###############################################################################
# define_daylight_savings_or_not.py
# author: Craig Smith 
# purpose: define utc conversion and time zone label based on whether or not 
#          daylight savings time is in effect or not 
# revision history:  
#   03/09/2018 - updated through and including 2024
#   02/19/2018 - original 
# usage:  
#   (utc_conversion, time_zone_label) = define_daylight_savings_or_not(datetime_cron_start_utc) 
# version history 
#   02/19/2018 - ported to new function_library 
#   11/05/2017 - updated to 2018 dst dates 
#   10/28/2016 - original  
# to do: 
#   - 
# notes: 
#   - 
# debugging: 
# datetime_temp_utc = datetime.datetime.utcnow()
# datetime_temp_utc = datetime.datetime(2018,  2, 1)
# datetime_temp_utc = datetime.datetime(2018,  7, 1)
# datetime_temp_utc = datetime.datetime(2018, 12, 1)

def define_daylight_savings_or_not(datetime_temp_utc):

    import datetime 

    yy_temp = datetime.datetime.strftime(datetime_temp_utc,'%Y')
    yy_temp = int(yy_temp) 

    #mo_temp = datetime.datetime.strftime(datetime_temp_utc,'%m')
    #dd_temp = datetime.datetime.strftime(datetime_temp_utc,'%d')
    #hh_temp = datetime.datetime.strftime(datetime_temp_utc,'%H') 
    #mo_temp = int(mo_temp) 
    #dd_temp = int(dd_temp) 
    #hh_temp = int(hh_temp)  

    #2018	March 11	November 4
    #2019	March 10	November 3
    #2020	March 8	November 1  
    #2021	March 14	November 7
    #2022	March 13	November 6
    #2023	March 12	November 5
    #2024	March 10	November 3      
        
    if   (yy_temp == 2018):
        datetime_dst_start = datetime.datetime(2018,  3, 11, 10) 
        datetime_dst_end   = datetime.datetime(2018, 11,  4, 10) 
    elif (yy_temp == 2019):
        datetime_dst_start = datetime.datetime(2019,  3, 10, 10)  
        datetime_dst_end   = datetime.datetime(2019, 11,  3, 10)   
    elif (yy_temp == 2020):
        datetime_dst_start = datetime.datetime(2020,  3,  8, 10)
        datetime_dst_end   = datetime.datetime(2020, 11,  1, 10)
    elif (yy_temp == 2021):
        datetime_dst_start = datetime.datetime(2021,  3, 14, 10)
        datetime_dst_end   = datetime.datetime(2021, 11,  7, 10)
    elif (yy_temp == 2022):
        datetime_dst_start = datetime.datetime(2022,  3, 13, 10)
        datetime_dst_end   = datetime.datetime(2022, 11,  6, 10)
    elif (yy_temp == 2023):
        datetime_dst_start = datetime.datetime(2023,  3, 12, 10)
        datetime_dst_end   = datetime.datetime(2024, 11,  5, 10)
    elif (yy_temp == 2024):
        datetime_dst_start = datetime.datetime(2024,  3, 10, 10)
        datetime_dst_end   = datetime.datetime(2024, 11,  3, 10)

    if ((datetime_temp_utc >= datetime_dst_start) and (datetime_temp_utc <= datetime_dst_end)):
        use_dst = 1
    else:
        use_dst = 0
        
    if   (use_dst == 0):
        utc_conversion = 8
        time_zone_label = 'PST'
    elif (use_dst == 1):    
        utc_conversion = 7
        time_zone_label = 'PDT'

    return utc_conversion, time_zone_label

# define_daylight_savings_or_not
###############################################################################
