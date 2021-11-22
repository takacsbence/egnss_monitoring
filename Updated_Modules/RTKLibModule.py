import os
import sys
import zipfile
from os.path import exists

#http://152.66.5.8/~tbence/hc/data/Y2021/D010/PildoBox205/PildoBox20521010a.raw.zip
#Egy példa az RTKLibModule használatához: RTKLibModule.py 2021 010 205 a Lehel

if len(sys.argv) != 6:
    print("arguments: yyy ddd sss h uid")
    print("where: yyy  y=year, ddd=day of year, sss=station id, h=hourly session with abc, uid=user id")
    print("an example 2021 10 205 a John")
    exit()

year=str(sys.argv[1])
doy=str(sys.argv[2])
station=str(sys.argv[3])
time=str(sys.argv[4])
uid=str(sys.argv[5])

year_for_filename= year[2:]

temp=""
f = open('config.txt', 'r')
for line in f:
        if(line.split(' ')[0]==sys.argv[5]):
            temp=line.split(' ')[1]


save_location=temp[6:]


zip_path= save_location +'\\PildoBox' + station + year_for_filename + doy + time + ".raw.zip"
print("zip:",zip_path)

if exists(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(save_location)

if not exists(zip_path):
    print("No such file download started!")
    full_command="python DownloadModule.py "+year+" "+doy+" "+station+" "+time+" "+uid
    os.system(full_command)
    exit()


file_to_convert="PildoBox" + station + year_for_filename + doy + time + ".raw"


convert_to_Rinex="convbin "+save_location+"\\"+file_to_convert+" -r sbf -d "+save_location
print("Command:",convert_to_Rinex)
os.system(convert_to_Rinex)

obs= save_location +"\\" +"PildoBox" + station + year_for_filename + doy + time + ".obs"

nav= save_location +"\\" +"PildoBox" + station + year_for_filename + doy + time + ".nav"

sbs= save_location +"\\" +"PildoBox" + station + year_for_filename + doy + time + ".sbs"


fp="rnx2rtkp -k rnxconfig.conf -p 0 -f 1 -f 2 -f 5 -t " + obs +" " + nav +" " + sbs +" -o " + save_location +"\PildoBox" + station + year_for_filename + doy + time + ".pos"
print("fp:",fp)

os.system(fp)



