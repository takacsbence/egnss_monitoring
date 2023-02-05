#!/usr/bin/env python3

"""
    generate true position error plot from RTKLIB pos file
    write statistical parameters into database
"""

import sys
import os
import json
import warnings
from pathlib import Path
from math import pi, cos, radians
import pandas as pd
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import psycopg2

def header_lines(posfile):

    """ get data from RTKLIB position file header
        :param:     RTKLIB pos file
        :returns:   the number of header lines (header lines strats by "%")
                    solution mode (single, kinematic)
                    navigation systems (GPS, GPS GALILEO, GPS SBAS)
    """
    ct = 0
    navi_sys = 'GPS'
    mode = 'single'
    file = open(posfile, 'r')
    lines = file.readlines()
    for line in lines:
        ct += 1
        if line.find('% pos mode') == 0:
            mode = line.split()[4]
        if line.find('% navi sys') == 0:
            navi_sys = ' '.join(line.split()[4:]).upper()
        if line.find('%') == -1:
            file.close()
            break
    return ct, mode, navi_sys

def plot_gen(data, mode, navi_sys, station, ref, pic_name):
    """ generate true position error plots
        :param: pandas dataframe with data
        :param: solutuion mode, like single or kinematic
        :param: navigation system, like GPS or GPS GALILEO
        :param: station id, like 205
        :param: reference station name
        :param: plot image file name
        :returns: mode_i (SPP:5, DGPS:4, SBAS:3, RTK fix:1)
    """

    #plot
    fig, ax = plt.subplots()

    ax.plot(data['datetime'], data['EW_error'], label='East-West')
    ax.plot(data['datetime'], data['SN_error'], label='North-South')
    ax.plot(data['datetime'], data['ELE_error'], label='Up-Down')

    #solution mode
    if mode == 'kinematic':
        ymax = 0.4
        title = 'RTK'
        mode_i = 1      #fix solutions
    elif mode == 'single':
        ymax = 10
        title = 'SPP'
        mode_i = 5      #SPP solutions
        if navi_sys == 'GPS SBAS':
            mode_i = 3  #SBAS solutions
    elif mode == 'dgps':
        ymax = 10
        title = 'DGPS'
        mode_i = 4      #DGPS solutions
    else:
        ymax = 10

    #parameters
    ax.set_ylim([-ymax, ymax])
    # show exactly one hour session
    dtmin = min(data['datetime']).round('60min').to_pydatetime()
    dtmax = max(data['datetime']).round('60min').to_pydatetime()
    ax.set_xlim([dtmin, dtmax])
    ax.yaxis.set_major_locator(plt.MaxNLocator(8))
    ax.set_xlabel('time (hh:mm)')
    ax.set_ylabel('Coordinate errors [meters]')
    ax.set_title('Position Error Graph ' + title + " " + navi_sys)
    ax.legend(loc=2)
    ax.grid()

    #number of satellites
    ax2 = ax.twinx()
    ax2.plot(data['datetime'], data['nsat'], label='# of satellites', color='red')
    ax2.plot(data['datetime'], data['mode'], label='solution mode', color='purple')
    ax2.set_ylim([0, 24])
    ax2.yaxis.set_major_locator(plt.MaxNLocator(8))
    ax2.set_ylabel('# of satellites / solution mode')
    ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    ax2.legend(loc=1)
    ax2.xaxis.set_major_formatter(DateFormatter("%H:%M"))

    #add date and station name to plot
    plt.figtext(0.1, 0.02, dtmin.strftime("%Y-%m-%d"))
    plt.figtext(0.7, 0.02, ref + "-" + station)

    #save plot as an image
    plt.savefig(pic_name, dpi=100)

    return mode_i

