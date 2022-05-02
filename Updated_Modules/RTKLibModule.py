#!/usr/bin/python3


import os
import zipfile
from os.path import exists
import platform
from datetime import date, datetime, timedelta
import sys

def hour2session(hour):
    session_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w']
    return session_list[int(hour)]

if __name__ == "__main__":

    #user input
    station = sys.argv[1]

    #date and time parameters
    last_hour_date_time = datetime.utcnow() - timedelta(hours = 1)
    doy = last_hour_date_time.strftime("%j")
    year = last_hour_date_time.strftime("%Y")
    year2 = last_hour_date_time.strftime("%y")
    hour = last_hour_date_time.strftime("%H")
    last_hour = datetime.utcnow() - timedelta(hours = 2)
    prev_time = last_hour.strftime("%H")
    print('hr:'+hour,'prev:'+prev_time)

    #convert hour to abc session
    session = hour2session(hour)
    session2 = hour2session(prev_time)
    print(year2, doy, hour, session)

    #input and output data folders
    raw_data_folder = '/home/tbence/HC/data/Y' + year + '/D' + doy + '/PildoBox' + station + '/' #raw data
    save_location = '/home/hegyi/Paripa/Downloaded_zips'            #pos files
    ref_data_save = '/home/hegyi/Paripa/Reference_for_Kinematic'    #reference station data
    #TB átírtam tbence-re
    #unzipped_raw_data_folder = '/home/tbence/Paripa/Downloaded_zips/Y' + year + '/D' + doy + '/PildoBox' + station  + '/' #processed data folder
    unzipped_raw_data_folder = '/home/hegyi/Paripa/Downloaded_zips/Y' + year + '/D' + doy + '/PildoBox' + station  + '/' #processed data folder
    conf_folder = '/home/tbence/Paripa/conf/'
    
    #unzip raw file
    raw_data_file = 'PildoBox' + station + year2 + doy + session + ".raw.zip"
    
    if exists(raw_data_folder + raw_data_file):
        with zipfile.ZipFile(raw_data_folder + raw_data_file, 'r') as zip_file:
            zip_file.extractall(unzipped_raw_data_folder)
    
    raw_data_file = raw_data_file[:-4]

    #convert RTCM raw binary reference file to RINEX
    hour2 = f'{int(hour):02d}'
    #rtcm_folder = '/home/hegyi/Paripa/Reference_for_Kinematic/BME10/'
    rtcm_folder = '/home/tbence/Paripa/Reference_for_Kinematic/BUTE0/'
    #rtcm_file_name = 'Ref' + year2 + doy + hour2 + '.rtcm'
    rtcm_file_name = 'BUTE0' + year2 + doy + hour2 + '.rtcm'
    print('FName:',rtcm_folder+rtcm_file_name)
    
    if exists(rtcm_folder + rtcm_file_name):
        #ref_obs_file = 'Ref' + station + year2 + doy + session + ".obs"
        ref_obs_file = 'BUTE0' + station + year2 + doy + session + ".obs"
        convert_rtcm = "/usr/local/bin/convbin " + rtcm_folder + rtcm_file_name + " -r rtcm3 -v 3.03 -o " + unzipped_raw_data_folder + ref_obs_file
        print(convert_rtcm)
        os.system(convert_rtcm)
        
    
    #convert septentrio raw binary files to RINEX
    if exists(unzipped_raw_data_folder + raw_data_file):
        #observation file
        obs_file = raw_data_file[:-3] + 'obs'
        convert_to_Rinex = "/usr/local/bin/convbin " + unzipped_raw_data_folder + raw_data_file + " -v 3.03 -r sbf -d " + unzipped_raw_data_folder
        os.system(convert_to_Rinex)
               

        #navigation file, mixed
        nav_file = raw_data_file[:-3] + 'nav'
        convert_to_Rinex = "/opt/Septentrio/RxTools/bin/sbf2rin -f " + unzipped_raw_data_folder + raw_data_file + " -R3 -n P -o " + unzipped_raw_data_folder + nav_file
        if int(hour) % 2 == 1:
            nav_file = nav_file[:-5] + session2 + '.nav'
            #convert_to_Rinex = "/opt/Septentrio/RxTools/bin/sbf2rin -f " + unzipped_raw_data_folder + raw_data_file + " -R3 -n P -o " + unzipped_raw_data_folder + nav_file
            print('Bad_NAV:'+nav_file)
        else :
            print('GOOD nav')
        os.system(convert_to_Rinex)
        
                   

    #post processing
        #SPP - GPS
        pos_file = raw_data_file[:-4] + '_spp.pos'
        conf = conf_folder + 'SSSS_sps.conf'
        pp = "/usr/local/bin/rnx2rtkp -k " + conf + " -p 0 " + unzipped_raw_data_folder + obs_file + " " \
                + unzipped_raw_data_folder + nav_file + " -o " + unzipped_raw_data_folder + pos_file
        os.system(pp)
        #generate plots
        le = "python3 /home/hegyi/Paripa/Paripa1/GraphModule.py " + unzipped_raw_data_folder + pos_file + " " + station + " 0"
        #gr = "python3 /home/tbence/RTK_lib_automatizalas/Updated_Modules/GraphModule.py " + unzipped_raw_data_folder + pos_file + " " + station + " 0"
        os.system(le)
        
        
        #SPP - GPS+GAL
        pos_file = raw_data_file[:-4] + '_spp_G.pos'
        conf = conf_folder + 'SSSS_sps_gal.conf'
        pp = "/usr/local/bin/rnx2rtkp -k " + conf + " -p 0 " + unzipped_raw_data_folder + obs_file + " " \
                + unzipped_raw_data_folder + nav_file + " -o " + unzipped_raw_data_folder + pos_file
        os.system(pp)
        #generate plots
        le = "python3 /home/hegyi/Paripa/Paripa1/GraphModule.py " + unzipped_raw_data_folder + pos_file + " " + station + " 0"
        #gr = "python3 /home/tbence/RTK_lib_automatizalas/Updated_Modules/GraphModule.py " + unzipped_raw_data_folder + pos_file + " " + station + " 0"
        os.system(le)

        #SBAS - GPS
        sbs_file = raw_data_file[:-3] + 'sbs'
        pos_file = raw_data_file[:-4] + '_sbas.pos'
        conf = conf_folder + 'SSSS_sbs.conf'
        pp = "/usr/local/bin/rnx2rtkp -k " + conf + " -p 0 " + unzipped_raw_data_folder + obs_file + " " + unzipped_raw_data_folder + sbs_file + " " \
                + unzipped_raw_data_folder + nav_file + " -o " + unzipped_raw_data_folder + pos_file
        os.system(pp)

        #RTK - GPS
        pos_file = raw_data_file[:-4] + '_rtk.pos'
        conf = conf_folder + 'SSSS_rtk.conf'
        #pp = "/usr/local/bin/rnx2rtkp -k " + conf + " -p 2 " + unzipped_raw_data_folder + obs_file + " " + unzipped_raw_data_folder + ref_obs_file + " " \
        #        + unzipped_raw_data_folder + nav_file + " -r 4082001.389 1410144.844 4678052.918" + " -o " + unzipped_raw_data_folder + pos_file
        pp = "/usr/local/bin/rnx2rtkp -k " + conf + " -p 2 " + unzipped_raw_data_folder + obs_file + " " + unzipped_raw_data_folder + ref_obs_file + " " \
                + unzipped_raw_data_folder + nav_file + " -r 4081882.37127 1410011.14595 4678199.39545" + " -o " + unzipped_raw_data_folder + pos_file
        os.system(pp)
        #generate plots
        le = "python3 /home/hegyi/Paripa/Paripa1/GraphModule.py " + unzipped_raw_data_folder + pos_file + " " + station + " 1"
        #gr = "python3 /home/tbence/RTK_lib_automatizalas/Updated_Modules/GraphModule.py " + unzipped_raw_data_folder + pos_file + " " + station + " 1"
        os.system(le)

        #RTK - GPS+GAL
        pos_file = raw_data_file[:-4] + '_rtk_G.pos'
        conf = conf_folder + 'SSSS_rtk_gal.conf'
        #pp = "/usr/local/bin/rnx2rtkp -k " + conf + " -p 2 " + unzipped_raw_data_folder + obs_file + " " + unzipped_raw_data_folder + ref_obs_file + " " \
        #        + unzipped_raw_data_folder + nav_file + " -r 4082001.389 1410144.844 4678052.918" + " -o " + unzipped_raw_data_folder + pos_file
        pp = "/usr/local/bin/rnx2rtkp -k " + conf + " -p 2 " + unzipped_raw_data_folder + obs_file + " " + unzipped_raw_data_folder + ref_obs_file + " " \
                + unzipped_raw_data_folder + nav_file + " -r 4081882.37127 1410011.14595 4678199.39545" + " -o " + unzipped_raw_data_folder + pos_file
        os.system(pp)
        #generate plots
        #gr = "python3 /home/tbence/RTK_lib_automatizalas/Updated_Modules/GraphModule.py " + unzipped_raw_data_folder + pos_file + " " + station + " 1"
        le = "python3 /home/hegyi/Paripa/Paripa1/GraphModule.py " + unzipped_raw_data_folder + pos_file + " " + station + " 1"
        
        os.system(le)
        
        delete_path = save_location + '/Y' + year + '/D' + doy + '/PildoBox' + station + '/'
        for f in os.listdir(delete_path):
            if f.endswith('.lnav') or f.endswith('.obs') or f.endswith('.raw') or f.endswith('.stat') or f.endswith('_events.pos'):
                os.remove(delete_path + f)
        
