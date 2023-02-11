#!/usr/bin/env python3

"""
    get rtcm messages from an ntrip caster using RTKLIB str2str
    parameters come from a json file. Json file name is the 1st argument
"""
import sys
import subprocess
import json

if __name__ == "__main__":
    #check number of arguments
    if len(sys.argv) != 2:
        print('wrong number of arguments')
        print('use', sys.argv[0], 'json file')
        exit()

    #first argument is a json file
    JNAME = sys.argv[1]
    with open(JNAME) as jfile:
        JDATA = json.load(jfile)
        USERNAME = JDATA["username"]
        PWD = JDATA["pwd"]
        SERVER = JDATA["server"]
        PORT = JDATA["port"]
        OUT_DIR = JDATA["out_dir"]
        MOUNTPOINT = JDATA["mountpoint"]
        REC_POS = JDATA.get("rec_pos")
        REF_STA_NAME = JDATA["ref_sta_name"]

    #folder of output file
    FOLDER = OUT_DIR + REF_STA_NAME + '/'
    #extension of output file
    EXT = '.rtcm'

    #use rtklib str2str to get data in RTCM as an ntrip client
    try:
        if REC_POS:
            LAT, LON, ELE = REC_POS.split()
            cmd = ["str2str", "-in", "ntrip://" + USERNAME + ":" + PWD + "@" +
                            SERVER + ":" + PORT + "/" + MOUNTPOINT, "-p", LAT, LON, ELE,
                            "-n", "1000",
                            "-out", FOLDER + REF_STA_NAME + '%y%n%h' + EXT + '::S=1']
            #print(cmd)
            subprocess.run(["str2str", "-in", "ntrip://" + USERNAME + ":" + PWD + "@" +
                            SERVER + ":" + PORT + "/" + MOUNTPOINT, "-p", LAT, LON, ELE,
                            "-n", "1000",
                            "-out", FOLDER + REF_STA_NAME + '%y%n%h' + EXT + '::S=1'])
        else:
            subprocess.run(["str2str", "-in", "ntrip://" + USERNAME + ":" + PWD + "@" +
                            SERVER + ":" + PORT + "/" + MOUNTPOINT,
                            "-out", FOLDER + REF_STA_NAME + '%y%n%h' + EXT + '::S=1'])

    except subprocess.TimeoutExpired:
        print("TimeOutError")
        exit()

#how to kill str2str
#pkill str2str
#or
#ps -aux | grep str2str -->PID
#kill -9 PID
