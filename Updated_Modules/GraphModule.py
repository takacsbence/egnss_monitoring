#!/usr/bin/env python3

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
d0 = date(todays_date.year, 1, 1)
d1 = date(todays_date.year, todays_date.month, todays_date.day)
delta = d1 - d0
doy=str(delta)
doy=str(doy)[:-14]

#Ellenorzese a nap hossznak ha kevesebb mint harom karakter akkor kap egy 0-t elore
if len(doy)<3:
    doy='0'+doy



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
if mode.__eq__('0'):
    file_name=save_location +'/'+doy+'/'+station+'/'+pos_file+'.pos'

#Ebben a modban pedig RTK fileokat
if mode.__eq__('1'):
    real_day=str(int(doy)+1)
    file_name=save_location +'/'+real_day+'/'+station+'/'+pos_file+'.pos'

#A txt file beolvasasa es adatok eltarolasa
data_stations=pd.read_csv('stations.txt',header=None,delim_whitespace=True)
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
def PosEvaluator(conn,filename,type):
    
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
    print('\n date:',data_gps['datetime'][10])

    #fist_obs=data_gps['datetime'][0]
    #last_obs=data_gps['datetime'][3598]

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
    # ax.set_ylim([-5,5])
    ax.set_xlim([min(data_gps['datetime']).round('60min').to_pydatetime(),
                 max(data_gps['datetime']).round('60min').to_pydatetime()])  # show exactly one hour session
    ax.set_xlabel('time (hh:mm)')
    ax.set_ylabel('Difference in meters')
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
    fig.set_size_inches(10, 10)
    # plt.savefig(pic_save+'//' + station_name+"_" +year+"_"+doy+"_"+ time + ".png",dpi=100)

    # Elevation-graph plot
    ax.plot(data_gps['datetime'], Elevation, label='Elevation')
    ax.set_ylim([-6, 6])
    ax.set_xlim([min(data_gps['datetime']).round('60min').to_pydatetime(),
                 max(data_gps['datetime']).round('60min').to_pydatetime()])  # show exactly one hour session
    ax.set_xlabel('time (hh:mm)')
    ax.set_ylabel('Difference in meters')
    ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))

    # Number of satellites
    fig.autofmt_xdate(rotation=45)
    ax2=ax.twinx()
    ax2.plot(data_gps['datetime'], data_gps['nsat'],label='Number of Satellites',color='red')
    ax2.set_ylim([0, 20])
    ax.set_xlim([min(data_gps['datetime']).round('60min').to_pydatetime(),
                 max(data_gps['datetime']).round('60min').to_pydatetime()])  # show exactly one hour session
    ax.set_xlabel('time (hh:mm)')
    ax2.set_ylabel('Number of Sattelites')
    ax.xaxis.set_major_formatter(DateFormatter("%Y/%m/%d %H:%M"))
    #Statisztikai adatok elkeszitese a grafikonra
    plt.text(data_gps['datetime'][1000], 19, "EW: avarage:" + str(round(EW_meters.mean(), 3)) + " min:" + str(
        round(min(EW_meters), 3)) + " max:" + str(round(max(EW_meters), 3))+ " Spread: " +str(round(statistics.variance(EW_meters),3)), fontsize=10)
    plt.text(data_gps['datetime'][1000], 18.5, "NS: avarage:" + str(round(NS_meters.mean(), 3)) + " min:" + str(
        round(min(NS_meters), 3)) + " max:" + str(round(max(NS_meters), 3)) + " Spread: "+str(round(statistics.variance(NS_meters),3)), fontsize=10)
    plt.text(data_gps['datetime'][1000], 18, "Elevation: avarage:" + str(round(Elevation.mean(), 3)) + " min:" + str(
        round(min(Elevation), 3)) + " max:" + str(round(max(Elevation), 3)) + " Spread: "+str(round(statistics.variance(Elevation),3)), fontsize=10)
       
    

    ax.set_title(type+' Position Error Graph')
    #Tengelyek beallitasa
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc='upper left')

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
        temp=type
        var='K'
        num=1
        ax.set_ylim([-1, 1])
        #Ha RTK a mod akkor kicsit jobban rakozelit a kepre mert varhatoan kissebb a pozicio hiba
        plt.text(data_gps['datetime'][1800], 0.9, "EW: avarage:" + str(round(EW_meters.mean(), 4)) + " min:" + str(
            round(min(EW_meters), 4)) + " max:" + str(round(max(EW_meters), 4)), fontsize=10)
        plt.text(data_gps['datetime'][1800], 0.85, "NS: avarage:" + str(round(NS_meters.mean(), 4)) + " min:" + str(
            round(min(NS_meters), 4)) + " max:" + str(round(max(NS_meters), 4)), fontsize=10)
        plt.text(data_gps['datetime'][1800], 0.8,
                 "Elevation: avarage:" + str(round(Elevation.mean(), 4)) + " min:" + str(
                     round(min(Elevation), 4)) + " max:" + str(round(max(Elevation), 4)), fontsize=10)
        particular_line = linecache.getline(filename, 21)
        split = particular_line.split(' ')
        #kine_latitude = split[6]
        #kine_longitude = split[8]
        #kine_elevation = split[10]
    elif type.__eq__('KINEMATICG'):
        ax.set_ylim([-1, 1])
        var='KG'
        temp=type
        num=9
        plt.text(data_gps['datetime'][1800], 0.9, "EW: avarage:" + str(round(Average(EW_meters), 4)) + " min:" + str(
            round(min(EW_meters), 4)) + " max:" + str(round(max(EW_meters), 4)), fontsize=10)
        plt.text(data_gps['datetime'][1800], 0.85, "NS: avarage:" + str(round(Average(NS_meters), 4)) + " min:" + str(
            round(min(NS_meters), 4)) + " max:" + str(round(max(NS_meters), 4)), fontsize=10)
        plt.text(data_gps['datetime'][1800], 0.8,
                 "Elevation: avarage:" + str(round(Average(Elevation), 4)) + " min:" + str(
                     round(min(Elevation), 4)) + " max:" + str(round(max(Elevation), 2)), fontsize=10)
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


    
    
    '''cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS Statisticss(stat_id nvarchar(20) not null,
        station_id_fk nvarchar(20) not null,
        foreign key(station_id_fk) references ROVERStations(station_id),
        type nvarchar(15) not null,
        float smallint not null,
        first_obs DATETIME not null,
        last_obs DATETIME not null,
        constellation smallint not null,
        number_of_positions smallint not null, 
        EW_avarage float(4) not null,
        EW_stdev float(4) not null,
        EW_maximum float(4) not null,
        EW_minimum float(4) not null,
        NS_avarage float(4) not null,
        NS_stdev float(4) not null,
        NS_maximum float(4) not null,
        NS_minimum float(4) not null,
        Elevation_avarage float(4) not null,
        Elevation_stdev float(4) not null,
        Elevation_maximum float(4) not null,
        Elevation_minimum float(4) not null,
        reference_point_latitude nvarchar(50),
        reference_point_longitude nvarchar(50),
        reference_point_elevation nvarchar(50); )"""

'''

    #cursor.execute('SELECT stat_id from Statisticss where stat_id = %(stat_id)s',{'stat_id': stat_id})
    #cursor.execute(sql,data)
    #myresult2 = cursor.fetchall()
    #if not myresult2:
    #    print('Row Does not exist!')
    #    cursor.execute("INSERT INTO Statisticss (stat_id,station_id_fk,type,float,first_obs,last_obs,constellation,number_of_positions,EW_avarage,EW_stdev,EW_maximum,EW_minimum,NS_avarage,NS_stdev,NS_maximum,NS_minimum,Elevation_avarage,Elevation_stdev,Elevation_maximum,Elevation_minimum,reference_point_latitude,reference_point_longitude,reference_point_elevation)
    #                   Values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
    #        (stat_id,station,type,fist_obs,last_obs,num,nop,EW_AV,EW_STDEV,round(max(EW_meters), 4),round(min(EW_meters), 4),NS_AV,NS_STDEV,round(max(NS_meters), 4),round(min(NS_meters), 4),ELEV_AV,ELEV_STDEV,round(max(Elevation), 4),round(min(Elevation), 4),reference_point_latitude,reference_point_longitude,reference_point_elevation)
    #        )
    '''cursor.execute("INSERT INTO Statisticss (stat_id,
        station_id_fk,
        type,
        float,
        first_obs,
        last_obs,
        constellation,
        number_of_positions,
        EW_avarage,
        EW_stdev,
        EW_maximum,
        EW_minimum,
        NS_avarage,
        NS_stdev,
        NS_maximum,
        NS_minimum,
        Elevation_avarage,
        Elevation_stdev,
        Elevation_maximum,
        Elevation_minimum,
        reference_point_latitude,
        reference_point_longitude,
        reference_point_elevation)
        Values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
        % (stat_id,station,type,float,fist_obs,last_obs,num,nop,EW_AV,EW_STDEV,round(max(EW_meters), 4),round(min(EW_meters), 4),NS_AV,NS_STDEV,round(max(NS_meters), 4),round(min(NS_meters), 4),ELEV_AV,ELEV_STDEV,round(max(Elevation), 4),round(min(Elevation), 4),reference_point_latitude,reference_point_longitude,reference_point_elevation))

    conn.commit()    '''

    #cursor.execute("SELECT * FROM Statisticss")
    #result = cursor.fetchall()
    #for row in result:
    #    print(row)
    #    print("\n")


