#!/usr/bin/env python3

#generate true position error plot from RTKLIB pos file

import os.path
from pathlib import Path
import sys
import math
from datetime import date, datetime, timedelta
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
import pandas as pd
import statistics
import matplotlib.ticker as ticker

def HeaderLines(posfile):
#input: RTKLIB pos file
#output: the number of header lines (header lines strats by "%")
    ct = 0
    file = open(posfile, 'r')
    Lines = file.readlines()
    for line in Lines:
        ct +=1
        if line.find('%') == -1:
            file.close()
            return ct


def PlotGen(data, mode, station, pic_name):
#generate true position error plots

    fig, ax = plt.subplots()
    #fig.set_size_inches(10, 10)    #TB: meghagynám a default méreteket

    #plot
    ax.plot(data['datetime'], data['EW_error'], label='East-West')
    ax.plot(data['datetime'], data['SN_error'], label='North-South')
    ax.plot(data['datetime'], data['ELE_error'], label='Up-Down')
    
    #solution mode
    if mode == 'RTK':
        ymax = 1
    elif mode == 'DGPS':
        ymax = 5
    elif mode == 'SPP':
        ymax = 10
    else:
        ymax = 5

    #parameters   
    ax.set_ylim([-ymax, ymax])
    # show exactly one hour session
    dtmin = min(data['datetime']).round('60min').to_pydatetime()
    dtmax = max(data['datetime']).round('60min').to_pydatetime()
    ax.set_xlim([dtmin, dtmax])
    ax.set_xlabel('time (hh:mm)')
    ax.set_ylabel('Coordinate errors [meters]')
    ax.set_title('Position Error Graph ' + mode)
    ax.legend(loc = 2)
    ax.grid()
 
    #number of satellites
    ax2 = ax.twinx()
    ax2.plot(data['datetime'], data['nsat'], label='# of satellites', color = 'red')
    ax2.plot(data['datetime'], data['mode'], label='solution mode', color = 'purple')
    ax2.set_ylim([0, 16])   #TODO legyen dinamikus
    ax2.set_ylabel('# of satellites / solution mode')
    ax2.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
    ax2.legend(loc = 1)
    ax2.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    
    #add statistical data
    #TB TODO: feliratok helye
    '''
    ax.text(data['datetime'][600], -0.7, "EW: mean:" + str(round(data['EW_error'].mean(), 3)) + " min:" +
        str(round(data['EW_error'].min(), 3)) + " max:" + str(round(data['EW_error'].max(), 3)) + " stdev: " + str(round(data['EW_error'].std(), 3)), fontsize=10)
    ax.text(data_gps['datetime'][600], -0.8, "NS: mean:" + str(round(data['SN_error'].mean(), 3)) + " min:" +
        str(round(data['SN_error'].min(), 3)) + " max:" + str(round(data['SN_error'].max(), 3)) + " stdev: "+ str(round(data['SN_error'].std(),3)), fontsize=10)
    ax.text(data_gps['datetime'][600], -0.9, "Ele: mean:" + str(round(data['ELE_error'].mean(), 3)) + " min:" + 
        str(round(data['ELE_error'].min(), 3)) + " max:" + str(round(data['ELE_error'].max(), 3)) + " stdev: "+str(round(data['ELE_error'].std(),3)), fontsize=10)
    '''        
    
    #add date and station name to plot
    plt.figtext(0.1, 0.02, dtmin.strftime("%Y-%m-%d"))
    plt.figtext(0.8, 0.02, station)
    
    #save plot as an image
    plt.savefig(pic_name, dpi = 100)

if __name__ == "__main__":

    #user inputs
    # TODO: check wrong number of inputs
    pos_file = str(sys.argv[1])
    station = str(sys.argv[2])
    mode = str(sys.argv[3])
        
    #solution mode TB ez majd később jöhetne a pos file fejlécéből
    if mode == '0':
        mode = 'SPP'
    elif mode == '1':
        mode = 'RTK'

    #output file
    #tbence átírandó hegyi-re !!!!!
    #pic_save = Path('/home/hegyi/public_html/Position_Error_Graphs/' + pos_file[35:50])
    pic_save = Path('/home/tbence/public_html/Position_Error_Graphs/' + pos_file[35:59])
    pic_save.mkdir(parents=True, exist_ok=True)
    pic_name = str(pic_save) + '/' + pos_file[59:-3] + 'png'
    print(pic_name)

    #load stations.txt file with true position of stations
    data_stations = pd.read_csv('/home/hegyi/Paripa/Paripa1/stations.txt', header=None, delim_whitespace=True)
    data_stations.columns=["id", "city", "lat", "long", "elev"]

    #index of current station
    station = 'PildoBox' + station
    idx = data_stations[data_stations['id'] == station].index.item()

    #true coordinates of rover
    ref_lat = data_stations['lat'][idx]
    ref_lon = data_stations['long'][idx]
    ref_ele = data_stations['elev'][idx]

    #1 arc seconds in latitude corresponds to ~31 m on the surface of the Earth
    dlat = math.pi / 180 * 6380000 / 3600

    #nr of header lines
    ct = HeaderLines(pos_file)

    #load pos file
    data_gps = pd.read_csv(pos_file, header=None, delim_whitespace=True, skiprows=ct)
    data_gps.columns = ["date", "time", "lat", "lon", "ele", "mode", "nsat", "stdn", "stde", "stdu", "stdne", "stdeu", "stdun" , "age", "ratio"]
    print(data_gps.shape[0], 'positions read from', pos_file)
    data_gps['datetime'] = pd.to_datetime(data_gps['date'] + ' ' + data_gps['time'], format='%Y/%m/%d %H:%M:%S.%f')
        
    #coordinate errors
    data_gps['EW_error'] = (data_gps['lon'] - ref_lon) * dlat * math.cos(math.radians(ref_lat)) * 3600
    data_gps['SN_error'] = (data_gps['lat'] - ref_lat) * dlat * 3600
    data_gps['ELE_error'] = data_gps['ele'] - ref_ele  
    
    #generate plots
    PlotGen(data_gps, mode, station, pic_name)

#TB ezek a sorok sztem nem kellenek

'''
    if mode.__eq__('0'):
        PosEvaluator(file_name, 'SPP')
        file_name = file_name[:-4]
        PosEvaluator(file_name + 'G.pos', 'SPPG')

    if mode.__eq__('1'):
        file_name = file_name[:-4]
        print('FNAME:',file_name)
        PosEvaluator(file_name+'.pos', 'KINEMATIC')
        PosEvaluator(file_name+'_G.pos', 'KINEMATICG')

    exit()
'''

#TB ezt magamnak szedtem ki, nem ebben a programban van a helye

'''
    zip_path= save_location +'/PildoBox' + pos_file + ".raw.zip"

    for f in os.listdir(save_location):
        if f.endswith('.nav') or f.endswith('.lnav') or f.endswith('.hnav') or f.endswith('.obs') or f.endswith('.pos') or f.endswith('.raw') or f.endswith('.stat') or f.endswith('.sbs'):

            os.remove(save_location+"//"+f)
    '''
