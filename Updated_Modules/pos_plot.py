from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import sys

#check number of args
if len(sys.argv) != 2:
    print("arguments: posfile")
    print("an example: data/PildoBox20521010a.pos")
    exit()

#pos file name as first argument
pos = str(sys.argv[1])

#read data from RTKpost output
data_gps = pd.read_csv(pos, sep='\s+', header=None,  skiprows=[15])
data_gps.columns = ["date", "time", "lat", "lon", "ele", "mode", "nsat", "stdn", "stde", "stdu", "stdne", "stdeu", "stdun", "age", "ratio",]
print(len(data_gps['stdu']))

#format date and time
data_gps['datetime'] = pd.to_datetime(data_gps['date'] + ' ' + data_gps['time'], format='%Y/%m/%d %H:%M:%S.%f')

#plot data, just for demonstration
fig, ax = plt.subplots()
ax.plot(data_gps['datetime'], data_gps['nsat'])

#format plot
ax.set_ylim([0, 12])
ax.set_xlim([min(data_gps['datetime']).round('60min').to_pydatetime(), max(data_gps['datetime']).round('60min').to_pydatetime()]) #show exactly one hour session
ax.set_xlabel('time (hh:mm)')
ax.set_ylabel('# of satellites')
ax.xaxis.set_major_formatter(DateFormatter("%H:%M"))
ax.grid()
ax.text(max(data_gps['datetime']), 12.25, pos, ha='right') #add pos file name as annotation text

#plt.show()
plt.savefig('proba.png')
