#!/usr/bin/env python3

"""
    check files size in HC Paripa project
"""

import os
from datetime import datetime, timedelta
import psycopg2

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

    last_hour_date_time = (datetime.utcnow() - timedelta(hours=dt)).replace(microsecond=0, second=0, minute=0)
    doy = last_hour_date_time.strftime("%j")
    year = last_hour_date_time.strftime("%Y")
    year2 = last_hour_date_time.strftime("%y")
    hour = last_hour_date_time.strftime("%H")
    hour2 = f'{int(hour):02d}'

    return year, year2, doy, hour, hour2, last_hour_date_time

def dbase(station_id, last_hour_date_time, file_size):
    """
        write data to database
        :param:     station id, like 205, BUTE0
                    last_hour_date_time, datetime object of last truncated hour
                    file_size, file size of the file in byte
    """
    #data base connection
    conn = psycopg2.connect("dbname=" + 'hegyi')

    #create a cursor
    cur = conn.cursor()

    #create table
    sql_create_table = "CREATE TABLE IF NOT EXISTS paripa_files (id SERIAL PRIMARY KEY, station_id VARCHAR, file_size INT, datetime TIMESTAMP, unique(station_id, datetime));"
    cur.execute(sql_create_table)

    #insert a new row
    val_cols = ", ".join(["'{}'".format(station_id), "'{}'".format(last_hour_date_time), "'{}'".format(file_size)])

    sql = "INSERT INTO paripa_files(station_id, datetime, file_size) VALUES(" + val_cols + ");"
    #print(sql)
    cur.execute(sql)

    # close the communication with the PostgreSQL
    conn.commit()
    cur.close()
    conn.close()

def raw_file(work_folder, station, dt):
    """
        :param:     folder where zipped raw eptentrio binary files are stored
                    station id, like 205
                    timedelta in hours
    """

    #date and time parameters
    year, year2, doy, hour, hour2, last_hour_date_time = date2doy(dt)

    #convert hour to abc session
    session = hour2session(hour)

    #zipped raw data folder
    zipped_raw_data_folder = '/home/tbence/HC/data/Y' + year + '/D' + doy + '/PildoBox' + station + '/'

    #raw file name
    raw_data_file = 'PildoBox' + station + year2 + doy + session + ".raw.zip"

    #concat path and filename
    zipped_raw_data_file = zipped_raw_data_folder + raw_data_file

    #unzip raw file
    if os.path.exists(zipped_raw_data_file):
        file_size = os.path.getsize(zipped_raw_data_file)
    else:
        file_size = 0

    dbase(station_id, last_hour_date_time, file_size)
    print(station_id, last_hour_date_time, file_size, zipped_raw_data_file)

def ref_file(folder, station, dt):
    """
        :param:     folder where rtcm data of reference stations are stored
                    station id, like BUTE
                    timedelta in hours
        :returns:   file_size
    """

    #date and time parameters
    year, year2, doy, hour, hour2, last_hour_date_time = date2doy(dt)

    #raw data folder
    rtcm_folder = folder + station + '/'

    #raw file name
    rtcm_file_name = station + year2 + doy + hour2 + '.rtcm'

    #concat path and filename
    rtcm_data_file = rtcm_folder + rtcm_file_name

    #check file size
    if os.path.exists(rtcm_data_file):
        file_size = os.path.getsize(rtcm_data_file)
    else:
        file_size = 0

    dbase(station, last_hour_date_time, file_size)
    print(station, last_hour_date_time, file_size, rtcm_data_file)

if __name__ == "__main__":

    hc_data_folder = "/home/tbence/HC/data/"
    rtcm_folder = "/home/tbence/Paripa/Reference_for_Kinematic/"
    dt = 4

    #HC stations
    for station_id in range(205, 216):
        raw_file(hc_data_folder, str(station_id), dt)

    #Reference stations
    for station_id in ['BUTE0', 'BME10', 'ZZON0']:
        ref_file(rtcm_folder, station_id, dt)
