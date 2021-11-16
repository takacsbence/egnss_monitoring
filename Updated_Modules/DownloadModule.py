import wget
import sys

#http://152.66.5.8/~tbence/hc/data/Y2021/D010/PildoBox205/PildoBox20521010a.raw.zip

#an example to use this script DownloadModule.py 2021 10 205 a

url = 'http://152.66.5.8/~tbence/hc/data/'

#check number of args
if len(sys.argv) != 5:
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

#directory to save data locally
##TODO check if it exists and create if not
##TODO test under linux and windows
save_location = 'data/'

#full url to download
full_url = url + '/Y' + year + '/D' + doy + '/PildoBox' + station + '/PildoBox' + station + year2 + doy + session + '.raw.zip'
print (full_url)

#download
##TODO check if url exists. Do not dwonload if not
##TODO check if the file exists locally. do not dwonload if yes
fn = wget.download(full_url, out = save_location)
