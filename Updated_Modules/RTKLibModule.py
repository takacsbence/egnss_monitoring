#!/usr/bin/env python3

"""
    run RTKLIB to evaluate GNSS performance in the Hungarian E-GNSS network
    unzip raw septentrio binary files
    convert them into RINEX
    convert rtcm messages from reference station to RINEX
    run rnx2rtkp t post-process RINEX files in several positioning modes
    call GrpahModule to generate true position error plots
"""

import os
import zipfile
from datetime import datetime, timedelta
import shutil

def hour2session(hour):
    """ get abc session from hour, a = 0, b = 1, ...
        :param:     hour
        :returns:   abc session
    """

    session_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                    'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w']
    return session_list[int(hour)]

def date2doy(dt):
    """ get date and time parameters from computer time
        :param:     dt timedelta in hour
        :returns:   year (4 characters)
                    year2 last two characters of the year
                    doy day of year
                    hour
                    hour2 with leading zeros, like 02
    """

    last_hour_date_time = datetime.utcnow() - timedelta(hours=dt)
    doy = last_hour_date_time.strftime("%j")
    year = last_hour_date_time.strftime("%Y")
    year2 = last_hour_date_time.strftime("%y")
    hour = last_hour_date_time.strftime("%H")
    hour2 = f'{int(hour):02d}'

    return year, year2, doy, hour, hour2
        
def GraphCaller():
    call = "python3 " + graph + "GraphModule.py " + raw_data_folder + " " + pos_file + " " +station + " " + year + " " + doy
    os.system(call)

def raw_file(work_folder, station, dt):
    """ get raw file name and path from date and time parameters
        :param:     folder where temporary files are stored
                    station id, like 205
                    timedelta in hours
        :returns:   raw data folder
                    raw data file
    """

    #date and time parameters
    year, year2, doy, hour, hour2 = date2doy(dt)

    #convert hour to abc session
    session = hour2session(hour)

    #zipped raw data folder
    zipped_raw_data_folder = '/home/tbence/HC/data/Y' + year + '/D' + doy + '/PildoBox' + station + '/'

    #processed data folder
    raw_data_folder = work_folder + 'Y' + year + '/D' + doy + '/PildoBox' + station  + '/'

    #raw file name
    raw_data_file = 'PildoBox' + station + year2 + doy + session + ".raw.zip"

    #concat path and filename
    zipped_raw_data_file = zipped_raw_data_folder + raw_data_file
    #unzip raw file
    if os.path.exists(zipped_raw_data_file):
        with zipfile.ZipFile(zipped_raw_data_file, 'r') as zip_file:
            zip_file.extractall(raw_data_folder)

    #remove .zip extension
    raw_data_file = raw_data_file[:-4]

    return raw_data_folder, raw_data_file

