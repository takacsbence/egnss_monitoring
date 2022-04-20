#!/usr/bin/env python3

#Ennek a programnak a celja hogy eloallitsa a pozicio filet amit abrazolunk egy kesobbi modullal, egy input kell a usertol az pedig a mod ami megadja hogy SPP vagy RTK
#Mivel automatikusan fog futni igy ugy terveztem hogy az SPP mindig megcsinalja egyszerre az elozo naphoz tartozo kepeket mig az RTK modszer pedig az adott napon
#orankent fut es csinalja a kepeket, a vegen pedig a program torli a felesleges fileokat

import os
import zipfile
from os.path import exists
import platform
from datetime import date,datetime
import sys

#Datum meghatarozasa
todays_date = date.today()
d0 = date(todays_date.year, 1, 1)
d1 = date(todays_date.year, todays_date.month, todays_date.day)
delta = d1 - d0
    
#Tegnapi datum
doy=str(delta)
doy=str(doy)[:-14]
if len(doy)<3:
    doy='0'+doy

#Mai datum
tmp=int(doy)+1
real_day=str(tmp)
if len(real_day)<3:
    real_day='0'+real_day

#real_day='0'+str(real_day)



os_type=''

if platform.system()=='Linux':
    os_type='Linux'
if platform.system()=='Windows':
    os_type='Windows'
if platform.system()=='Darwin':
    os_type='Darwin'


year=str(todays_date.year)

url = 'http://152.66.5.8/~tbence/hc/data/'

#0 akkor SPP ha 1 akkor RTK
mode=sys.argv[1]


save_location='/home/hegyi/Paripa/Downloaded_zips'
ref_data_save='/home/hegyi/Paripa/Reference_for_Kinematic'

#A PildoAdatok eleresehez szukseges
mirror='/home/tbence/HC/data/Y'+year+'/D'+doy
mirror2='/home/tbence/HC/data/Y'+year+'/D'+real_day



