import wget
import sys
import os

#http://152.66.5.8/~tbence/hc/data/HC-Budapest_01-12-2019_01-12-2019.zip

#A letolto modul úgy működik hogy meg kell adni a letöltendő file nevét parancssori argumentumként pl:HC-Budapest_01-12-2019_01-12-2019.zip formaban

url = 'http://152.66.5.8/~tbence/hc/data/'
file_name=str(sys.argv[1])


download_location="D:\Rinex_datas\Downloaded_zips"
download = wget.download(url+file_name,download_location)

#Elindul a kicsomagolo modul
path='python ExtractModule.py D:\Rinex_datas\Downloaded_zips\\'+file_name
os.system(path)

