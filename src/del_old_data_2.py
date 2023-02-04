#!/usr/bin/env python3

"""
    delete old files in Hungarian EGNSS monitoring project
    TODO: delete files from HC/data
"""

import os, time, shutil
from pathlib import Path

def del_files(path, days):
    """
    delete files in path older than x days
    :param:     path
    :param:     days
    """
    for f in list(Path(path).rglob("*")):
        if os.stat(f).st_mtime < now - days * 86400:
            #if os.path.isfile(f):
                #os.remove(f)
            shutil.rmtree(f)

def del_files2(path, days):
    """
    delete files in path older than x days
    :param:     path
    :param:     days
    """
    now = time.time()

    #for f in os.listdir(path):
    for f in list(Path(path).rglob("*")):
        full_path = os.path.join(path, f)
        if os.stat(full_path).st_mtime < now - days * 86400:
            #print(f)
            if os.path.isfile(full_path):
                try:
                    os.remove(full_path)
                except:
                    print("Could not remove file:", full_path)
            else:
                try:
                    shutil.rmtree(full_path)
                    #print(full_path)
                except:
                    print("Could not remove directory:", full_path)

if __name__ == "__main__":

    days = 20
    #files from base stations
    path = "/home/tbence/Paripa/Reference_for_Kinematic"
    del_files2(path, days)

    #files from EGNSS stations
    path = "/home/tbence/HC/data"
    del_files2(path, days)

