    
###############################################################################
# convert_ws_components_to_ws_and_wd.py
# author: Craig Smith 
# purpose: convert u and v components of wind speed to wind speed and wind direction 
# revision history:  
#   02/09/2019 - allows for NULL inputs in addition to nan
#                note  arrays with numpy.nan can be float
#                while arrays with NULL must be object 
#   03/09/2018 - original 
# usage:  
#   (ws_temp, wd_temp) convert_ws_components_to_ws_and_wd(u_ws_10m, v_ws_10m)
# to do: 
#   - 
# notes: 
#   - 
# debugging: 
#   u_ws_temp = u_ws_10m
#   v_ws_temp = v_ws_10m
#   u_ws_temp = u_ws_1hr
#   v_ws_temp = v_ws_1hr


#
###############################################################################


###############################################################################
#

def convert_ws_components_to_ws_and_wd(u_ws_temp, v_ws_temp):

    import numpy 


    # convert NULL if found to numpy.nan
    index_null = ((u_ws_temp == 'NULL') | (v_ws_temp == 'NULL'))
    u_ws_temp_no_null = u_ws_temp
    v_ws_temp_no_null = v_ws_temp
    len_null_found = len(u_ws_temp[index_null])
    if (len_null_found > 0):
        null_found = True
    else:
        null_found = False
    del u_ws_temp, v_ws_temp
    if (null_found):
        u_ws_temp_no_null[index_null] = numpy.nan
        v_ws_temp_no_null[index_null] = numpy.nan
        # an array with NULL must be and object
        u_ws_temp_no_null = u_ws_temp_no_null.astype(float)
        v_ws_temp_no_null = v_ws_temp_no_null.astype(float)

    ws_temp_no_null = numpy.sqrt((numpy.square(u_ws_temp_no_null) + numpy.square(v_ws_temp_no_null)))  

    #n_dim = numpy.ndim(u_ws_temp_no_null)
    #if   (n_dim == 2): 
    #    [n1, n2] = numpy.shape(u_ws_temp)      
    #    wd_temp = numpy.full([n1, n2], numpy.nan, dtype='float') 
    #elif (n_dim == 3): 
    #    [n1, n2, n3] = numpy.shape(u_ws_temp)         
    #    wd_temp = numpy.full([n1, n2, n3], numpy.nan, dtype='float') 

    wd_temp_no_null = numpy.arctan2(v_ws_temp_no_null, u_ws_temp_no_null)*180.0/numpy.pi
    wd_temp_no_null = 270.0 - wd_temp_no_null 
    mask = (wd_temp_no_null < 0.0)     
    wd_temp_no_null[mask] = wd_temp_no_null[mask] + 360.0 
    mask = (wd_temp_no_null > 360.0)     
    wd_temp_no_null[mask] = wd_temp_no_null[mask] - 360.0 

    ws_temp = ws_temp_no_null
    wd_temp = wd_temp_no_null
    del ws_temp_no_null, wd_temp_no_null
    if (null_found): # otherwise returns numpy.nan as found 
        ws_temp = ws_temp.astype(object)
        wd_temp = ws_temp.astype(object)
        ws_temp[index_null] = 'NULL'
        wd_temp[index_null] = 'NULL'
    
    return ws_temp, wd_temp 
  
# 
###############################################################################
