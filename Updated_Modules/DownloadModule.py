import wget
import sys
import os
import requests

#http://152.66.5.8/~tbence/hc/data/Y2021/D010/PildoBox205/PildoBox20521010a.raw.zip

#an example to use this script DownloadModule.py 2021 10 205 a Lehel

url = 'http://152.66.5.8/~tbence/hc/data/'
##TODO test under linux and windows

#Basic test function for windows
def test_mode(input:str):
    if sys.argv[1]=='Test':
        url="http://152.66.5.8/~tbence/hc/data/Y2021/D010/PildoBox205/PildoBox20521010b.raw.zip"
        f = open('config.txt', 'r')
        for line in f:
            if (line.split(' ')[0] == sys.argv[2]):
                temp = line.split(' ')[1]

        save_location = temp[:-1]

        if not os.path.exists(save_location):
            os.mkdir(save_location)
            print("Directory created!")


        response = requests.get(url)

        if response.status_code !=200:
            print("URL Error!")
            exit()

        if response.status_code==200 and not os.path.exists(save_location+'//'+'PildoBox20521010b.raw.zip'):
            download = wget.download(url, save_location)
            exit()

        if os.path.exists(save_location+'//'+'PildoBox20521010b.raw.zip'):
            print("Existing file!")
            exit()

test_mode(sys.argv[1])

#check number of args
if len(sys.argv) != 6:
    print("arguments: yyy ddd sss h")
    print("where: yyy  y=year, ddd=day of year, sss=station id, h=hourly session with abc")
    print("an example 2021 10 205 a")
    exit()

#format args
year = str(sys.argv[1])
year2 = year[-2:]   #year with the last two characters
doy = int(sys.argv[2])
doy = "{:03d}".format(doy)  #day of year with leading zeros 10->010
station = str(sys.argv[3])
session = str(sys.argv[4])
uid=str(sys.argv[5])

#Read config file and get save_location by user id
save_location=""

f = open('config.txt', 'r')
for line in f:
        if(line.split(' ')[0]==sys.argv[5]):
            temp=line.split(' ')[1]


save_location=temp[:-1]

#directory to save data locally. If directory does not exist create it
if not os.path.exists(save_location):
    os.mkdir(save_location)
    print("Directory created!")

year_for_filename= year[2:]


#full url to download
full_url = url + '/Y' + year + '/D' + doy + '/PildoBox' + station + '/PildoBox' + station + year2 + doy + session + '.raw.zip'

station='PildoBox'+station
dupe_check= save_location +'//' + station + year_for_filename + doy + session + '.raw.zip'


response=requests.get(full_url)
if response.status_code!=200:
    print("URL Error!")

if response.status_code==200 and not os.path.exists(dupe_check) :
    fn = wget.download(full_url, out=save_location)





