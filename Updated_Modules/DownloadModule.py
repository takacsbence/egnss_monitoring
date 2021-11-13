import wget
import sys
import zipfile

#http://152.66.5.8/~tbence/hc/data/Y2021/D010/PildoBox205/PildoBox20521010a.raw.zip


#Egy példa a letöltő modul használatára:DownloadModule.py 2021 D010 205 a Lehel
url = 'http://152.66.5.8/~tbence/hc/data/Y2021/'

if len(sys.argv)==1:
    print("A helyes paraméterezés a következő: Kiválasztott nap pl: 10, 115 | PildoBox2xx | a kiválasztott óra pl: a=0 óra és így haladva 24 óráig | Személyes configurációhoz azonosító")
    exit()

chosen_year=str(sys.argv[1])
chosen_day=str(sys.argv[2])
chosen_location=str(sys.argv[3])
file_name=str(sys.argv[4])
user_id=str(sys.argv[5])

temp=sys.argv[2]
cut=temp[1:]

chosen_location="PildoBox"+chosen_location

save_location=""
temp=""

f = open('config.txt', 'r')
for line in f:
        if(line.split(' ')[0]==sys.argv[5]):
            temp=line.split(' ')[1]


save_location=temp[:-1]
year_for_filename=chosen_year[2:]
chosen_year='Y'+chosen_year


full_url=url+chosen_day+'/'+chosen_location+'/'+chosen_location+year_for_filename+cut+file_name+".raw.zip"
download = wget.download(full_url,save_location)


zip_path=save_location+'\\'+chosen_location+year_for_filename+cut+file_name+".raw.zip"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(save_location)