def evalFiles(station,timer,container,prev_time):


    print('timer:'+str(timer))
    year_for_filename = year[2:]
    station_number=station
    
    files=mirror+'/PildoBox'+str(station)+'/PildoBox' + str(station) + year_for_filename + str(doy) + timer + ".raw.zip"
    files_for_hourly=mirror2+'/PildoBox'+str(station)+'/PildoBox' + str(station) + year_for_filename + real_day + timer + ".raw.zip"

    #nav_handler = "python GetNavData.py " + str(year) + " " + str(doy)  # + " " + uid
    #nav_for_hourly="python GetNavData.py " + str(year) + " " + real_day
    '''if mode.__eq__('1'):
        os.system(nav_for_hourly)

    if mode.__eq__('0'):
        os.system(nav_handler)
    '''
    
    
    
    #zip_path= save_location +'/PildoBox' + str(station) + year_for_filename + str(doy) + timer + ".raw.zip"

    if mode.__eq__('0'):
        zip_path=files

    if mode.__eq__('1'):
        zip_path=files_for_hourly    
    
    #Zip file kicsomagolasa
    print('zip:'+zip_path)
    if exists(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(save_location)
    #SPP-hez a fileok
    file_to_convert = "PildoBox" + str(station) + year_for_filename + str(doy) + timer + ".raw"
    #real_day=doy
    #RTKhoz a fileok
    file_to_convert2 = "PildoBox" + str(station) + year_for_filename + real_day + timer + ".raw"
    print('file',file_to_convert2)

    year_for_filename = year[2:]

    convert_to_Rinex = "convbin " + save_location + "/" + file_to_convert + " -v 3.03 -r sbf -f 1 -y J,C,S,R,E -d " + save_location
    convert_hourly="convbin " + save_location + "/" + file_to_convert2 + " -v 3.03 -r sbf -f 1 -y J,C,S,R,E -d " + save_location

    #Navigacios fileok eloallitasa SPP
    if mode.__eq__('0'):
        nav_Galileo='sbf2rin -f '+save_location + "/" + file_to_convert+' -R3 -n E -o '+save_location+'/PildoBox'+str(station)+year_for_filename + str(doy) + timer+'.enav'
        nav_GPSGalileo='sbf2rin -f '+save_location + "/" + file_to_convert+' -R3 -n N -o '+save_location+'/PildoBox'+str(station)+year_for_filename + str(doy) + timer+'.nav'

        os.system(nav_Galileo)
        os.system(nav_GPSGalileo)

    #Navigacios fileok eloallitasa RTK
    if mode.__eq__('1'):
        nav_Galileo_RTK='sbf2rin -f '+save_location+'/'+file_to_convert2+' -R3 -n E -o '+save_location+'/PildoBox'+str(station)+year_for_filename + str(doy) + timer+'.enav'
        nav_GPS_RTK='sbf2rin -f '+save_location+'/'+file_to_convert2+' -R3 -n N -o '+save_location+'/PildoBox'+str(station)+year_for_filename + str(doy) + timer+'.nav'
        
        os.system(nav_Galileo_RTK)
        os.system(nav_GPS_RTK)

    if mode.__eq__('0'):
        obs = save_location + "/" + "PildoBox" + str(station) + year_for_filename + str(doy) + timer + ".obs"
        
        nav_new=save_location+'/PildoBox'+str(station)+year_for_filename+str(doy)+timer+".nav"
        nav_new_g=save_location+'/PildoBox'+str(station)+year_for_filename+str(doy)+timer+".enav"

           
    #sbs = save_location + "/" + "PildoBox" + str(station) + year_for_filename + str(doy) + timer + ".sbs"

    if mode.__eq__('1'):
        #obs = save_location + "/" + "PildoBox" + str(station) + year_for_filename + real_day + timer + ".obs"
        nav_new=save_location+'/PildoBox'+str(station)+year_for_filename+real_day+timer+".nav"
        nav_new_g=save_location+'/PildoBox'+str(station)+year_for_filename+real_day+timer+".enav"

        #nav = save_location + '/BRDC00WRD_R_' + str(year) + real_day + '0000_01D_MN.rnx

    if flag==1 and mode.__eq__('0'):
        x='a'
        val = chr(ord(x) + prev_time-1)
        print('CHAR:',val)
        nav_new=save_location+'/PildoBox'+str(station)+year_for_filename+str(doy)+val+".nav"

    '''if flag==1 and mode.__eq__('1'):
        x='a'
        val = chr(ord(x) + prev_time-1)
        print('CHAR:',val)
        nav_new=save_location+'/PildoBox'+str(station)+year_for_filename+real_day+val+".nav"'''

    

            
        
    #/home/hegyi/Paripa/Reference_for_Kinematic/PildoBox205202210306
    if station.__eq__('205') and mode.__eq__('1'):
        rtcm_file_name='/home/hegyi/Paripa/Reference_for_Kinematic/Pildobox205'+year+real_day+ftime+'.rtcm3'
        convert_rtcm="convbin "+rtcm_file_name+" -r rtcm3 -v 3.03 -f 1 -d "+ '/home/hegyi/Paripa/Reference_for_Kinematic/'
        os.system(convert_rtcm)
        obs = save_location + "/" + "PildoBox" + str(station) + year_for_filename + real_day + timer + ".obs"
        #exit()

        nav_Galileo_RTK='sbf2rin -f '+save_location+'/'+file_to_convert2+' -R3 -n E -o '+save_location+'/PildoBox'+str(station)+year_for_filename + real_day + timer+'.enav'
        nav_GPS_RTK='sbf2rin -f '+save_location+'/'+file_to_convert2+' -R3 -n N -o '+save_location+'/PildoBox'+str(station)+year_for_filename + real_day + timer+'.nav'
        if flag==1:
            nav_GPS_RTK='sbf2rin -f '+save_location+'/'+file_to_convert2+' -R3 -n N -o '+save_location+'/PildoBox'+str(station)+year_for_filename + real_day + prev_time+'.nav'
            nav_nev=nav_new=save_location+'/PildoBox'+str(station)+year_for_filename+real_day+prev_time+".nav"
            exit()

        
        os.system(nav_Galileo_RTK)
        os.system(nav_GPS_RTK)

        obs_ref=ref_data_save+'/PildoBox205'+year+real_day+ftime+".obs"
        print('\n obs_ref:'+obs_ref)
        
        
        nav_new='/home/hegyi/Paripa/Downloaded_zips/PildoBox20522108c.nav'
        print('NAV:'+nav_new)
        kinematic = "rnx2rtkp -k test_config2.conf " + obs + " " + obs_ref + " " + nav_new + " -r 4082000.925 1410145.630 4678053.713 -o " +save_location +'/'+real_day+container+ '/PildoBox' +str(station) + year_for_filename + real_day + ftime + "_kinematic" + ".pos"
        kinematic_G = "rnx2rtkp -k test_config.conf " + obs + " " + obs_ref + " " + nav_new + " -r 4082000.925 1410145.630 4678053.713 -o " + save_location +'/'+real_day+container+ '/PildoBox' +str(station) + year_for_filename + real_day + ftime +"_kinematic_G" + ".pos"
        os.system(kinematic)
        os.system(kinematic_G)
        pos_file_rtk='PildoBox'+str(station)+year_for_filename+real_day+ftime+'_kinematic'
        

    #obs = save_location + "/" + "PildoBox" + str(station) + year_for_filename + str(doy) + timer + ".obs"

    #obs2 = save_location + '/BUTE' + str(doy) + timer + '.21/BUTE' + str(doy) + timer + '.' + year_for_filename + 'd'
    #obs2 = save_location + '\BUTE' + str(doy) + timer + '.' + year_for_filename + '\BUTE' + str(doy) + timer + '.' + year_for_filename + 'd'
        

    station = '/PildoBox' + str(station)


    #nav='C:\Paripa\Downloaded_zips\BRDC00WRD_R_20220550000_01D_MN.rnx'
    #nav2 = save_location + '/BRDC00WRD_R_' + str(year) + str(doy) + '0000_01D_GN.'

    #"C:\Paripa\Downloaded_zips\BRDC00WRD_R_20210100000_01D_MN"
    if mode.__eq__('0'):
        os.system(convert_to_Rinex)

    if mode.__eq__('1'):
        os.system(convert_hourly)
    

    # SPP with Gps and Gps+Galileo

    path=save_location +'/'+str(doy)
    path2=save_location+'/'+real_day

    if not os.path.exists(path2):
        os.mkdir(path2)

    if not os.path.exists(path):
        os.mkdir(path)

    if mode.__eq__('0'):
        SPP = "rnx2rtkp -k rnxconfig.conf -p 0 -f 1 -f 2 -f 5 -t " + obs + " " + nav_new + " -o " + save_location +'/'+str(doy)+container+ str(station) + year_for_filename + str(doy) + timer + ".pos"
        SPPG = "rnx2rtkp -k rnxconfig_gal.conf -p 0 -f 1 -f 2 -f 5 -t " + obs + " " + nav_new + " -o " + save_location +'/'+str(doy)+container+ str(station) + year_for_filename + str(doy) + timer + "G.pos"
        os.system(SPP)
        os.system(SPPG)
        pos_file=str(station) + year_for_filename + str(doy) + timer
        pos_file=pos_file[1:]
        #print('POS:FILE'+pos_file)

    '''if mode.__eq__('1'):
        SPP = "rnx2rtkp -k rnxconfig.conf -p 0 -f 1 -f 2 -f 5 -t " + obs + " " + nav_new + " -o " + save_location +'/'+real_day+container+ str(station) + year_for_filename + real_day + timer + ".pos"
        SPPG = "rnx2rtkp -k rnxconfig_gal.conf -p 0 -f 1 -f 2 -f 5 -t " + obs + " " + nav_new + " -o " + save_location +'/'+real_day+container+ str(station) + year_for_filename + real_day + timer + "G.pos"
        os.system(SPP)
        os.system(SPPG)
        #pos_file=str(station) + year_for_filename + real_day + timer'''


    
    #SBAS = "rnx2rtkp -k rnxconfigSBAS.conf " + obs + " " + nav + " -o " + save_location +'/'+str(doy)+container+ str(station) + year_for_filename + str(doy) + timer + "SBAS.pos"

    # fp2="rnx2rtkp -k rnxconfig2.conf " + obs +" " + nav +" " + sbs +" -o " + save_location + station + year_for_filename + doy + time +"_egnos"+ ".pos"

    # /usr/local/bin/rnx2rtkp -k ~/HC/util/SSSS_rtk.conf -r 4081881.803 1410011.610 4678199.731 -o $fname"_rtk.out" $fname$year2"o" $fname$year2"n" $fname$year2"l" $bute_ref_30

    # SBAS
    #os.system(SBAS)

    
    if mode.__eq__('0'):
        Graph_maker = "python3 GraphModule.py " + pos_file+' '+str(station_number)+' '+mode
        print('pos:'+Graph_maker)
        os.system(Graph_maker)

    if mode.__eq__('1'):
        Graph_maker = "python3 GraphModule.py " + pos_file_rtk+' '+str(station_number)+' '+mode
        os.system(Graph_maker)
    

    for f in os.listdir(save_location):
        if f.endswith('.lnav') or f.endswith('.hnav') or f.endswith('.obs') or f.endswith('.raw') or f.endswith('.stat') or f.endswith('.sbs') or f.endswith('_events.pos'):
            os.remove(save_location +"//" + f)

    if os.path.exists(save_location+'/'+str(doy)+container):
        for f in os.listdir(save_location+'/'+str(doy)+container):
            if f.endswith('.pos.stat') or f.endswith('_events.pos'):
                os.remove(save_location+'/'+str(doy)+container+'/'+f)
    

time_stamps=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w']

check=0
flag=0

if mode.__eq__('0'):
    i=205
    while i!=216:
        container='/PildoBox'+str(i)
        for a in range(24):
            check=check+1
            if check==2:
                flag=1
                check=0

            x = 'a'
            val = chr(ord(x) + a)
            evalFiles(i,val,container,a)
            flag=0
        i=i+1

now = datetime.now()
ctime=str(now.hour)
ctime=int(ctime)-1
ctime=str(ctime)
ftime=str(int(ctime)-2)
print(ftime)


if mode.__eq__('1'):
    idx=int(ctime)-2
    i=205
    container='/PildoBox'+str(i)
    #Itt ellenorzom hogy az adott idoben a nav file megfelelo adatokat tartalmaz ha nem akkor az  egy oraval elozot vizsgalom
    if idx%2==1:
        flag=1    
    evalFiles(i,time_stamps[idx],container,time_stamps[idx-1])

for f in os.listdir(save_location):
    if f.endswith('.rnx') or f.endswith('.gz'):
        os.remove(save_location +"//" + f)
