#!/usr/bin/env python3

#A program kap inputkent egy masik modulbol egy pos filet azt hogy melyik roverhez viszonyitsa az adott pos file ertekeit egy mode ami annyit csinal hogy SPP vagy RTK
#Ezutan a program eloallitja a True Position Error graphot az adott pos file ertekibol, legvegul pedig a statisztikat elmenti egy adatbazisba(work in proggres)

import os.path
import sys
import math
from datetime import date
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
import pandas as pd
import linecache
import psycopg2
import statistics

#Datum meghatarozas
todays_date = date.today()
doy = date.today().strftime("%j")

#Recommended user inputs
pos_file=str(sys.argv[1])
station=str(sys.argv[2])
mode=str(sys.argv[3])
station_number=station

print(pos_file)

#Mentesi helyek
save_location='/home/hegyi/Paripa/Downloaded_zips'
pic_save="/home/hegyi/public_html/Position_Error_Graphs"

station='PildoBox'+station

#Ebben a  modban SPP fileokat dolgoz fel
file_name=save_location +'/'+doy+'/'+station+'/'+pos_file+'.pos'

#A txt file beolvasasa es adatok eltarolasa
data_stations=pd.read_csv('/home/hegyi/Paripa/Paripa1/stations.txt',header=None,delim_whitespace=True)
data_stations.columns=["id","city","lat","long","elev"]

#Jelenleg melyik Roverhez hasonlitjuk az adott pos file ertekeit
idx=data_stations[data_stations['id']==station].index.item()

dlat = math.pi / 180 * 6380000 / 3600

#Azert felel hogy kitorolje a headert a fileokbol
def HeaderDelete(posfile):
    ct=0
    print('elim'+posfile)
    file=open(posfile,'r')
    Lines = file.readlines()
    for line in Lines:
        ct=ct+1
        if line.find('%')==-1:
            print('CT:'+str(ct))
            return ct



