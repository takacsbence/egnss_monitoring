import os
import sys
import zipfile

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

#filename with full path
#local directory
save_location = 'data'
fname = '/PildoBox' + station + year2 + doy + session + '.raw.zip'

#unzip file
#TODO check if zip file exists. Exit with error message if not
#TODO check if unzipped file exists. do not unzip if not
#TODO feedback if everything is okay
zip_path = save_location + fname
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(save_location)

#convert septentrio raw binary into RINEX
#convert_to_Rinex="convbin -f 1 -f 2 -f 5 -r sbf -d D:\Rinex_datas\Extracted_zips D:\Rinex_datas\Extracted_zips\PildoBox20519335"+sys.argv[1]+".raw"
fname = '/PildoBox' + station + year2 + doy + session + '.raw'
convert_to_Rinex="convbin " + save_location + fname + " -r sbf -d " + save_location
print(convert_to_Rinex)
os.system(convert_to_Rinex)

#process with RKTpost
obs = fname[:-4] + '.obs'
nav = fname[:-4] + '.nav'
sbs = fname[:-4] + '.sbs'
pos = fname[:-4] + '.pos'
fp = "rnx2rtkp  -k sbs.conf" + " -o " + save_location + pos + " " + save_location + obs + " " + save_location + nav + " " + save_location + sbs
print(fp)
os.system(fp)

