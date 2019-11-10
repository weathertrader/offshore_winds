    
###############################################################################
# define_dt_axis.py
# author: Craig Smith 
# purpose: define a datetime axis
# usage:  
#   interval_string = '1d'
#   interval_string = '1hr'
#   interval_string = '1min'
#   (dt_axis_master_day_pst, n_days) = define_dt_axis(logger, dt_start, dt_end, '1d')
#   (dt_axis_master_hr_pst, n_hrs)   = define_dt_axis(logger, dt_start, dt_end, '1hr')
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
#   dt_start = dt_start_1hr
#   dt_end   = dt_end_1hr
#   dt_start = dt_init_utc_start
#   dt_end   = dt_init_utc_end  

#
###############################################################################


###############################################################################
# 

def define_datetime_axis(logger, dt_start, dt_end, interval_string):

    import numpy
    import datetime
    #from datetime import datetime, timedelta

    if ('d' in interval_string):
        interval_int = int(interval_string.replace('d',''))
        n_days = (dt_end- dt_start).days
        n_intervals = n_days
        dt_axis_master_temp = numpy.full([n_days], numpy.nan, dtype=object)
        for d in range(0, n_days, 1):
            dt_axis_master_temp[d] = dt_start + datetime.timedelta(days=d*interval_int) 
    elif ('hr' in interval_string):
        interval_int = int(interval_string.replace('hr',''))
        n_days = (dt_end- dt_start).days
        if (n_days == 0):
            n_intervals = int((dt_end - dt_start).seconds/(3600*interval_int))
            print      ('      define_dt_axis: n_int option 1 is %s ' % (n_intervals))
            logger.info('      define_dt_axis: n_int option 1 is %s ' % (n_intervals))
        else:
            n_intervals = int((dt_end - dt_start).days*24/interval_int + (dt_end - dt_start).seconds/(3600*interval_int))+1
            print      ('      define_dt_axis: n_int option 2 is %s ' % (n_intervals))
            logger.info('      define_dt_axis: n_int option 2 is %s ' % (n_intervals))

        dt_axis_master_temp = numpy.full([n_intervals], numpy.nan, dtype=object)
        for hr in range(0, n_intervals, 1):
            dt_axis_master_temp[hr] = dt_start + datetime.timedelta(hours=hr*interval_int) 
    elif ('min' in interval_string):
        interval_int = int(interval_string.replace('min',''))
        n_seconds = (dt_end- dt_start).days*24*60
        n_intervals = n_seconds
        dt_axis_master_temp = numpy.full([n_seconds], numpy.nan, dtype=object)
        for sec in range(0, n_intervals, 1):
            dt_axis_master_temp[sec] = dt_start + datetime.timedelta(minutes=sec*interval_int) 
    else: 
        print      ('      ERROR: define_dt_axis interval not defined yet ')
        logger.info('      ERROR: define_dt_axis interval not defined yet ')

    print      ('      define_dt_axis: %s to %s with %s intervals ' % (dt_axis_master_temp[0].strftime('%Y-%m-%d_%H'), dt_axis_master_temp[-1].strftime('%Y-%m-%d_%H'), n_intervals))
    logger.info('      define_dt_axis: %s to %s with %s intervals ' % (dt_axis_master_temp[0].strftime('%Y-%m-%d_%H'), dt_axis_master_temp[-1].strftime('%Y-%m-%d_%H'), n_intervals))

    return dt_axis_master_temp, n_intervals

# 
###############################################################################