#A kepeket allitja elo a fuggveny az elso parameter az adatbazis kapcsolata a masodik a feldolgozando file neve a harmadik pedig a tipusa
def PosEvaluator(filename,type):
    
    #Megadja hogy hany sor fog atugrani a fileban
    ct=HeaderDelete(filename)  
    print(ct) 

    #Pos file beolvasasa
    data_gps = pd.read_csv(filename, header=None, delim_whitespace=True, skiprows=ct)

    data_gps.columns = ["date", "time", "lat", "lon", "ele", "mode", "nsat", "stdn", "stde", "stdu", "stdne", "stdeu", "stdun" , "age", "ratio"]
        
    ref_lat = data_stations['lat'][idx]
    ref_lon = data_stations['long'][idx]
    ref_ele = data_stations['elev'][idx]
   
    #Ertekek szamitasa
    EW_meters = (data_gps['lon'] - ref_lon) * 31 * math.cos(dlat) * 3600
    NS_meters = (data_gps['lat'] - ref_lat) * 31 * 3600
    Elevation = data_gps['ele'] - ref_ele  
       
    
    data_gps['datetime'] = pd.to_datetime(data_gps['date'] + ' ' + data_gps['time'], format='%Y/%m/%d %H:%M:%S.%f')

    fig, ax = plt.subplots()
    fig.set_size_inches(10, 10)

    # EW-graph plot
    ax.plot(data_gps['datetime'], EW_meters, label='East-West')
    ax.set_ylim([-5, 20])
    ax.set_xlim([min(data_gps['datetime']).round('60min').to_pydatetime(),
                 max(data_gps['datetime']).round('60min').to_pydatetime()])  # show exactly one hour session
    ax.set_xlabel('time (hh:mm)')
    ax.set_ylabel('Difference in meters')
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))

    # NS-graph plot
    ax.plot(data_gps['datetime'], NS_meters, label='North-South')
    ax.set_xlim([min(data_gps['datetime']).round('60min').to_pydatetime(),
                 max(data_gps['datetime']).round('60min').to_pydatetime()])  # show exactly one hour session
    ax.set_xlabel('time (hh:mm)')
    ax.set_ylabel('Difference in meters')
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    fig.set_size_inches(10, 10)
    

    # Elevation-graph plot
    ax.plot(data_gps['datetime'], Elevation, label='Elevation')
    ax.set_ylim([-6, 6])
    ax.set_xlim([min(data_gps['datetime']).round('60min').to_pydatetime(),
                 max(data_gps['datetime']).round('60min').to_pydatetime()])  # show exactly one hour session
    ax.set_xlabel('time (hh:mm)')
    ax.set_ylabel('Difference in meters')
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))

    # Number of satellites
    if mode.__eq__('0'):
        ax2=ax.twinx()
        ax2.plot(data_gps['datetime'], data_gps['nsat'],label='Number of Satellites',color='red')
        ax2.set_ylim([0, 20])
        ax.set_xlim([min(data_gps['datetime']).round('60min').to_pydatetime(),
                 max(data_gps['datetime']).round('60min').to_pydatetime()])  # show exactly one hour session
        ax2.set_ylabel('Number of Sattelites')
    #Statisztikai adatok elkeszitese a grafikonra atlag, min, max, szoras harom tizeddesre kerekitve
        plt.text(data_gps['datetime'][1000], 19, "EW: avarage:" + str(round(EW_meters.mean(), 3)) + " min:" + str(
            round(min(EW_meters), 3)) + " max:" + str(round(max(EW_meters), 3))+ " Spread: " +str(round(statistics.variance(EW_meters),3)), fontsize=10)
        plt.text(data_gps['datetime'][1000], 18.5, "NS: avarage:" + str(round(NS_meters.mean(), 3)) + " min:" + str(
            round(min(NS_meters), 3)) + " max:" + str(round(max(NS_meters), 3)) + " Spread: "+str(round(statistics.variance(NS_meters),3)), fontsize=10)
        plt.text(data_gps['datetime'][1000], 18, "Elevation: avarage:" + str(round(Elevation.mean(), 3)) + " min:" + str(
            round(min(Elevation), 3)) + " max:" + str(round(max(Elevation), 3)) + " Spread: "+str(round(statistics.variance(Elevation),3)), fontsize=10)
            
    fig.autofmt_xdate(rotation=45)
    ax.set_xlabel('time (hh:mm)')
    ax.xaxis.set_major_formatter(DateFormatter("%Y/%m/%d %H:%M"))   
    ax.set_title(type+' Position Error Graph')
    
    #Tengelyek beallitasa es jelmagyarazat elhelyezese
    h1, l1 = ax.get_legend_handles_labels()
    if mode.__eq__('0'):
        h2, l2 = ax2.get_legend_handles_labels()
        ax.legend(h1 + h2, l1 + l2, loc='upper left')
    ax.legend(h1, l1, loc='upper left')

    temp=''
    num=0
    if type.__eq__('SPP'):
        temp=''
        var='S'
        num=1
    elif type.__eq__('SPPG'):
        temp='G'
        var='SG'
        num=9
    elif type.__eq__('KINEMATIC'):
        temp=''
        var='K'
        num=1
        ax.set_ylim([-1, 1])
        #Ha RTK a mod akkor kicsit jobban rakozelit a kepre mert varhatoan kissebb a pozicio hiba
        plt.text(data_gps['datetime'][1800], 0.9, "EW: avarage:" + str(round(EW_meters.mean(), 3)) + " min:" + str(
            round(min(EW_meters), 3)) + " max:" + str(round(max(EW_meters), 3)), fontsize=10)
        plt.text(data_gps['datetime'][1800], 0.85, "NS: avarage:" + str(round(NS_meters.mean(), 3)) + " min:" + str(
            round(min(NS_meters), 3)) + " max:" + str(round(max(NS_meters), 3)), fontsize=10)
        plt.text(data_gps['datetime'][1800], 0.8,
                 "Elevation: avarage:" + str(round(Elevation.mean(), 3)) + " min:" + str(
                     round(min(Elevation), 3)) + " max:" + str(round(max(Elevation), 3)), fontsize=10)
        particular_line = linecache.getline(filename, 21)
        split = particular_line.split(' ')
        #kine_latitude = split[6]
        #kine_longitude = split[8]
        #kine_elevation = split[10]
    elif type.__eq__('KINEMATICG'):
        ax.set_ylim([-1, 1])
        var='KG'
        temp='G'
        num=9
        plt.text(data_gps['datetime'][1800], 0.9, "EW: avarage:" + str(round(EW_meters.mean(), 3)) + " min:" + str(
            round(min(EW_meters), 3)) + " max:" + str(round(max(EW_meters), 3)), fontsize=10)
        plt.text(data_gps['datetime'][1800], 0.85, "NS: avarage:" + str(round(NS_meters.mean(), 3)) + " min:" + str(
            round(min(NS_meters), 3)) + " max:" + str(round(max(NS_meters), 3)), fontsize=10)
        plt.text(data_gps['datetime'][1800], 0.8,
                 "Elevation: avarage:" + str(round(Elevation.mean(), 3)) + " min:" + str(
                     round(min(Elevation), 3)) + " max:" + str(round(max(Elevation), 3)), fontsize=10)
        particular_line = linecache.getline(filename, 21)
        split=particular_line.split(' ')
        kine_latitude=split[6]
        kine_longitude=split[8]
        kine_elevation=split[10]
    elif type.__eq__('SBAS'):
        temp=type
        var='SBAS'
        num=3
    elif type.__eq__('SBASG'):
        temp=type
        var='SBASG'
        num=11

    plt.grid()
    #plt.legend(loc='upper left')
    if not os.path.exists(pic_save+'/'+str(doy)):
        os.mkdir(pic_save+'/'+str(doy))
    if not os.path.exists(pic_save+'/'+str(doy)+'/'+station):
        os.mkdir(pic_save+'/'+str(doy)+'/'+station)
 
    #Kep elmentese a weblap mappajaba
    plt.savefig(pic_save+'/'+str(doy)+'/'+station+'/'+pos_file+temp+'.png', dpi=100)
    station2=station[8:]
    stat_id = pos_file[8:] + station2 + var
    nop=0


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

zip_path= save_location +'/PildoBox' + pos_file + ".raw.zip"

for f in os.listdir(save_location):
    if f.endswith('.nav') or f.endswith('.lnav') or f.endswith('.hnav') or f.endswith('.obs') or f.endswith('.pos') or f.endswith('.raw') or f.endswith('.stat') or f.endswith('.sbs'):

        os.remove(save_location+"//"+f)


