import os.path
import sys
from openpyxl import load_workbook
import matplotlib.pyplot as plt
import math
from datetime import date
import datetime

#Ez az excel filebol beolvasott bazisallomas osztaly
class Base_station:
    def __init__(self, id, city, lat, long, elev):
        self.id = id
        self.city = city
        self.lat = lat
        self.long = long
        self.elev = elev

    def func(self):
        print("Ertekek" + self.id + self.city)

#Ez a pos filebol olvasott adatok osztalya
class Gps_data:
    def __init__(self, date, time, lat, lon, ele, mode, nsat, stdn, stde, stdu, stdne, stdeu, stdun, age, ratio):
        self.date = date
        self.time = time
        self.lat = lat
        self.lon = lon
        self.ele = ele
        self.mode = mode
        self.nsat = nsat
        self.stdn = stdn
        self.stde = stde
        self.stdu = stdu
        self.stdne = stdne
        self.stdeu = stdeu
        self.sttun = stdun
        self.age = age
        self.ratio = ratio

#a bazisallomasok tarolasa
listofbst = []
#a pos filebol beolvasott adatok tarolasa
listofpositions = []

year=str(sys.argv[1])

doy=str(sys.argv[2])

station=str(sys.argv[3])

time=str(sys.argv[4])

uid=str(sys.argv[5])

temp=""
pic_save=""
file = open('config.txt', 'r')
for line in file:
        if(line.split(' ')[0]==sys.argv[5]):
            temp=line.split(' ')[1]
            pic_save=line.split(' ')[2]

file.close()

save_location=temp
pic_save=pic_save[:-1]

#ket valtozo ezek lesznek beallitva a megadott idotartam szerint a megfelelo ertekre, hogy a pos file soraibol a jo adatot olvassa az idonek megfeleloen
start=0
stop=0

if(time== 'a'):
    start = 16
    stop = 3616
elif(time == 'b'):
    start = 3616
    stop = 7216
elif(time == 'c'):
    start = 7216
    stop = 10816
elif (time == 'd'):
    start = 10816
    stop = 14416
elif (time == 'e'):
    start = 14416
    stop = 18016
elif (time == 'f'):
    start = 18016
    stop = 21616
elif (time == 'g'):
    start = 21616
    stop = 25216
elif (time == 'h'):
    start = 25216
    stop =28816
elif (time == 'i'):
    start=28816
    stop=32416
elif (time == 'j'):
    start=32416
    stop=36016
elif (time == 'k'):
    start=36016
    stop=39616
elif (time == 'l'):
    start=39616
    stop=43216
elif (time == 'm'):
    start=43216
    stop=46816
elif (time == 'n'):
    start=46816
    stop=50416
elif (time == 'o'):
    start=50416
    stop=54016
elif (time == 'p'):
    start=54016
    stop=57616
elif (time == 'q'):
    start=57616
    stop=61216
elif (time == 'r'):
    start=61216
    stop=64816
elif (time == 's'):
    start=64816
    stop=68416
elif (time == 't'):
    start=68416
    stop=72016
elif (time == 'u'):
    start=72016
    stop=75618
elif (time == 'v'):
    start=75618
    stop=79216
elif (time == 'w'):
    start=79216
    stop=82816
elif (time == 'x'):
    start=82816
    stop=86416

#Ez a valtozo tarolja, hogy melyik bazisallomashoz hasonlitsuk a pos filet, ugy hogy ellenorzi a pos file nevet
base_station=0
station_name=""

if(station=='205'):
    station_name="Budapest"
    base_station=0
elif(station=='206'):
    station_name="Nyiregyhaza"
    base_station=1
elif(station=='207'):
    station_name = "Sarmellek"
    base_station=2
elif(station=='208'):
    station_name = "Szeged"
    base_station=3
elif(station=='209'):
    station_name = "Gyor-Per"
    base_station=4
elif(station=='211'):
    station_name = "Bekescsaba"
    base_station=5
elif(station=='212'):
    station_name = "Debrecen"
    base_station=6
elif(station=='213'):
    station_name = "Pecs-Pogany"
    base_station=7
elif(station=='214'):
    station_name = "Bugac"
    base_station=8
elif(station=='215'):
    station_name = "Sajohidveg"
    base_station=9
