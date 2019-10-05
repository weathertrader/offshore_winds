    
###############################################################################
# define_datetime_axis.py
# author: Craig Smith 
# purpose: define a datetime axis
# usage:  
#   interval_string = '1d'
#   interval_string = '1hr'
#   interval_string = '1min'
#   (dt_axis_master_day_pst, n_days) = define_datetime_axis(logger, dt_start, dt_end, '1d')
#   (dt_axis_master_hr_pst, n_hrs)   = define_datetime_axis(logger, dt_start, dt_end, '1hr')
# revision history:  
#   03/29/2018 - original 
# to do: 
#   generalize output codes for http vs ftp  
# notes: 
#   - 
# debugging: 
#   interval_string = '1d'
#   interval_string = '1hr'
#   interval_string = '1min'
#   datetime_start = datetime_start_1hr
#   datetime_end   = datetime_end_1hr

###############################################################################


###############################################################################
# 

def define_datetime_axis(logger, datetime_start, datetime_end, interval_string):

    import numpy
    import datetime
    #from datetime import datetime, timedelta

    if ('d' in interval_string):
        interval_int = int(interval_string.replace('d',''))
        n_days = (datetime_end- datetime_start).days
        n_intervals = n_days
        datetime_axis_master_temp = numpy.full([n_days], numpy.nan, dtype=object)
        for d in range(0, n_days, 1):
            datetime_axis_master_temp[d] = datetime_start + datetime.timedelta(days=d*interval_int) 
    elif ('hr' in interval_string):
        interval_int = int(interval_string.replace('hr',''))
        n_days = (datetime_end- datetime_start).days
        if (n_days == 0):
            n_hrs = int((datetime_end - datetime_start).seconds/3600)
            print      ('      define_datetime_axis: n_hrs option 1 is %s ' % (n_hrs))
            logger.info('      define_datetime_axis: n_hrs option 1 is %s ' % (n_hrs))
        else:
            n_hrs = int((datetime_end - datetime_start).days*24+(datetime_end - datetime_start).seconds/(3600))+1
            print      ('      define_datetime_axis: n_hrs option 2 is %s ' % (n_hrs))
            logger.info('      define_datetime_axis: n_hrs option 2 is %s ' % (n_hrs))

        n_intervals = n_hrs
        datetime_axis_master_temp = numpy.full([n_hrs], numpy.nan, dtype=object)
        for hr in range(0, n_hrs, 1):
            datetime_axis_master_temp[hr] = datetime_start + datetime.timedelta(hours=hr*interval_int) 
    elif ('min' in interval_string):
        interval_int = int(interval_string.replace('min',''))
        n_seconds = (datetime_end- datetime_start).days*24*60
        n_intervals = n_seconds
        datetime_axis_master_temp = numpy.full([n_seconds], numpy.nan, dtype=object)
        for sec in range(0, n_intervals, 1):
            datetime_axis_master_temp[sec] = datetime_start + datetime.timedelta(minutes=sec*interval_int) 
    else: 
        print      ('      ERROR: define_datetime_axis interval not defined yet ')
        logger.info('      ERROR: define_datetime_axis interval not defined yet ')

    print      ('      define_datetime_axis: %s to %s with %s intervals ' % (datetime_axis_master_temp[0].strftime('%Y-%m-%d_%H'), datetime_axis_master_temp[-1].strftime('%Y-%m-%d_%H'), n_intervals))
    logger.info('      define_datetime_axis: %s to %s with %s intervals ' % (datetime_axis_master_temp[0].strftime('%Y-%m-%d_%H'), datetime_axis_master_temp[-1].strftime('%Y-%m-%d_%H'), n_intervals))

    return datetime_axis_master_temp, n_intervals

# 
###############################################################################

