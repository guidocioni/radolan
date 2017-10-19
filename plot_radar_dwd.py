# coding: utf-8
from mpl_toolkits.basemap import Basemap
import wradlib as wrl
import numpy as np
import matplotlib.pyplot as pl
import os
import netCDF4
import requests

#Download latest RX scan
response=requests.get("https://opendata.dwd.de/weather/radar/composit/rx/raa01-rx_10000-latest-dwd---bin")
with open('raa01-rx_10000-latest-dwd---bin', 'wb') as f:
    f.write(response.content)

rx_filename = "raa01-rx_10000-latest-dwd---bin"

rxdata, rxattrs = wrl.io.read_RADOLAN_composite(rx_filename)
rxdata = np.ma.masked_equal(rxdata, -9999) / 2 - 32.5

# Get coordinates

radolan_grid_ll = wrl.georef.get_radolan_grid(900,900, wgs84=True)

lon_wgs0 = radolan_grid_ll[:,:,0]
lat_wgs0 = radolan_grid_ll[:,:,1]

datestring=rxattrs['datetime'].strftime("%Y-%m-%d %H:%M")

# plot RX product
# fig = pl.figure()

bmap = Basemap(projection='cyl', llcrnrlon=4, llcrnrlat=47, urcrnrlon=16, urcrnrlat=55,  resolution='i')

bmap.contourf(lon_wgs0,lat_wgs0,rxdata,np.arange(-1,60,0.5),cmap='nipy_spectral',extend="both")

# Draw the coastlines, countries, parallels and meridians
bmap.drawcoastlines(linewidth=0.5, linestyle='solid', color='white')
bmap.drawcountries(linewidth=0.5, linestyle='solid', color='white')
bmap.drawparallels(np.arange(-90.0, 90.0, 1), linewidth=0.1, color='white', labels=[True, False, False, True])
bmap.drawmeridians(np.arange(0.0, 360.0, 1), linewidth=0.1, color='white', labels=[True, False, False, True])
bmap.readshapefile('/Users/guidocioni/shapefiles/DEU_adm_shp/DEU_adm1','DEU_adm1',linewidth=0.3,color='white')

# Insert the legend
bmap.colorbar(location='right', label='Reflectivity [dBz]')

pl.title('RX Product single scan\n' + datestring)

# pl.grid(color='r')
pl.show()
#pl.savefig('radar'+rxattrs['datetime'].strftime("%Y%m%d%H%M")+'.png', dpi=150)