def dbase_write(dbase_name, data, station, mode, navi_sys, mode_i, ref):
    """ write statistical parameters into psql database
        :param: psql data base name
                pandas dataframe with data
                station id
                positioning mode
                navigation sytems
    """
    #create list of dictionaries of the statistical parameters
    #just add new elements to the list and all the others are done automatically
    data_to_dbase = [
        {'col': 'station_ID', 'type': 'INT', 'value': station},                         #station id
        {'col': 'ref_name', 'type': 'VARCHAR', 'value': ref},                           #reference station name
        {'col': 'datetime', 'type': 'TIMESTAMP', 'value': min(data['datetime'])},       #date and time of the first position
        {'col': 'nr_of_epochs', 'type': 'INT', 'value': data.shape[0]},                 #number of epochs
        {'col': 'mode', 'type': 'VARCHAR', 'value': mode},                              #solution mode
        {'col': 'navi_sys', 'type': 'VARCHAR', 'value': navi_sys},                      #used navigation systems
        {'col': 'nr_of_float', 'type': 'INT', 'value': len(data[(data['mode'] == 2)])}, #number of float positions
        {'col': 'mean_EW', 'type': 'FLOAT', 'value': data['EW_error'].where(data['mode'] == mode_i).mean()},          #mean of East-West positions
        {'col': 'mean_SN', 'type': 'FLOAT', 'value': data['SN_error'].where(data['mode'] == mode_i).mean()},
        {'col': 'mean_EL', 'type': 'FLOAT', 'value': data['ELE_error'].where(data['mode'] == mode_i).mean()},
        {'col': 'max_EL', 'type': 'FLOAT', 'value': data['ELE_error'].where(data['mode'] == mode_i).max()},
        {'col': 'max_EW', 'type': 'FLOAT', 'value': data['EW_error'].where(data['mode'] == mode_i).max()},
        {'col': 'max_SN', 'type': 'FLOAT', 'value': data['SN_error'].where(data['mode'] == mode_i).max()},
        {'col': 'min_ELE', 'type': 'FLOAT', 'value': data['ELE_error'].where(data['mode'] == mode_i).min()},
        {'col': 'min_EW', 'type': 'FLOAT', 'value': data['EW_error'].where(data['mode'] == mode_i).min()},
        {'col': 'min_SN', 'type': 'FLOAT', 'value': data['SN_error'].where(data['mode'] == mode_i).min()},
        {'col': 'std_ELE', 'type': 'FLOAT', 'value': data['ELE_error'].where(data['mode'] == mode_i).std()},
        {'col': 'std_EW', 'type': 'FLOAT', 'value': data['EW_error'].where(data['mode'] == mode_i).std()},
        {'col': 'std_SN', 'type': 'FLOAT', 'value': data['SN_error'].where(data['mode'] == mode_i).std()},
        {'col': 'q95_ELE', 'type': 'FLOAT', 'value': data['ELE_error'].where(data['mode'] == mode_i).quantile(.95)},
        {'col': 'q95_EW', 'type': 'FLOAT', 'value': data['EW_error'].where(data['mode'] == mode_i).quantile(.95)},
        {'col': 'q95_SN', 'type': 'FLOAT', 'value': data['SN_error'].where(data['mode'] == mode_i).quantile(.95)},
        {'col': 'q95_ELE_abs', 'type': 'FLOAT', 'value': data['ELE_error'].where(data['mode'] == mode_i).abs().quantile(.95)},
        {'col': 'q95_EW_abs', 'type': 'FLOAT', 'value': data['EW_error'].where(data['mode'] == mode_i).abs().quantile(.95)},
        {'col': 'q95_SN_abs', 'type': 'FLOAT', 'value': data['SN_error'].where(data['mode'] == mode_i).abs().quantile(.95)}

    ]
    #for testing mode filter
    #print('no mode filer', data['ELE_error'].mean())
    #print('with mode filter', data['ELE_error'].where(data['mode'] == mode_i).mean())

    #data base connection
    conn = psycopg2.connect("dbname=" + dbase_name)

    #create a cursor
    cur = conn.cursor()

    #create table
    sql_create_table = "CREATE TABLE IF NOT EXISTS rtk_stats (id SERIAL PRIMARY KEY);"
    cur.execute(sql_create_table)

    #add columns
    sql_add_cols = "ALTER TABLE rtk_stats " + ", ".join(['ADD COLUMN IF NOT EXISTS {} {}'.format(d['col'], d['type']) for d in data_to_dbase])
    cur.execute(sql_add_cols)

    #insert a new row
    cols = ", ".join(['{}'.format(d['col']) for d in data_to_dbase])
    val_cols = ", ".join(["'{}'".format(d['value']) for d in data_to_dbase])
    sql = "INSERT INTO rtk_stats(" + cols + ") VALUES(" + val_cols + ");"
    cur.execute(sql)
    #print(sql)

    # close the communication with the PostgreSQL
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    warnings.filterwarnings("ignore")

    #check number of arguments
    if len(sys.argv) < 7:
        print('wrong number of arguments')
        print('use', sys.argv[0], 'json_file', 'pos_file_path', 'pos_file_name', 'station', 'year', 'doy', 'ref')
        exit()

    #json file name as the first argument from command prompt
    JNAME = str(sys.argv[1])
    if not os.path.exists(JNAME):
        print(JNAME, 'json file does not exist')
        exit()

    #load json file and get config parameters
    with open(JNAME) as jfile:
        JDATA = json.load(jfile)
        pic_folder = JDATA["pic_folder"]    #folder to save graph pictures
        dbase_name = JDATA["dbase_name"]    #psql dbase name

    #arguments from command prompt
    pos_file_path = str(sys.argv[2])
    pos_file_name = str(sys.argv[3])
    station = str(sys.argv[4])
    year = str(sys.argv[5])
    doy = str(sys.argv[6])
    if len(sys.argv) == 8:
        ref = str(sys.argv[7])
    else:
        ref = 0
    print(ref)
    pos_file = pos_file_path + pos_file_name

    #output file
    pic_save = Path(pic_folder + '/Y' + year + '/D' + doy +'/PildoBox' + station)
    pic_save.mkdir(parents=True, exist_ok=True)
    pic_name = str(pic_save) + '/' + pos_file_name[:-3] + 'png'

    #load stations.txt file with true position of stations
    data_stations = pd.read_csv('/home/tbence/Paripa/rov_stations.txt',
                                header=None, delim_whitespace=True)
    data_stations.columns = ["id", "city", "lat", "long", "elev"]

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
    ct, mode, navi_sys = header_lines(pos_file)

    #load pos file
    data_gps = pd.read_csv(pos_file, header=None,
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

    #generate plots
    mode_i = plot_gen(data_gps, mode, navi_sys, station, ref, pic_name)

    #write statistical parameters into psql database
    dbase_write(dbase_name, data_gps, int(station[-3:]), mode, navi_sys, mode_i, ref)

