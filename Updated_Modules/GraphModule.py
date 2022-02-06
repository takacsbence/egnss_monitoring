import os.path
import sys
import math
from matplotlib.dates import DateFormatter
import matplotlib.pyplot as plt
import pandas as pd
import json


#Ez az excel filebol beolvasott bazisallomas osztaly

def Average(lst):
    return sum(lst) / len(lst)

class Base_station:
    def __init__(self, id, city, lat, long, elev):
        self.id = id
        self.city = city
        self.lat = lat
        self.long = long
        self.elev = elev

    def func(self):
        print("Ertekek" + self.id + self.city)

#check number of args
if len(sys.argv) != 4:
    print("arguments: fn sss uid")
    print("where: fn=pos_file_name, sss=station id, uid=user id")
    print("an example PildoBox20521010c 205 John")
    exit()

#Recommended user inputs
pos_file=str(sys.argv[1])

station=str(sys.argv[2])

uid=str(sys.argv[3])




#Use of config file to determine save location
pic_save=""
with open("config.json","r") as f:
    json_data=json.loads(f.read())
    f.close()
    i=0
    size=len(json_data['Users'])
    while i!=size:
        splited=str(json_data['Users'][i]).split(',')
        user=splited[2]
        user=user[10:-2]
        if user==uid:
            temp=splited[0]
            temp=temp[10:-1]
            pictemp=splited[1]
            pictemp=pictemp[14:-1]
            pic_save=pictemp
            save_location=temp
        i=i+1

station='PildoBox'+station
file_name=save_location +'//'+pos_file+'.pos'

if not os.path.exists(file_name):
    print('Position file does not exists!')
    exit()

dupe_check= pic_save +'//' +pos_file+'.png'

data_stations=pd.read_csv('stations.txt',header=None,delim_whitespace=True)
data_stations.columns=["id","city","lat","long","elev"]
idx=data_stations[data_stations['id']==station].index.item()


#Read position file
data_gps=pd.read_csv(file_name,header=None,delim_whitespace=True,skiprows=15)
data_gps.columns=["date", "time", "lat", "lon", "ele", "mode", "nsat", "stdn", "stde", "stdu", "stdne", "stdeu", "stdun", "age", "ratio"]

times=[]
i=0
while i!=len(data_gps['time']):
    splitted=str(data_gps['time'][i]).split(':')
    hour=splitted[0]
    minute=splitted[1]
    sec=splitted[2]
    i=i+1

dlat = math.pi / 180 * 6380000 / 3600

##TODO error margin for wrong station-pos_file comparison
#Calculate position error in meters
EW_meters=(data_gps['lon']-data_stations._get_value(idx,3,takeable=True))*31*math.cos(dlat)*3600
NS_meters=(data_gps['lat']-data_stations._get_value(idx,2,takeable=True))*31*3600
Elevation=data_gps['ele']-data_stations._get_value(idx,4,takeable=True)

if not os.path.exists(pic_save):
    os.mkdir(pic_save)

data_gps['datetime'] = pd.to_datetime(data_gps['date'] + ' ' + data_gps['time'], format='%Y/%m/%d %H:%M:%S.%f')
fig, ax = plt.subplots()
fig.set_size_inches(10,10)

#EW-graph plot
ax.plot(data_gps['datetime'], EW_meters,label='East-West')
ax.set_ylim([-5,20])
ax.set_xlim([min(data_gps['datetime']).round('60min').to_pydatetime(), max(data_gps['datetime']).round('60min').to_pydatetime()]) #show exactly one hour session
ax.set_xlabel('time (hh:mm)')
ax.set_ylabel('Difference in meters')
ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))


#NS-graph plot
ax.plot(data_gps['datetime'], NS_meters,label='North-South')
#ax.set_ylim([-4,4])
ax.set_xlim([min(data_gps['datetime']).round('60min').to_pydatetime(), max(data_gps['datetime']).round('60min').to_pydatetime()]) #show exactly one hour session
ax.set_xlabel('time (hh:mm)')
ax.set_ylabel('Difference in meters')
ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
fig.set_size_inches(10, 10)
#plt.savefig(pic_save+'//' + station_name+"_" +year+"_"+doy+"_"+ time + ".png",dpi=100)

#Elevation-graph plot
ax.plot(data_gps['datetime'],Elevation,label='Elevation')
ax.set_ylim([-10, 10])
ax.set_xlim([min(data_gps['datetime']).round('60min').to_pydatetime(), max(data_gps['datetime']).round('60min').to_pydatetime()]) #show exactly one hour session
ax.set_xlabel('time (hh:mm)')
ax.set_ylabel('Difference in meters')
ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))

#Number of satellites
ax.plot(data_gps['datetime'],data_gps['nsat'],label='Number of Satellites')
ax.set_ylim([-10, 20])
ax.set_xlim([min(data_gps['datetime']).round('60min').to_pydatetime(), max(data_gps['datetime']).round('60min').to_pydatetime()]) #show exactly one hour session
ax.set_xlabel('time (hh:mm)')
ax.set_ylabel('Meters/Number of Sattelites')
ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
plt.text(data_gps['datetime'][2000],19,"EW: avarage:"+str(round(Average(EW_meters),2))+" min:"+str(round(min(EW_meters),2))+" max:"+str(round(max(EW_meters),2)),fontsize=10)
plt.text(data_gps['datetime'][2000],18.5,"NS: avarage:"+str(round(Average(NS_meters),2))+" min:"+str(round(min(NS_meters),2))+" max:"+str(round(max(NS_meters),2)),fontsize=10)
plt.text(data_gps['datetime'][2000],18,"Elevation: avarage:"+str(round(Average(Elevation),2))+" min:"+str(round(min(Elevation),2))+" max:"+str(round(max(Elevation),2)),fontsize=10)
plt.grid()
ax.set_title('Position Error Graphs')
plt.legend(loc='upper left')

plt.savefig(pic_save+'//' + pos_file + ".png",dpi=100)


print('Graphs created and saved!')

exit()

zip_path= save_location +'/PildoBox' + pos_file + ".raw.zip"

for f in os.listdir(save_location):
    if f.endswith('.nav') or f.endswith('.lnav') or f.endswith('.hnav') or f.endswith('.obs') or f.endswith('.pos') or f.endswith('.raw') or f.endswith('.stat') or f.endswith('.sbs'):

        os.remove(save_location+"//"+f)

