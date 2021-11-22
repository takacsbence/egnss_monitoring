# RTK_lib_automatizalas
This program contains 3 modules. The first one is DownloadModule, which downloads a chosen file from a webserver. The second module is RTKLibModule which converts the downloaded raw zip file to a Rinex file than it converts the Rinex file to a pos file, which will be used for position-error diagrams. The last module is GraphModule, which simply makes an E-W position error diagram, which will be saved to the chosen location on the users storage unit.

The syntax for the DownloadModule: year, day of the chosen year, id of the station, time: a=0hour and x=23hour, user_id
An example: 2021 10 205 a Lehel
This module contains a test mode which can be used the following way: Test, user_id

The syntax for the RTKLibModule: year, day of the chosen year, id of the station, time: a=0hour and x=23hour, user_id
An example: 2021 10 205 a Lehel

The syntax for the GraphModule: year, day of the chosen year, id of the station, time: a=0hour and x=23hour, user_id
An example: 2021 10 205 a Lehel

The program also contains a config file, which contains the users chosen save location for the data and the position error diagrams in .png format.
An example for the config file use:Lehel Data||D:\Rinex_datas\Downloaded_zips Pictures||D:\Rinex_datas\E-W_graphs