elif(station=='210'):
    station_name = "Sagvar"
    base_station=10

year_for_filename= year[2:]
station='PildoBox'+station
file_name=save_location +'//' + station + year_for_filename + doy + time + '.pos'

dupe_check= pic_save +'//' + station +"_"+ year+"_" + doy+"_" + time + '.png'

##Todo Dupe_Check
if os.path.exists(dupe_check):
    print("Duplicate Detected!")
    exit()

#Itt olvassa be a pos filet jelenleg a felhasznalo altal kivalasztott idokereten belul D:\Rinex_datas\HC-Nyiregyhaza_17-10-2021_17-10-2021.pos
f = open(file_name,'r')
for x, line in enumerate(f):
    if x >= start and x <= stop:
        converted = str(line)
        splitted = converted.split()
        element=Gps_data(splitted[0],splitted[1],float(splitted[2]),float(splitted[3]),float(splitted[4]),splitted[5],splitted[6],splitted[7],splitted[8],splitted[9],splitted[10],splitted[11],splitted[12],splitted[13],splitted[14])
        listofpositions.append(element)

f.close()
difference_list=[]

path = "stations4.xlsx"
wb = load_workbook(path)
ws = wb.active
x = 2

#Itt olvassa be a bazisallomasokat az excel filebol
while x != 12:
    converter = str(x)
    ID = ws['A' + converter].value
    city = ws['B' + converter].value
    latitude = ws['C' + converter].value
    longitude = ws['D' + converter].value
    elevation = ws['E' + converter].value
    basestc = Base_station(ID, city, latitude, longitude, elevation)
    listofbst.append(basestc)
    x = x + 1

y=0
x=0
Rfold=6378.137
rad=0.000008998719243599958
differences_by_city=[]


while y != len(listofpositions):
    diff_in_degree=listofbst[base_station].long - listofpositions[y].lon
    dlat=(listofbst[base_station].lat*math.pi/180) - (listofpositions[y].lat*math.pi/180)
    dlong=(listofbst[base_station].long*math.pi/180) - (listofpositions[y].lon*math.pi/180)
    a_val=math.sin(dlat/2)*math.sin(dlat/2)+ math.cos((listofbst[base_station].lat)*math.pi/180)*math.cos((listofpositions[y].lat)*math.pi/180)*math.sin(dlong/2)*math.sin(dlong/2)
    c=2*math.atan2(math.sqrt(a_val),math.sqrt(1-a_val))
    diff_in_kms=Rfold*c
    diff_in_meters=diff_in_kms*1000
    val=(math.sqrt(math.pow(listofbst[base_station].lat-listofpositions[y].lat,2))+math.pow(listofbst[base_station].long-listofpositions[y].lon,2))/rad
    conv_to_meter=diff_in_degree*31
    differences_by_city.append(diff_in_meters)
    y=y+1

x_axis=[]
y_axis=[]
i=0

#A grafikon x tengelyet feltolti 3600s-al
while i != 3600:
    x_axis.append(datetime.timedelta(seconds=i))
    i=i+1


#Az y tengely pedig az eltereseket abrazolja
y_axis=differences_by_city

today = date.today()

#Itt tortenik a grafikon kirajzolasa
it=0
while it!=3599:
    plt.scatter(str(x_axis[it]), y_axis[it], color="red",marker="*", s=30)
    it=it+1

plt.xlabel('x - axis in seconds')
plt.ylabel('y - axis in meters')
plt.title('E-W Pos differences')
plt.legend()

#Itt menti el egy mappaba a grafikonokat kepkent az adott bazisallomas nevevel es az adott nap datumaval, ha már ki van értékelve egy adott pos file azt nem duplikálja, hanem felülírja
plt.savefig(pic_save+'//' + station_name+"_" +year+"_"+doy+"_"+ time + ".png")

plt.show()

zip_path= save_location +'\\PildoBox' + station + year_for_filename + doy + time + ".raw.zip"

for f in os.listdir(save_location):
    if f.endswith('.nav') or f.endswith('.lnav') or f.endswith('.hnav') or f.endswith('.obs') or f.endswith('.pos') or f.endswith('.raw') or f.endswith('.stat') or f.endswith('.sbs'):
        print("torolt file:\n",str(f))
        os.remove(save_location+"\\"+f)

