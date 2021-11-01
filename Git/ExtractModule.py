import os
import sys
import zipfile

zip_path=sys.argv[1]
print("EM:",zip_path)
zip_extract_path = "D:\Rinex_datas\Extracted_zips"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(zip_extract_path)


path_to_call_RTK=""
os.system()