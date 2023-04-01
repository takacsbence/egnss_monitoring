#!/usr/bin/env python3

"""
    run RTKLIB to evaluate GNSS performance in the Hungarian E-GNSS network
    unzip raw septentrio binary files
    convert them into RINEX
    convert rtcm messages from reference station to RINEX
    run rnx2rtkp to post-process RINEX files in kinematic modes, having different reference stations
    call GraphModule to generate true position error plots
"""

import sys
import json
import os
import zipfile
from datetime import datetime, timedelta
import shutil
import pandas as pd
import subprocess

def hour2session(hour):
    """ get abc session from hour, a = 0, b = 1, ...
        :param:     hour
        :returns:   abc session
    """

    session_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n',
                    'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x']
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

def graph_caller(graph_folder, JNAME, raw_data_folder, pos_file, station, year, doy, ref):
    """
        call GraphModule.py to plot true position errors
    """
    subprocess.run(["python3", graph_folder + "GraphModule.py", JNAME, raw_data_folder, pos_file, station, year, doy, ref])

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

    #check number of arguments
    if len(sys.argv) != 2:
        print('wrong number of arguments')
        print('use', sys.argv[0], 'json_file')
        exit()

    #json file name as the first argument from command prompt
    JNAME = str(sys.argv[1])
    if not os.path.exists(JNAME):
        print(JNAME, 'json file does not exist')
        exit()

    #load json file and get config parameters
    with open(JNAME) as jfile:
        JDATA = json.load(jfile)
        conf_folder = JDATA["conf_folder"]      #folder of RTKLIB config files
        rov_stations = JDATA["rov_stations"]    #list of rover stations
        ref_stations = JDATA["ref_stations"]    #list of reference stations
        ref_data_save = JDATA["ref_data_save"]  #reference station data folder
        work_folder = JDATA["work_folder"]      #working folder
        graph_folder = JDATA["graph_folder"]    #GraphModule folder
        log_file = JDATA["log"]

    #open log file
    log_file = open(log_file, 'a+')

    #loop over rover stations
    for i, station in enumerate(rov_stations):
        dt = 1
        year, year2, doy, hour, hour2 = date2doy(dt)

        #current raw file
        raw_data_folder, raw_data_file = raw_file(work_folder, station, dt)
        #previous raw file
        raw_data_folder_p, raw_data_file_p = raw_file(work_folder, station, dt + 1)

        #concat these two files
        if os.path.exists(raw_data_folder_p + raw_data_file_p):
            with open(raw_data_folder_p + raw_data_file_p, "ab") as myfile, open(raw_data_folder + raw_data_file, "rb") as file2:
                myfile.write(file2.read())

        #convert septentrio raw binary files to RINEX
        if not os.path.exists(raw_data_folder + raw_data_file):
            #log_file.write(datetime.now().strftime("%m/%d/%Y, %H:%M:%S" ) + raw_data_folder + raw_data_file + ' does not exist')
            #log_file.close()
            continue

        #observation file
        obs_file = raw_data_file[:-3] + 'obs'
        subprocess.run(["/usr/local/bin/convbin", raw_data_folder + raw_data_file, "-v", "3.03",
                        "-r", "sbf", "-ha", "1/AERAT1675_382   NONE", "-d", raw_data_folder])

        #navigation file, mixed
        nav_file = raw_data_file[:-3] + 'nav'
        subprocess.run(["/opt/Septentrio/RxTools/bin/sbf2rin", "-f", raw_data_folder_p +
                        raw_data_file_p, "-R3", "-n", "P", "-o", raw_data_folder + nav_file])

        #sbas messages
        sbs_file = raw_data_file[:-3] + 'sbs'
        subprocess.run(["/usr/local/bin/convbin", raw_data_folder_p + raw_data_file_p, "-v", "3.03",
                        "-r", "sbf", "-s", raw_data_folder + sbs_file])

        #convert RTCM raw binary reference file to RINEX
        ref_name = ref_stations[i]
        rtcm_folder = ref_data_save + ref_name + '/'
        rtcm_file_name = ref_name + year2 + doy + hour2 + '.rtcm'
        if os.path.exists(rtcm_folder + rtcm_file_name):
            ref_obs_file = ref_name + year2 + doy + hour2 + ".obs"
            subprocess.run(["/usr/local/bin/convbin", rtcm_folder + rtcm_file_name,
                            "-r", "rtcm3", "-v", "3.03", "-o", raw_data_folder + ref_obs_file])

            #RTK - GPS post processing
            pos_file = raw_data_file[:-4] + '_rtk.pos'
            conf = conf_folder + 'SSSS_rtk.conf'
            """
            subprocess.run(["/usr/local/bin/rnx2rtkp", "-k", conf, "-p", "2",
                            raw_data_folder + obs_file, raw_data_folder + ref_obs_file,
                            raw_data_folder + nav_file, "-r", str(ref_X), str(ref_Y), str(ref_Z),
                            "-o", raw_data_folder + pos_file])
            graph_caller()
            """

            #RTK - GPS+GAL post processing
            pos_file = raw_data_file[:-4] + '_' + ref_name + '.pos'
            conf = conf_folder + 'rtk_gal.conf'
            
            subprocess.run(["/usr/local/bin/rnx2rtkp", "-k", conf, "-p", "2",
                            raw_data_folder + obs_file, raw_data_folder + ref_obs_file,
                            raw_data_folder + nav_file, 
                            "-o", raw_data_folder + pos_file])
            graph_caller(graph_folder, JNAME, raw_data_folder, pos_file, station, year, doy, ref_name)

        #delete raw data folder
        print(raw_data_folder)
        shutil.rmtree(raw_data_folder)
