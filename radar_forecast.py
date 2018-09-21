import wradlib as wrl
import numpy as np
import matplotlib.pyplot as pl
import os
import requests
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import matplotlib.dates as mdates
from matplotlib.dates import  DateFormatter
import calendar
import tarfile

# Download data
folder="/scratch/local1/m300382/temp/"

response=requests.get("https://opendata.dwd.de/weather/radar/composit/fx/FX_LATEST.tar.bz2")
with open(folder+'FX_LATEST.tar.bz2', 'wb') as f:
    f.write(response.content)

tar = tarfile.open(folder+'FX_LATEST.tar.bz2', "r:bz2")
files=tar.getnames()
tar.extractall(folder)
tar.close()
os.remove(folder+'FX_LATEST.tar.bz2')

fnames=[folder + str(file) for file in files]

# Get the localization of the cities
cities = ["Feuerbergstrasse 6, Hamburg","Bundesstrasse 53, Hamburg"]
geolocator = Nominatim()
cities_location=[geolocator.geocode(city) for city in cities]

box_average= 1

data=[]
datestring=[]

for fname in fnames:
    rxdata, rxattrs = wrl.io.read_radolan_composite(fname)
    data.append(np.ma.masked_equal(rxdata, -9999))
    minute = int(fname[fname.find("_MF002")-3:fname.find("_MF002")])
    datestring.append((rxattrs['datetime']+timedelta(minutes=minute)))
#     datestring.append((rxattrs['datetime']+timedelta(minutes=minute)).strftime("%Y-%m-%d %H:%M"))

# Convert UTC time to local time
def utc_to_local(utc_dt):
    # get integer timestamp to avoid precision lost
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= timedelta(microseconds=1)
    return local_dt.replace(microsecond=utc_dt.microsecond)

for i in range(0,np.size(datestring)):
    datestring[i]=utc_to_local(datestring[i])

# Convert to a masked array
data=np.ma.array(data)
# Get coordinates
radolan_grid_ll = wrl.georef.get_radolan_grid(900,900, wgs84=True)
lon_wgs0 = radolan_grid_ll[:,:,0]
lat_wgs0 = radolan_grid_ll[:,:,1]

data_point={}
rain_point={}
for city in cities_location:
    lon_point=city.longitude
    lat_point=city.latitude
    dist=np.sqrt((lon_wgs0-lon_point)**2+(lat_wgs0-lat_point)**2)
    indx, indy=np.unravel_index(np.argmin(dist, axis=None), dist.shape)
    data_point[city.address]=np.mean(data[:, indx-box_average:indx+box_average, indy-box_average:indy+box_average], axis=(1,2))
    rain_point[city.address]=wrl.zr.z_to_r(data_point[city.address], a=200., b=1.6)

for city in cities_location:
    fig = pl.figure(1, figsize=(15,4))
    pl.plot_date(datestring, rain_point[city.address], '-',linewidth=3)
    pl.gca().spines['right'].set_visible(False)
    pl.gca().spines['top'].set_visible(False)
    pl.gca().xaxis.grid(True, ls='dashed')
    pl.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
    pl.gca().xaxis.set_major_formatter(DateFormatter('%H:%M'))
    pl.gca().yaxis.set_major_locator(pl.MaxNLocator(5))
    pl.gca().set_title("Radar forecast for "+city.address+" | Basetime "+datestring[0].strftime("%Y%m%d %H:%M"))
    pl.gca().set_ylabel("$P$ [mm h$^{-1}$]")
    pl.gca().set_xlabel("Time")
    pl.gca().set_ylim(bottom=0, top=30)
    pl.gca().set_xlim(left=datestring[0], right=datestring[-1])
    pl.gca().fill_between(datestring, y1=0, y2=2.5, alpha=0.4, color="paleturquoise")
    pl.gca().fill_between(datestring, y1=2.5, y2=7.6, alpha=0.3, color="lightseagreen")
    pl.gca().fill_between(datestring, y1=7.6, y2=30., alpha=0.3, color="teal")
    pl.gca().annotate("Light", xy=(.9, .02), xycoords="axes fraction", alpha=0.5)
    pl.gca().annotate("Moderate", xy=(.9, .13), xycoords="axes fraction", alpha=0.5)
    pl.gca().annotate("Heavy", xy=(.9, .3), xycoords="axes fraction", alpha=0.5)
    fig.autofmt_xdate()
    # pl.savefig('forecast_radar_'+city+'_'+datestring[0].strftime("%Y%m%d%H")+'.png', dpi=100, bbox_inches='tight')
    pl.savefig('forecast_radar_'+city.address.replace(' ','').replace(',','_')+'_latest.png', dpi=100, bbox_inches='tight')
    pl.clf()

for fname in fnames:
    os.remove(fname)
