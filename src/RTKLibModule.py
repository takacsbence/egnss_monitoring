#!/usr/bin/env python3

"""
    run RTKLIB to evaluate GNSS performance in the Hungarian E-GNSS network
    unzip raw septentrio binary files
    convert them into RINEX
    convert rtcm messages from reference station to RINEX
    run rnx2rtkp to post-process RINEX files in several positioning modes
    plot true position error plots 
    store statistical paramteres into psql database
    
    written by Hegyi Lehel and Takács Bence
    last modified: 2024.05.24.
    
    TODO:
    -
    
"""

import sys
import json
import os
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from math import pi, cos, radians
import shutil
import subprocess
import pandas as pd
from GraphModule import header_lines, plot_gen, dbase_write

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

def graph_caller2(pic_folder, graph_folder, JNAME, raw_data_folder, pos_file, station, year, doy, ref, data_stations):
    """
        compute and plot true position errors and store data into database
    """
    #output file
    pic_save = Path(pic_folder + '/Y' + year + '/D' + doy +'/PildoBox' + station)
    pic_save.mkdir(parents=True, exist_ok=True)
    pic_name = str(pic_save) + '/' + pos_file[:-3] + 'png'

    #index of current station
    station = 'PildoBox' + station
    idx = data_stations[data_stations['id'] == station].index.item()

    #true coordinates of rover
    ref_lat = data_stations['lat'][idx]
    ref_lon = data_stations['long'][idx]
    ref_ele = data_stations['elev'][idx]

    #1 arc seconds in latitude corresponds to ~31 m on the surface of the Earth
    dlat = pi / 180 * 6380000 / 3600

    #info from pos file header
    ct, mode, navi_sys = header_lines(raw_data_folder + pos_file)

    #load pos file
    data_gps = pd.read_csv(raw_data_folder + pos_file, header=None,
                           delim_whitespace=True, skiprows=ct)
    data_gps.columns = ["date", "time", "lat", "lon", "ele", "mode", "nsat", "stdn", "stde",
                        "stdu", "stdne", "stdeu", "stdun", "age", "ratio"]
    print(data_gps.shape[0], 'positions read from', pos_file)
    data_gps['datetime'] = pd.to_datetime(data_gps['date'] + ' ' + data_gps['time'],
                                          format='%Y/%m/%d %H:%M:%S.%f')

    #coordinate errors
    data_gps['EW_error'] = (data_gps['lon'] - ref_lon) * dlat * cos(radians(ref_lat)) * 3600
    data_gps['SN_error'] = (data_gps['lat'] - ref_lat) * dlat * 3600
    data_gps['ELE_error'] = data_gps['ele'] - ref_ele
    
    if mode == 'ppp':

        #in PPP mode we have to correct by ITRS-ETRF manually, values need to be confirmed
        data_gps['EW_error'] = data_gps['EW_error'] - 0.724
        data_gps['SN_error'] = data_gps['SN_error'] - 0.580

    #generate plots
    mode_i = plot_gen(data_gps, mode, navi_sys, station, ref, pic_name)

    #write statistical parameters into psql database
    dbase_write(dbase_name, data_gps, int(station[-3:]), mode, navi_sys, mode_i, ref)