'''







def evalFiles(station,timer,container,prev_time):

    station_number=station
    files=mirror+'/PildoBox'+str(station)+'/PildoBox' + str(station) + year_for_filename + str(doy) + timer + ".raw.zip"
    files_for_hourly=mirror2+'/PildoBox'+str(station)+'/PildoBox' + str(station) + year_for_filename + real_day + timer + ".raw.zip"

    if mode.__eq__('0'):
        zip_path=files

    if mode.__eq__('1'):
        zip_path=files_for_hourly    
    

    print('zip:'+zip_path)

    file_to_convert = "PildoBox" + str(station) + year_for_filename + str(doy) + timer + ".raw"
    file_to_convert2 = "PildoBox" + str(station) + year_for_filename + real_day + timer + ".raw"

    year_for_filename = year[2:]

    convert_hourly="convbin " + save_location + "/" + file_to_convert2 + " -v 3.03 -r sbf -f 1 -y J,C,S,R,E -d " + save_location

    #Navigacios fileok eloallitasa SPP
    if mode.__eq__('0'):
        nav_Galileo='/opt/Septentrio/RxTools/bin/sbf2rin -f '+save_location + "/" + file_to_convert+' -R3 -n E -o '+save_location+'/PildoBox'+str(station)+year_for_filename + str(doy) + timer+'.enav'
        nav_GPSGalileo='/opt/Septentrio/RxTools/bin/sbf2rin -f '+save_location + "/" + file_to_convert+' -R3 -n N -o '+save_location+'/PildoBox'+str(station)+year_for_filename + str(doy) + timer+'.nav'

        #os.system(nav_Galileo)
        #os.system(nav_GPSGalileo)

    #Navigacios fileok eloallitasa RTK
    if mode.__eq__('1'):
        nav_Galileo_RTK='/opt/Septentrio/RxTools/bin/sbf2rin -f '+save_location+'/'+file_to_convert2+' -R3 -n E -o '+save_location+'/PildoBox'+str(station)+year_for_filename + real_day + timer+'.enav'
        nav_GPS_RTK='/opt/Septentrio/RxTools/bin/sbf2rin -f '+save_location+'/'+file_to_convert2+' -R3 -n N -o '+save_location+'/PildoBox'+str(station)+year_for_filename + real_day + timer+'.nav'
        
        #os.system(nav_Galileo_RTK)
        #os.system(nav_GPS_RTK)

    if mode.__eq__('0'):
        obs = save_location + "/" + "PildoBox" + str(station) + year_for_filename + str(doy) + timer + ".obs"
        
        nav_new=save_location+'/PildoBox'+str(station)+year_for_filename+str(doy)+timer+".nav"
        #nav_new_g=save_location+'/PildoBox'+str(station)+year_for_filename+str(doy)+timer+".enav"

           
    #sbs = save_location + "/" + "PildoBox" + str(station) + year_for_filename + str(doy) + timer + ".sbs"

    if mode.__eq__('1'):
        #obs = save_location + "/" + "PildoBox" + str(station) + year_for_filename + real_day + timer + ".obs"
        nav_new=save_location+'/PildoBox'+str(station)+year_for_filename+real_day+timer+".nav"
        #nav_new_g=save_location+'/PildoBox'+str(station)+year_for_filename+real_day+timer+".enav"

        #nav = save_location + '/BRDC00WRD_R_' + str(year) + real_day + '0000_01D_MN.rnx

    if flag==1 and mode.__eq__('0'):
        x='a'
        val = chr(ord(x) + prev_time-1)
        print('CHAR:',val)
        nav_new=save_location+'/PildoBox'+str(station)+year_for_filename+str(doy)+val+".nav"

    #/home/hegyi/Paripa/Reference_for_Kinematic/PildoBox205202210306
    if station.__eq__('205') and mode.__eq__('1'):
        rtcm_file_name='/home/hegyi/Paripa/Reference_for_Kinematic/Pildobox205'+year+real_day+ftime+'.rtcm3'
        print('\n obs_ref:'+rtcm_file_name)
        convert_rtcm="/usr/local/bin/convbin "+rtcm_file_name+" -r rtcm3 -v 3.03 -f 1 -d "+ '/home/hegyi/Paripa/Reference_for_Kinematic/'
        os.system(convert_rtcm)
        obs = save_location + "/" + "PildoBox" + str(station) + year_for_filename + real_day + timer + ".obs"
        nav_new=save_location+'/PildoBox'+str(station)+year_for_filename+real_day+timer+".nav"
        #exit()

        #nav_Galileo_RTK='sbf2rin -f '+save_location+'/'+file_to_convert2+' -R3 -n E -o '+save_location+'/PildoBox'+str(station)+year_for_filename + real_day + timer+'.enav'
        #nav_GPS_RTK='sbf2rin -f '+save_location+'/'+file_to_convert2+' -R3 -n N -o '+save_location+'/PildoBox'+str(station)+year_for_filename + real_day + timer+'.nav'
        
        
        if flag==1:
            #nav_GPS_RTK='sbf2rin -f '+save_location+'/'+file_to_convert2+' -R3 -n N -o '+save_location+'/PildoBox'+str(station)+year_for_filename + real_day + prev_time+'.nav'
            nav_new=save_location+'/PildoBox'+str(station)+year_for_filename+real_day+prev_time+".nav"
            print('Missing nav',nav_new)
                    
        os.system(convert_hourly)
        #nav_RTK='/opt/Septentrio/RxTools/bin/sbf2rin -f '+save_location+'/'+file_to_convert2+' -R3 -n N -o '+save_location+'/PildoBox'+str(station)+year_for_filename + real_day + timer+'.nav'
        #os.system(nav_RTK)
        #nav_new=save_location+'/PildoBox'+str(station)+year_for_filename + real_day + timer+'.nav'

        obs_ref=ref_data_save+'/PildoBox205'+year+real_day+ftime+".obs"
        print('\n obs_ref:'+obs_ref)
        print('NAV:'+nav_new)
        print('OBS',obs)
        
        kinematic = "/usr/local/bin/rnx2rtkp -k /home/hegyi/Paripa/Paripa1/test_config2.conf " + obs + " " + obs_ref + " " + nav_new + " -r 4082000.925 1410145.630 4678053.713 -o " +save_location +'/'+real_day+container+ '/PildoBox' +str(station) + year_for_filename + real_day + ftime + "_kinematic" + ".pos"
        kinematic_G = "/usr/local/bin/rnx2rtkp -k /home/hegyi/Paripa/Paripa1/test_config.conf " + obs + " " + obs_ref + " " + nav_new + " -r 4082000.925 1410145.630 4678053.713 -o " + save_location +'/'+real_day+container+ '/PildoBox' +str(station) + year_for_filename + real_day + ftime +"_kinematic_G" + ".pos"
        os.system(kinematic)
        os.system(kinematic_G)
        pos_file_rtk='PildoBox'+str(station)+year_for_filename+real_day+ftime+'_kinematic'
                

    station = '/PildoBox' + str(station)

    if mode.__eq__('0'):
        os.system(convert_to_Rinex)    

    path=save_location +'/'+str(doy)
    path2=save_location+'/'+real_day

    if not os.path.exists(path2):
        os.mkdir(path2)

    if not os.path.exists(path):
        os.mkdir(path)

    if mode.__eq__('0'):
        SPP = "/usr/local/bin/rnx2rtkp -k /home/hegyi/Paripa/Paripa1/rnxconfig.conf -p 0 -f 1 -f 2 -f 5 -t " + obs + " " + nav_new + " -o " + save_location +'/'+str(doy)+container+ str(station) + year_for_filename + str(doy) + timer + ".pos"
        SPPG = "/usr/local/bin/rnx2rtkp -k /home/hegyi/Paripa/Paripa1/rnxconfig_gal.conf -p 0 -f 1 -f 2 -f 5 -t " + obs + " " + nav_new + " -o " + save_location +'/'+str(doy)+container+ str(station) + year_for_filename + str(doy) + timer + "G.pos"
        os.system(SPP)
        os.system(SPPG)
        pos_file=str(station) + year_for_filename + str(doy) + timer
        pos_file=pos_file[1:]

    if mode.__eq__('0'):
        Graph_maker = "python3 /home/hegyi/Paripa/Paripa1/GraphModule.py " + pos_file+' '+str(station_number)+' '+mode
        print('pos:'+Graph_maker)
        os.system(Graph_maker)

    if mode.__eq__('1'):
        Graph_maker = "python3 /home/hegyi/Paripa/Paripa1/GraphModule.py " + pos_file_rtk+' '+str(station_number)+' '+mode
        os.system(Graph_maker)
    

    for f in os.listdir(save_location):
        if f.endswith('.lnav') or f.endswith('.hnav') or f.endswith('.obs') or f.endswith('.raw') or f.endswith('.stat') or f.endswith('.sbs') or f.endswith('_events.pos'):
            os.remove(save_location +"//" + f)

    if os.path.exists(save_location+'/'+str(doy)+container):
        for f in os.listdir(save_location+'/'+str(doy)+container):
            if f.endswith('.pos.stat') or f.endswith('_events.pos'):
                os.remove(save_location+'/'+str(doy)+container+'/'+f)
    



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
if len(ftime)<2:
    ftime='0'+ftime
print(ftime)

if mode.__eq__('1'):
    idx=int(ctime)-2
    
    i=205
    container='/PildoBox'+str(i)
    if idx%2==1:
        flag=1    
    evalFiles(i,time_stamps[idx],container,time_stamps[idx-1])

for f in os.listdir(save_location):
    if f.endswith('.rnx') or f.endswith('.gz'):
        os.remove(save_location +"//" + f)
'''
