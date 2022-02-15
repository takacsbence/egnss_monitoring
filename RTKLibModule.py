import os
import sys
import zipfile
from os.path import exists
import wget
import requests
import patoolib
import platform
import json


os_type=''

if platform.system()=='Linux':
    os_type='Linux'
if platform.system()=='Windows':
    os_type='Windows'
if platform.system()=='Darwin':
    os_type='Darwin'


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

doy="0"+doy

year_for_filename= year[2:]

with open("config.json","r") as f:
    json_data=json.loads(f.read())
    f.close()
    i=0
    size=len(json_data['Users'])
    while i!=size:
        splited=str(json_data['Users'][i]).split(',')
        user=splited[2]
        user=user[10:-2]
        if user==sys.argv[5]:
            temp=splited[0]
            temp=temp[10:-1]
            save_location=temp
        i=i+1

zip_path= save_location +'/PildoBox' + station + year_for_filename + doy + time + ".raw.zip"
print("zip:",zip_path)

if not os.path.exists(save_location):
    os.mkdir(save_location)
    print("Directory created!")

if exists(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(save_location)

if not exists(zip_path):
    print("No such file download started!")
    full_command="python DownloadModule.py "+year+" "+doy+" "+station+" "+time+" "+uid
    os.system(full_command)
    exit()

file_to_convert="PildoBox" + station + year_for_filename + doy + time + ".raw"


##TODO Finalize all os compatibility
if os_type=='Windows':
    convert_to_Rinex_Galileo = "convbin " + save_location + "\\" + file_to_convert + " -r sbf -f 1 -y J,C,S,R -d  " + save_location+'\\Galileo'
    convert_to_Rinex = "convbin " + save_location + "\\" + file_to_convert + " -r sbf -f 1 -y J,C,S,R,E -d " + save_location

    obs="C:\Paripa\Downloaded_zips"+"\\" +"PildoBox" + station + year_for_filename + doy + time + ".obs"
    #obs= save_location +"\\" +"PildoBox" + station + year_for_filename + doy + time + ".obs"

    obs2 = "C:\Paripa\Downloaded_zips\BUTE010a.21d\BUTE010a.21d"
    #save_location + '\\BUTE' + doy + time + '.21d\\BUTE' + doy + time + '.21d'

    #C:\Paripa\Downloaded_zips\BUTE010a.21d\BUTE010a.21d

    l_file="C:\Paripa\Downloaded_zips\BUTE010a.21d\BUTE010a.21l"

    nav= save_location +"\\" +"PildoBox" + station + year_for_filename + doy + time + ".nav"

    nav2 = "C:\Paripa\Downloaded_zips" + "\\" + "PildoBox" + station + year_for_filename + doy + time + ".*nav"

    sbs= save_location +"\\" +"PildoBox" + station + year_for_filename + doy + time + ".sbs"

    station='\\PildoBox'+station

    new_nav = save_location + '\\brdc' + doy + '0.' + year_for_filename + 'n.gz'

if os_type=='Linux' or os_type == 'Darwin':
    obs = save_location + "/" + "PildoBox" + station + year_for_filename + doy + time + ".obs"

    obs2=save_location+'/BUTE'+doy+time+'.21d/BUTE'+doy+time+'.21d'

    nav = save_location + "/" + "PildoBox" + station + year_for_filename + doy + time + ".nav"

    sbs = save_location + "/" + "PildoBox" + station + year_for_filename + doy + time + ".sbs"

    convert_to_Rinex = "convbin " + save_location + "/" + file_to_convert + " -r sbf -d " + save_location

    station = '/PildoBox' + station

    new_nav = save_location + '/brdc' + doy + '0.' + year_for_filename + 'n.gz'

#Execute convbin
#print("Command:",convert_to_Rinex)
os.system(convert_to_Rinex)
os.system(convert_to_Rinex_Galileo)


#Check if nav file is valid, if not download one
if os.path.getsize(nav)<=4000:
    year='20'+year_for_filename
    print("Hibas Nav file!")
    nav_file='brdc'+doy+'0.'+year_for_filename+'n.gz'
    download_url='https://igs.bkg.bund.de/root_ftp/EUREF/BRDC/'+year+'/'+doy+'/'+nav_file
    #print(file_path)
    #wget https://igs.bkg.bund.de/root_ftp/EUREF/obs/2020/004/ACOR00ESP_R_20200040000_01D_EN.rnx.gz

    response = requests.get(download_url)
    if response.status_code != 200:
        print("URL Error!")

    dupe_check = save_location + '/' + nav_file

    if response.status_code == 200 and not os.path.exists(dupe_check):
        wget.download(download_url, out=save_location)
        zip_path_to_nav = save_location + '/' + nav_file
        patoolib.extract_archive(zip_path_to_nav, outdir=save_location)

    if os_type == 'Windows':
        nav = save_location + "\\brdc" + doy + '0.21n'
    if os_type == 'Linux' or os_type == 'Darwin':
        nav = save_location + "/brdc" + doy + '0.21n'
#SPP with Gps and Gps+Galileo
SPP="rnx2rtkp -k rnxconfig.conf -p 0 -f 1 -f 2 -f 5 -t " + obs +" " + nav +" -o " + save_location + station + year_for_filename + doy + time + ".pos"
SPPG="rnx2rtkp -k rnxconfig_gal.conf -p 0 -f 1 -f 2 -f 5 -t " + obs +" " + nav +" -o " + save_location + station + year_for_filename + doy + time + "G.pos"
##TODO meg egy feldolgozas sbs használatával
fp2="rnx2rtkp -k rnxconfig2.conf " + obs +" " + nav +" " + sbs +" -o " + save_location + station + year_for_filename + doy + time +"_egnos"+ ".pos"

#/usr/local/bin/rnx2rtkp -k ~/HC/util/SSSS_rtk.conf -r 4081881.803 1410011.610 4678199.731 -o $fname"_rtk.out" $fname$year2"o" $fname$year2"n" $fname$year2"l" $bute_ref_30

#Kinematic with Gps and Gps+Galileo
kinematic="rnx2rtkp -k test_config2.conf "+ obs2 +" "+ obs +" "  + nav2 +" " + "-r 4081881.803 1410011.610 4678199.731 -o "+save_location + station + year_for_filename + doy + time+"_kinematic"+".pos"
kinematic_G="rnx2rtkp -k test_config.conf "+ obs2 +" "+ obs +" "  + nav2 +" " + "-r 4081881.803 1410011.610 4678199.731 -o "+save_location + station + year_for_filename + doy + time+"_kinematic_G"+".pos"
#print("fp:",fp)

#SPP
os.system(SPP)
os.system(SPPG)
#os.system(fp2)

#Kinematic
os.system(kinematic)
os.system(kinematic_G)

#rnx2rtkp -k test_config.conf "+ obs2 +" "+ obs +" "  + nav2 +" " + "-r 4081881.803 1410011.610 4678199.731 -o "+save_location + station + year_for_filename + doy + time+"_kinematic"+".pos"

#rnx2rtkp -k C:\Users\hegyi\PycharmProjects\Paripa1\SSSS_rtk.conf C:\Paripa\Downloaded_zips\PildoBox20521010a.obs C:\Paripa\Downloaded_zips\BUTE010a.21d\BUTE010a.21d C:\Paripa\Downloaded_zips\PildoBox20521010a.nav -r 4081881.803 1410011.610 4678199.731 -o C:\Paripa\Downloaded_zips\test.pos