if __name__ == "__main__":

    #list of stations
    stations = ['205', '215']   #more stations
    stations = ['205']  #just one station, for testing

    #reference station data folder
    ref_data_save = '/home/tbence/Paripa/Reference_for_Kinematic/'
    #conf file folder
    conf_folder = '/home/tbence/Paripa/conf/'
    #working folder
    work_folder = '/home/hegyi/Paripa/Downloaded_zips/'
    #GraphModule folder
    graph = "/home/hegyi/Paripa/Paripa1/"

    for station in stations:

        #current raw file
        raw_data_folder, raw_data_file = raw_file(work_folder, station, 1)
        #previous raw file
        raw_data_folder_p, raw_data_file_p = raw_file(work_folder, station, 2)

        #concat these two files
        with open(raw_data_folder_p + raw_data_file_p, "ab") as myfile, open(raw_data_folder + raw_data_file, "rb") as file2:
            myfile.write(file2.read())

        #convert RTCM raw binary reference file to RINEX
        #egyelőre fixen BUTE0
        year, year2, doy, hour, hour2 = date2doy(1)
        rtcm_folder = ref_data_save + 'BUTE0/'
        rtcm_file_name = 'BUTE0' + year2 + doy + hour2 + '.rtcm'
        if os.path.exists(rtcm_folder + rtcm_file_name):
            ref_obs_file = 'BUTE0' + year2 + doy + hour2 + ".obs"
            convert_rtcm = "/usr/local/bin/convbin " + rtcm_folder + rtcm_file_name + " -r rtcm3 -v 3.03 -o " + raw_data_folder + ref_obs_file
            os.system(convert_rtcm)

        #convert septentrio raw binary files to RINEX
        if os.path.exists(raw_data_folder + raw_data_file):
            #observation file
            obs_file = raw_data_file[:-3] + 'obs'
            convert_to_Rinex = "/usr/local/bin/convbin " + raw_data_folder + raw_data_file + " -v 3.03 -r sbf -d " + raw_data_folder
            os.system(convert_to_Rinex)

            #navigation file, mixed
            nav_file = raw_data_file[:-3] + 'nav'
            convert_to_Rinex = "/opt/Septentrio/RxTools/bin/sbf2rin -f " + raw_data_folder_p + raw_data_file_p + " -R3 -n P -o " + raw_data_folder + nav_file
            os.system(convert_to_Rinex)

        #post processing
            #SPP - GPS
            pos_file = raw_data_file[:-4] + '_spp.pos'
            conf = conf_folder + 'SSSS_sps.conf'
            pp = "/usr/local/bin/rnx2rtkp -k " + conf + " -p 0 " + raw_data_folder + obs_file + " " + raw_data_folder + nav_file + " -o " + raw_data_folder + pos_file
            os.system(pp)
            #generate plots
            #gr = "python3 " + graph + "GraphModule.py " + raw_data_folder + " " + pos_file + " " + station
            #os.system(gr)
            GraphCaller()

            #SPP - GPS+GAL
            pos_file = raw_data_file[:-4] + '_spp_G.pos'
            conf = conf_folder + 'SSSS_sps_gal.conf'
            pp = "/usr/local/bin/rnx2rtkp -k " + conf + " -p 0 " + raw_data_folder + obs_file + " " \
                    + raw_data_folder + nav_file + " -o " + raw_data_folder + pos_file
            os.system(pp)
            #generate plots
            #gr = "python3 " + graph + "GraphModule.py " + raw_data_folder + " " + pos_file + " " + station
            #os.system(gr)
            GraphCaller()

            #SBAS - GPS
            sbs_file = raw_data_file[:-3] + 'sbs'
            pos_file = raw_data_file[:-4] + '_sbas.pos'
            conf = conf_folder + 'SSSS_sbs.conf'
            pp = "/usr/local/bin/rnx2rtkp -k " + conf + " -p 0 " + raw_data_folder + obs_file + " " + raw_data_folder + sbs_file + " " \
                    + raw_data_folder + nav_file + " -o " + raw_data_folder + pos_file
            os.system(pp)
            #generate plots
            #gr = "python3 " + graph + "GraphModule.py " + raw_data_folder + " " + pos_file + " " + station
            #os.system(gr)
            GraphCaller()

            #RTK - GPS
            pos_file = raw_data_file[:-4] + '_rtk.pos'
            conf = conf_folder + 'SSSS_rtk.conf'
            pp = "/usr/local/bin/rnx2rtkp -k " + conf + " -p 2 " + raw_data_folder + obs_file + " " + raw_data_folder + ref_obs_file + " " \
                    + raw_data_folder + nav_file + " -r 4081882.37127 1410011.14595 4678199.39545" + " -o " + raw_data_folder + pos_file
            os.system(pp)
            #generate plots
            #gr = "python3 " + graph + "GraphModule.py " + raw_data_folder + " " + pos_file + " " + station
            #os.system(gr)
            GraphCaller()
            
            #RTK - GPS+GAL
            pos_file = raw_data_file[:-4] + '_rtk_G.pos'
            conf = conf_folder + 'SSSS_rtk_gal.conf'
            pp = "/usr/local/bin/rnx2rtkp -k " + conf + " -p 2 " + raw_data_folder + obs_file + " " + raw_data_folder + ref_obs_file + " " \
                    + raw_data_folder + nav_file + " -r 4081882.37127 1410011.14595 4678199.39545" + " -o " + raw_data_folder + pos_file
            os.system(pp)
            #generate plots
            #gr = "python3 " + graph + "GraphModule.py " + raw_data_folder + " " + pos_file + " " + station
            #os.system(gr)
            GraphCaller()
            
            #DGPS - GPS
            pos_file = raw_data_file[:-4] + '_dgps.pos'
            conf = conf_folder + 'SSSS_dgps.conf'
            pp = "/usr/local/bin/rnx2rtkp -k " + conf + " -p 2 " + raw_data_folder + obs_file + " " + raw_data_folder + ref_obs_file + " " \
                    + raw_data_folder + nav_file + " -r 4081882.37127 1410011.14595 4678199.39545" + " -o " + raw_data_folder + pos_file
            os.system(pp)
            GraphCaller()
            
            #DGPS - GPS+GAL
            pos_file = raw_data_file[:-4] + '_dgps_G.pos'
            conf = conf_folder + 'SSSS_dgps_gal.conf'
            pp = "/usr/local/bin/rnx2rtkp -k " + conf + " -p 2 " + raw_data_folder + obs_file + " " + raw_data_folder + ref_obs_file + " " \
                    + raw_data_folder + nav_file + " -r 4081882.37127 1410011.14595 4678199.39545" + " -o " + raw_data_folder + pos_file
            os.system(pp)
            GraphCaller()

        #delete raw data folder
        #shutil.rmtree(raw_data_folder)
