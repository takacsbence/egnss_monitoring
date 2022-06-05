#!/usr/bin/env python3

"""

"""
import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

dbase_name = "hegyi"

#data base connection
con = psycopg2.connect("dbname=" + dbase_name)

#query from psql database
sql_query = pd.read_sql("SELECT * FROM rtk_stats WHERE station_id = 205 AND mode = 'kinematic' AND navi_sys = 'GPS'", con)

#Convert SQL to DataFrame
df_gps = pd.DataFrame(sql_query, columns = ['id', 'station_id', 'datetime', 'nr_of_epochs', 'mode', 'navi_sys', 'nr_of_float'])
#df['datetime'] = pd.to_datetime(df['datetime'], format='%Y-%m-%d %H:%M:%S.%f')

#query from psql database
sql_query = pd.read_sql("SELECT * FROM rtk_stats WHERE station_id = 205 AND mode = 'kinematic' AND navi_sys = 'GPS GALILEO'", con)

#Convert SQL to DataFrame
df_gps_gal = pd.DataFrame(sql_query, columns = ['id', 'station_id', 'datetime', 'nr_of_epochs', 'mode', 'navi_sys', 'nr_of_float'])


#close data base connection
con.close()

fig, ax = plt.subplots()

#plot
ax.plot(df_gps['datetime'], df_gps['nr_of_float'], label='GPS')
ax.plot(df_gps_gal['datetime'], df_gps_gal['nr_of_float'], label='GPS GAL')
ax.xaxis.set_major_formatter(DateFormatter("%m-%d"))
ax.grid()
ax.set_ylim([0, 100])

plt.savefig('gps_gal.png', dpi=100)

