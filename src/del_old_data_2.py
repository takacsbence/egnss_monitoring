#!/usr/bin/env python3

"""
    delete old files in Paripa project
"""

import os
import time
from pathlib import Path
import shutil

def del_files(path, days):
    """
    delete files in path older than x days
    :param:     path
    :param:     days
    """
    for f in list(Path(path).rglob("*")):
        if os.stat(f).st_mtime < now - days * 86400:
            if os.path.isfile(f):
                os.remove(f)
            shutil.rmtree(f)

if __name__ == "__main__":
    now = time.time()
    path = "/home/tbence/Paripa/Reference_for_Kinematic"   #files from base stations
    days = 20
    del_files(path, days)
    path = "/home/tbence/HC/data"  #files from EGNSS stations
    del_files(path, days)
