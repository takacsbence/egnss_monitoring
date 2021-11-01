import os
import sys
import zipfile

extract_chosen_time="D:\Rinex_datas\Extracted_zips\\"+"PildoBox20519335"+sys.argv[1]+".raw.zip"
print(extract_chosen_time)
zip_extract_path="D:\Rinex_datas\Extracted_zips"

with zipfile.ZipFile(extract_chosen_time, 'r') as zip_ref:
    zip_ref.extractall(zip_extract_path)

convert_to_Rinex="D:\Rinex_datas\\convbin -f 1 -f 2 -f 5 -r ubx -d D:\Rinex_datas\Extracted_zips D:\Rinex_datas\Extracted_zips\PildoBox20519335"+sys.argv[1]+".raw"
print("Path:",convert_to_Rinex)
os.system(convert_to_Rinex)

#convert_to_pos="D:\Rinex_datas\\rnx2rtkp config.conf -r rinex -f 1 -f 2 -f 5 D:\Rinex_datas\Extracted_zips\\"
#os.system(convert_to_pos)
