    
###############################################################################
# instantiate_logger.py
# author: Craig Smith 
# purpose: create a logger 
# revision history:  
#   02/19/2018 - original 
# usage:  
#   log_name = 'run_wrf_%s' % (datetime_cron_start_lst.strftime('%Y-%m-%d_%H-%M')) 
#   logger = instantiate_logger(log_name) 
# version history 
#   02/19/2018 - ported to new function_library 
#   01/30/2016 - original 
# to do: 
#   - 
# notes: 
#   - 
# debugging: 
#   - 
###############################################################################


###############################################################################
# 

def instantiate_logger(log_name_full_file_path, datetime_cron_start_lt):

    import os
    import logging 

    if not (os.path.isdir(os.path.dirname(log_name_full_file_path))):
        #os.mkdir(os.path.dirname(log_name_full_file_path))
        os.system('mkdir -p '+os.path.dirname(log_name_full_file_path))    

    log_file_name = os.path.basename(log_name_full_file_path)    
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(module)s - %(message)s') 
    logger    = logging.getLogger(log_name_full_file_path)
    handler   = logging.FileHandler(log_name_full_file_path) 
    formatter = logging.Formatter('%(message)s')
    handler.setFormatter(formatter) 
    logger.addHandler(handler) 
    logger.setLevel(logging.INFO) # INFO, DEBUG,INFO,WARNING,ERROR,CRITICAL
    
    print      ('###############################################################################') 
    logger.info('###############################################################################') 
    print      ('instantiate_logger at %s ' % (datetime_cron_start_lt.strftime('%Y-%m-%d_%H-%M')))
    logger.info('instantiate_logger at %s ' % (datetime_cron_start_lt.strftime('%Y-%m-%d_%H-%M')))     
    print      ('instantiate_logger log_name is %s ' % (log_file_name))     
    logger.info('instantiate_logger log_name is %s ' % (log_file_name))     
       
    return logger
  
# 
###############################################################################
