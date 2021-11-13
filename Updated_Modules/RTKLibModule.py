import os
import sys

#http://152.66.5.8/~tbence/hc/data/Y2021/D010/PildoBox205/PildoBox20521010a.raw.zip
#Egy példa az RTKLibModule használatához: RTKLibModule.py 2021 010 205 a Lehel

chosen_year=str(sys.argv[1])
chosen_day=str(sys.argv[2])
chosen_location=str(sys.argv[3])
file_name=str(sys.argv[4])
user_id=str(sys.argv[5])

year_for_filename=chosen_year[2:]

temp=""
f = open('config.txt', 'r')
for line in f:
        if(line.split(' ')[0]==sys.argv[5]):
            temp=line.split(' ')[1]


save_location=temp[:-1]

file_to_convert="PildoBox"+chosen_location+year_for_filename+chosen_day+file_name+".raw"

#sbf legyen az input tipus
#convert_to_Rinex="convbin -f 1 -f 2 -f 5 -r sbf -d D:\Rinex_datas\Extracted_zips D:\Rinex_datas\Extracted_zips\PildoBox20519335"+sys.argv[1]+".raw"
#convert_to_Rinex="convbin -f 1 -f 2 -f 5 -r sbf -d "+save_location+" "+file_to_convert
#print("Command:",convert_to_Rinex)
#os.system(convert_to_Rinex)

#Rnx2rtkp hívás, ez működik ha megkapja a megfelelő inputot lefut és létrehozza a pos filet es elmenti abba a mappaba ami a configban van megadva
#fp="rnx2rtkp -p 0 -f 1 -f 2 -f 5 -t -e D:\Rinex_datas\HC-Budapest_15-10-2021_15-10-2021.o D:\Rinex_datas\HC-Budapest_15-10-2021_15-10-2021.n -o D:\Rinex_datas\HC-Budapest_15-10-2021_15-10-2021.pos"
obs=save_location+"\\"+"PildoBox"+chosen_location+year_for_filename+chosen_day+file_name+".o"

nav=save_location+"\\"+"PildoBox"+chosen_location+year_for_filename+chosen_day+file_name+".n"

sbs=save_location+"\\"+"PildoBox"+chosen_location+year_for_filename+chosen_day+file_name+".sbs"

fp="rnx2rtkp -p 0 -f 1 -f 2 -f 5 -t -e "+obs+" "+nav+" "+sbs+" "+save_location

os.system(fp)