def raw_file(rov_data_save, work_folder, station, dt):
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
    zipped_raw_data_folder = rov_data_save + 'Y' + year + '/D' + doy + '/PildoBox' + station + '/'

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
        rov_data_save = JDATA["rov_data_save"]  #rover station data folder
        ref_data_save = JDATA["ref_data_save"]  #reference station data folder
        work_folder = JDATA["work_folder"]      #working folder
        graph_folder = JDATA["graph_folder"]    #GraphModule folder
        log_file = JDATA["log"]
        pic_folder = JDATA["pic_folder"]    #folder to save graph pictures
        dbase_name = JDATA["dbase_name"]    #psql dbase name

    #open log file
    #log_file = open(log_file, 'a')

    #load stations.txt file with true position of stations
    data_stations = pd.read_csv('/home/tbence/Paripa/rov_stations.txt',
                                header=None, delim_whitespace=True)
    data_stations.columns = ["id", "city", "lat", "long", "elev"]

    #load ref_stations.txt file with true position of reference stations
    ref_stations_data = pd.read_csv('/home/tbence/Paripa/ref_stations.txt',
                                    header=None, delim_whitespace=True)
    ref_stations_data.columns = ["id", "X", "Y", "Z"]

    #loop over rover stations
    dt = 1  #time difference in hour, dt =1 -> previous hour
    for i, station in enumerate(rov_stations):
        year, year2, doy, hour, hour2 = date2doy(dt)

        #current raw file
        raw_data_folder, raw_data_file = raw_file(rov_data_save, work_folder, station, dt)
        #previous raw file
        raw_data_folder_p, raw_data_file_p = raw_file(rov_data_save, work_folder, station, dt + 1)

        #concat these two files
        if os.path.exists(raw_data_folder_p + raw_data_file_p):
            with open(raw_data_folder_p + raw_data_file_p, "ab") as myfile, open(raw_data_folder + raw_data_file, "rb") as file2:
                myfile.write(file2.read())

        #convert septentrio raw binary files to RINEX
        if not os.path.exists(raw_data_folder + raw_data_file):
            """
            log_file.write(datetime.now().strftime("%m/%d/%Y, %H:%M:%S" ) + raw_data_folder +
                           raw_data_file + ' does not exist')
            print(raw_data_folder + raw_data_file, 'does not exist')
            log_file.close()
            """
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
                        
        #ssr corrections
        rtcm_ssr_folder = ref_data_save + 'SSRA00BKG0/'
        rtcm_ssr_file_name = 'SSRA00BKG0' + year2 + doy + hour2 + '.rtcm'
        if not os.path.exists(rtcm_ssr_folder + rtcm_ssr_file_name + '3'):
            os.rename(rtcm_ssr_folder + rtcm_ssr_file_name, rtcm_ssr_folder + rtcm_ssr_file_name + '3')
        rtcm_ssr_file_name = rtcm_ssr_file_name + '3'
        
        #index of current reference station
        try:
            ref_idx = ref_stations_data[ref_stations_data['id'] == ref_stations[i]].index.item()

            #coordinates of reference station
            ref_name = ref_stations_data['id'][ref_idx]
            #ref_X = ref_stations_data['X'][ref_idx]
            #ref_Y = ref_stations_data['Y'][ref_idx]
            #ref_Z = ref_stations_data['Z'][ref_idx]

            #convert RTCM raw binary reference file to RINEX
            rtcm_folder = ref_data_save + ref_name + '/'
            rtcm_file_name = ref_name + year2 + doy + hour2 + '.rtcm'
            if os.path.exists(rtcm_folder + rtcm_file_name):
                ref_obs_file = ref_name + year2 + doy + hour2 + ".obs"
                subprocess.run(["/usr/local/bin/convbin", rtcm_folder + rtcm_file_name,
                                "-r", "rtcm3", "-v", "3.03", "-o", raw_data_folder + ref_obs_file])
        except IndexError:
            ref_idx = -1

        #index of DGPS reference station
        try:
            ref_idx_dgps = 0 #BUTE0 by default

            #coordinates of reference station
            ref_name_dgps = ref_stations_data['id'][ref_idx_dgps]
            ref_X_dgps = ref_stations_data['X'][ref_idx_dgps]
            ref_Y_dgps = ref_stations_data['Y'][ref_idx_dgps]
            ref_Z_dgps = ref_stations_data['Z'][ref_idx_dgps]

            #convert RTCM raw binary reference file to RINEX
            rtcm_folder_dgps = ref_data_save + ref_name_dgps + '/'
            rtcm_file_name_dgps = ref_name_dgps + year2 + doy + hour2 + '.rtcm'
            if os.path.exists(rtcm_folder_dgps + rtcm_file_name_dgps):
                ref_obs_file_dgps = ref_name_dgps + year2 + doy + hour2 + ".obs"
                subprocess.run(["/usr/local/bin/convbin", rtcm_folder_dgps + rtcm_file_name_dgps,
                                "-v", "3.03", "-r", "rtcm3", "-o",
                                raw_data_folder + ref_obs_file_dgps])
        except IndexError:
            ref_idx_dgps = -1


        #post processing
        #SPP - GPS
        pos_file = raw_data_file[:-4] + '_spp.pos'
        conf = conf_folder + 'SSSS_sps.conf'
        subprocess.run(["/usr/local/bin/rnx2rtkp", "-k", conf, "-p", "0",
                        raw_data_folder + obs_file, raw_data_folder + nav_file, "-o",
                        raw_data_folder + pos_file])
        ref = ""
        graph_caller2(pic_folder, graph_folder, JNAME, raw_data_folder, pos_file, station, year, doy, ref, data_stations)

        #SPP - GPS+GAL
        pos_file = raw_data_file[:-4] + '_spp_G.pos'
        conf = conf_folder + 'SSSS_sps_gal.conf'
        subprocess.run(["/usr/local/bin/rnx2rtkp", "-k", conf, "-p", "0",
                        raw_data_folder + obs_file, raw_data_folder + nav_file, "-o",
                        raw_data_folder + pos_file])
        ref = ""
        graph_caller2(pic_folder, graph_folder, JNAME, raw_data_folder, pos_file, station, year, doy, ref, data_stations)

        #SBAS - GPS
        pos_file = raw_data_file[:-4] + '_sbas.pos'
        conf = conf_folder + 'SSSS_sbs.conf'
        subprocess.run(["/usr/local/bin/rnx2rtkp", "-k", conf, "-p", "0", 
                        raw_data_folder + obs_file, raw_data_folder + sbs_file, 
                        raw_data_folder + nav_file, "-o", raw_data_folder + pos_file])
        ref = ""
        graph_caller2(pic_folder, graph_folder, JNAME, raw_data_folder, pos_file, station, year, doy, ref, data_stations)

        #RTK
        if ref_idx > -1 and os.path.exists(rtcm_folder + rtcm_file_name):

            #RTK - GPS
            pos_file = raw_data_file[:-4] + '_rtk.pos'
            conf = conf_folder + 'rtk_gps.conf'
            subprocess.run(["/usr/local/bin/rnx2rtkp", "-k", conf, "-p", "2",
                            raw_data_folder + obs_file, raw_data_folder + ref_obs_file,
                            raw_data_folder + nav_file, 
                            "-o", raw_data_folder + pos_file])
            graph_caller2(pic_folder, graph_folder, JNAME, raw_data_folder, pos_file, station, year, doy, ref_name, data_stations)

            #RTK - GPS+GAL
            pos_file = raw_data_file[:-4] + '_rtk_G.pos'
            conf = conf_folder + 'rtk_gal.conf'
            subprocess.run(["/usr/local/bin/rnx2rtkp", "-k", conf, "-p", "2",
                            raw_data_folder + obs_file, raw_data_folder + ref_obs_file,
                            raw_data_folder + nav_file, 
                            "-o", raw_data_folder + pos_file])
            graph_caller2(pic_folder, graph_folder, JNAME, raw_data_folder, pos_file, station, year, doy, ref_name, data_stations)

        #DGPS
        if ref_idx_dgps > -1 and os.path.exists(rtcm_folder_dgps + rtcm_file_name_dgps):

            #DGPS - GPS
            pos_file = raw_data_file[:-4] + '_dgps.pos'
            conf = conf_folder + 'SSSS_dgps.conf'
            subprocess.run(["/usr/local/bin/rnx2rtkp", "-k", conf, "-p", "1",
                            raw_data_folder + obs_file, raw_data_folder + ref_obs_file_dgps,
                            raw_data_folder + nav_file,
                            str(ref_Z_dgps), "-o", raw_data_folder + pos_file])
            graph_caller2(pic_folder, graph_folder, JNAME, raw_data_folder, pos_file, station, year, doy, ref_name_dgps, data_stations)

            #DGPS - GPS+GAL
            pos_file = raw_data_file[:-4] + '_dgps_G.pos'
            conf = conf_folder + 'SSSS_dgps_gal.conf'
            subprocess.run(["/usr/local/bin/rnx2rtkp", "-k", conf, "-p", "1",
                            raw_data_folder + obs_file, raw_data_folder + ref_obs_file_dgps,
                            raw_data_folder + nav_file,
                            str(ref_Z_dgps), "-o", raw_data_folder + pos_file])
            graph_caller2(pic_folder, graph_folder, JNAME, raw_data_folder, pos_file, station, year, doy, ref_name, data_stations)

        #SSR
        pos_file = raw_data_file[:-4] + '_ssr.pos'
        conf = conf_folder + 'ssr.conf'
        subprocess.run(["/usr/local/bin/rnx2rtkp", "-k", conf, "-p", "7", 
                        raw_data_folder + obs_file, raw_data_folder + nav_file,
                        rtcm_ssr_folder + rtcm_ssr_file_name, "-o", raw_data_folder + pos_file])
        ref_name = ""
        graph_caller2(pic_folder, graph_folder, JNAME, raw_data_folder, pos_file, station, year, doy, ref_name, data_stations)

        #delete raw data folder
        if os.path.exists(raw_data_folder) and os.path.isdir(raw_data_folder):
            shutil.rmtree(raw_data_folder)
        if os.path.exists(raw_data_folder_p) and os.path.isdir(raw_data_folder_p):
            shutil.rmtree(raw_data_folder_p)