'''conn=pyodbc.connect('Driver={SQL Server};'
                    'Server=192.168.0.32;'
                    'Port=1433;'
                    'Database=Paripa-HC;'
                    'UID=Lehel;'
                    'PWD=Paripa1'
                    )

'''
#Ez majd az adatbazis kapcsolathoz kerul
conn='Placeholder'

if mode.__eq__('0'):
    PosEvaluator(conn,file_name, 'SPP')
    file_name = file_name[:-4]
    PosEvaluator(conn,file_name + 'G.pos', 'SPPG')

if mode.__eq__('1'):
    file_name = file_name[:-4]
    print('FNAME:',file_name)
    PosEvaluator(conn,file_name+'.pos', 'KINEMATIC')
    PosEvaluator(conn,file_name+'_G.pos', 'KINEMATIC')


#conn.close()

#Kinetic+KineticG
#PosEvaluator(conn,kinematic,'KINEMATIC')
#PosEvaluator(conn,file_name+'_kinematic_G.pos','KINEMATICG')

#SBAS+SBASG
#sbas=file_name+'SBAS.pos'
#PosEvaluator(sbas,'SBAS',conn)
#PosEvaluator(file_name+'SBASG.pos','SBASG',conn)



'''conn=pyodbc.connect('Driver={SQL Server};'
                    'Server=192.168.0.32;'
                    'Port=1433;'
                    'Database=Paripa-HC;'
                    'UID=Lehel;'
                    'PWD=Paripa1'
                    )
'''
table='Stations'

exit()

zip_path= save_location +'/PildoBox' + pos_file + ".raw.zip"

for f in os.listdir(save_location):
    if f.endswith('.nav') or f.endswith('.lnav') or f.endswith('.hnav') or f.endswith('.obs') or f.endswith('.pos') or f.endswith('.raw') or f.endswith('.stat') or f.endswith('.sbs'):

        os.remove(save_location+"//"+f)


