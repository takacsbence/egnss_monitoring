#!/usr/bin/env python3

"""
    generate true position error plot from RTKLIB pos file
    add statistical parameters into database
"""

from pathlib import Path
import sys
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


def plot_gen(data, mode, navi_sys, station, pic_name):
    """ generate true position error plots
        :param: pandas dataframe with data
        :param: solutuion mode, like single or kinematic
        :param: navigation system, like GPS or GPS GALILEO
        :param: station id, like 205
        :param: plot image file name
    """

    fig, ax = plt.subplots()
    #fig.set_size_inches(10, 10)    #TB: meghagynám a default méreteket

    #plot
    ax.plot(data['datetime'], data['EW_error'], label='East-West')
    ax.plot(data['datetime'], data['SN_error'], label='North-South')
    ax.plot(data['datetime'], data['ELE_error'], label='Up-Down')

    #solution mode
    if mode == 'kinematic':
        ymax = 0.4
        title = 'RTK'
    elif mode == 'single':
        ymax = 10
        title = 'SPP'
    elif mode == 'dgps':
        ymax = 10
        title = 'DGPS'
    else:
        ymax = 10

    #parameters
    ax.set_ylim([-ymax, ymax])
    # show exactly one hour session
    dtmin = min(data['datetime']).round('60min').to_pydatetime()
    dtmax = max(data['datetime']).round('60min').to_pydatetime()
    ax.set_xlim([dtmin, dtmax])
    ax.set_xlabel('time (hh:mm)')
    ax.set_ylabel('Coordinate errors [meters]')
    ax.set_title('Position Error Graph ' + title + " " + navi_sys)
    ax.legend(loc=2)
    ax.grid()

    #number of satellites
    ax2 = ax.twinx()
    ax2.plot(data['datetime'], data['nsat'], label='# of satellites', color='red')
    ax2.plot(data['datetime'], data['mode'], label='solution mode', color='purple')
    ax2.set_ylim([0, 16])
    ax2.set_ylabel('# of satellites / solution mode')
    ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    ax2.legend(loc=1)
    ax2.xaxis.set_major_formatter(DateFormatter("%H:%M"))

    #add statistical data
    #TB TODO: feliratok helye
    '''
    ax.text(data['datetime'][600], -0.7, "EW: mean:" + str(round(data['EW_error'].mean(), 3))
        + " min:" + str(round(data['EW_error'].min(), 3))
        + " max:" + str(round(data['EW_error'].max(), 3))
        + " stdev: " + str(round(data['EW_error'].std(), 3)), fontsize=10)
    ax.text(data_gps['datetime'][600], -0.8, "NS: mean:" + str(round(data['SN_error'].mean(), 3))
        + " min:" + str(round(data['SN_error'].min(), 3))
        + " max:" + str(round(data['SN_error'].max(), 3))
        + " stdev: "+ str(round(data['SN_error'].std(),3)), fontsize=10)
    ax.text(data_gps['datetime'][600], -0.9, "Ele: mean:" + str(round(data['ELE_error'].mean(), 3))
        + " min:" + str(round(data['ELE_error'].min(), 3))
        + " max:" + str(round(data['ELE_error'].max(), 3))
        + " stdev: " + str(round(data['ELE_error'].std(),3)), fontsize=10)
    '''

    #add date and station name to plot
    plt.figtext(0.1, 0.02, dtmin.strftime("%Y-%m-%d"))
    plt.figtext(0.8, 0.02, station)

    #save plot as an image
    plt.savefig(pic_name, dpi=100)

def dbase_write(dbase_name, data, station, mode, navi_sys):
    """ write statistical parameters into psql database
        :param: psql data base name
                pandas dataframe with data
                station id
                positioning mode
                navigation sytems
    """

    #statistical parameters
    nr_of_epochs = data.shape[0]    #number of epochs
    dtmin = min(data['datetime'])   #date and time of the first position
    nr_of_float = len(data[(data['mode'] == 2)])  # nr of float solutions

    #data base connection
    conn = psycopg2.connect("dbname=" + dbase_name)

    #create a cursor
    cur = conn.cursor()

    #create table
    sql_create_table = "CREATE TABLE IF NOT EXISTS rtk_stats ( \
        id SERIAL PRIMARY KEY, \
        station_ID INT, \
        datetime TIMESTAMP, \
        nr_of_epochs INT, \
        mode VARCHAR, \
        navi_sys VARCHAR);"
    cur.execute(sql_create_table)

    #insert a new row
    sql_insert_row = "INSERT INTO rtk_stats(station_id, nr_of_epochs, mode, navi_sys, datetime, nr_of_float) VALUES ({}, {}, '{}', '{}', '{}', {})".format(station, nr_of_epochs, mode, navi_sys, dtmin, nr_of_float)
    #print(sql_insert_row)
    cur.execute(sql_insert_row)

    #querry all data, just for testing
    #cur.execute('SELECT * from rtk_stats')
    #s = cur.fetchall()
    #print(s)

    # close the communication with the PostgreSQL
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":

    #check number of arguments
    if len(sys.argv) != 6:
        print('wrong number of arguments')
        print('use', sys.argv[0], 'pos_file_path', 'pos_file_name', 'station')
        exit()

    #arguments from command prompt
    pos_file_path = str(sys.argv[1])
    pos_file_name = str(sys.argv[2])
    station = str(sys.argv[3])
    year = str(sys.argv[4])
    doy = str(sys.argv[5])
    pos_file = pos_file_path + pos_file_name

    #output file
    #tbence átírandó hegyi-re !!!!!
    pic_save = Path('/home/tbence/public_html/Position_Error_Graphs/Y' + year + '/D' + doy +'/PildoBox' + station)
    pic_save.mkdir(parents=True, exist_ok=True)
    pic_name = str(pic_save) + '/' + pos_file_name[:-3] + 'png'
    print(pic_name)

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
    plot_gen(data_gps, mode, navi_sys, station, pic_name)

    #write statistical parameters into psql database
    #tbence átírandó hegyi-re !!!!!
    dbase_name = "tbence"
    dbase_write(dbase_name, data_gps, int(station[-3:]), mode, navi_sys)
