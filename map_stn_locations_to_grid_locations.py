    
###############################################################################
# map_stn_locations_to_grid_locations.py
# author: Craig Smith 
# purpose: find indices of stn locations in a 2d grid 
# usage:  
#     print_flag = True
#     (j_loc_s, i_loc_s) = map_stn_locations_to_grid_locations(logger, stn_metadata_dict, lon_2d, lat_2d, print_flag)
# version history 
#   02/18/2016 - ported from 2.7 to 3.5
# to do: 
#   - 
# notes: 
#   - 
# debugging: 
#   - 
#
###############################################################################



###############################################################################
# 
 
def map_stn_locations_to_grid_locations(logger, stn_metadata_dict, lon_2d, lat_2d, print_flag):

    #import pandas 
    #import os 
    import numpy 
     
    #numpy.shape(stn_lon_temp)     
    #numpy.shape(stn_lon_temp)     
    #numpy.shape(lat_temp)     
    #numpy.shape(lon_temp)
    #numpy.nanmin(lon_2d)
    #numpy.nanmax(lon_2d)    
    #numpy.nanmin(lat_2d)
    #numpy.nanmax(lat_2d)
    #[ny_temp, nx_temp] = numpy.shape(lat_2d)
    
    i_loc_s = numpy.zeros([stn_metadata_dict['n_stn']], dtype='int') 
    j_loc_s = numpy.zeros([stn_metadata_dict['n_stn']], dtype='int') 
    s = 0
    for s in range(0, stn_metadata_dict['n_stn'], 1):
        total_diff_2d = numpy.abs(lon_2d - stn_metadata_dict['stn_lon'][s]) + numpy.abs(lat_2d - stn_metadata_dict['stn_lat'][s])
        #[j_loc_s[s], i_loc_s[s]] = numpy.unravel_index(total_diff_2d.argmin(), total_diff_2d.shape)
        [j_loc_s[s], i_loc_s[s]] = numpy.argwhere(total_diff_2d == numpy.min(total_diff_2d))[0]
        del total_diff_2d        
        
    #indices = []
    #i_loc   = []
    #j_loc   = []    
    #for stn_i, stn_lon_lat in enumerate(zip(stn_metadata_dict['stn_lon'], stn_metadata_dict['stn_lat'])):
    #    # print stn_i, stn_lon_lat
    #    total_diff = numpy.abs(lon_2d - stn_lon_lat[0]) + numpy.abs(lat_2d - stn_lon_lat[1])
    #    #total_diff = numpy.abs(lon_wrf - stn_lon_temp) + numpy.abs(lat_wrf - stn_lat_temp)
    #    # argmin returns the flattened index, use unravel to get the 2d index
    #    indices.append(numpy.unravel_index(total_diff.argmin(), total_diff.shape))
    #    temp1 = indices[stn_i]
    #    i_loc.append(temp1[1])
    #    j_loc.append(temp1[0])
    #    del total_diff
    #    del temp1         

    # using grid_id instead 
    #s = 0
    #for s in range(0, stn_metadata_dict['n_stn'], 1):
    #    total_diff = numpy.abs(lon_2d - stn_metadata_dict['stn_lon'][s]) + numpy.abs(lat_2d - stn_metadata_dict['stn_lat'][s])
    #    # argmin returns the flattened index, use unravel to get the 2d index
    #    grid_id_s[s] = grid_id[total_diff.argmin()]

    if (print_flag):
        s = 0
        for s in range(0, stn_metadata_dict['n_stn'], 1): 
            print ('processing s %s of %s ' % (s, stn_metadata_dict['n_stn']))
            print ('  lon expected %2.2f found %2.2f ' % (stn_metadata_dict['stn_lon'][s], lon_2d[j_loc_s[s],i_loc_s[s]]))
            print ('  lat expected %2.2f found %2.2f ' % (stn_metadata_dict['stn_lat'][s], lat_2d[j_loc_s[s],i_loc_s[s]]))

            #print ('stn # ',"{:2.0f}".format(stn+1),' lat expected/found ',"{:5.2f}".format(stn_lat_temp[stn]),' / ',"{:5.2f}".format(lat_temp[j_loc[stn],i_loc[stn]]),' lon expected/found ',"{:5.2f}".format(stn_lon_temp[stn]),' / ',"{:5.2f}".format(lon_temp[j_loc[stn],i_loc[stn]]))  
            #print ('processing stn = ',"{:3.0f}".format(stn+1),' of ',"{:3.0f}".format(n_stn_temp))  
            #print ('stn # ',"{:2.0f}".format(stn+1),' lat expected/found ',"{:5.2f}".format(stn_lat_temp[stn]),' / ',"{:5.2f}".format(lat_temp[j_loc[stn],i_loc[stn]]),' lon expected/found ',"{:5.2f}".format(stn_lon_temp[stn]),' / ',"{:5.2f}".format(lon_temp[j_loc[stn],i_loc[stn]]))  
            
    return j_loc_s, i_loc_s 

    #if (print_flag):
    #    for s in range(0, stn_metadata_dict['n_stn'], 1): 
    #        print ('  s %s of %s ' % (s, stn_metadata_dict['n_stn']))
    #        print ('  lon expected %s found %s ' % (stn_metadata_dict['stn_lon'][s], grid_lon[grid_id_s[s]]))
    #        print ('  lat expected %s found %s ' % (stn_metadata_dict['stn_lat'][s], grid_lat[grid_id_s[s]]))

# 
###############################################################################

