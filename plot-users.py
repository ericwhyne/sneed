#!/usr/bin/python
# -*- coding: utf-8 -*-
import GeoIP
import re
from collections import defaultdict

datadir= "/home/eric/workspace/sneed-data/"

gi = GeoIP.open(datadir + "GeoIPCity.dat", GeoIP.GEOIP_STANDARD)

iname = "XData"
map_title = iname + " VPN Connections"
infilename = datadir + "xdata-vpn-logins.txt"
outfilename = datadir + "sneed.html"

infile = open(infilename,'r')
outfile = open(outfilename, 'w')

map_head = """
<!DOCTYPE html>
<html>
<head>
  <title>Sneed Map</title>
  <meta charset="utf-8" />

  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <link rel="stylesheet" href="http://cdn.leafletjs.com/leaflet-0.7.3/leaflet.css" />
</head>
<body>
<h1> %s </h1>
  <div id="map" style="width: 1300px; height: 900px"></div>

  <script src="http://cdn.leafletjs.com/leaflet-0.7.3/leaflet.js"></script>
  <script>

    var map = L.map('map').setView([38, -98], 4);

    L.tileLayer('https://{s}.tiles.mapbox.com/v3/{id}/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
        'Imagery © <a href="http://mapbox.com">Mapbox</a>',
      id: 'examples.map-i875mjb7'
    }).addTo(map);
""" % map_title
map_body = ''
map_foot = """
</script>
</body>
</html>
"""
markers = []
paths = defaultdict(list)
locations = defaultdict(dict)
locationmeta = defaultdict(dict)
users = defaultdict(list)

for line in infile.readlines():
#  print line
  line = re.sub('\n','',line)
  data = line.split(' ')
  lon,lat,country,region,city = ['','','','','']
  try:
    geodata = gi.record_by_addr(data[1])
    lon = str(geodata['longitude'])
    lat = str(geodata['latitude'])
    country = str(geodata['country_name'])
    region = str(geodata['region_name'])
    city = str(geodata['city'])
  except:
    print "Unable to locate ip " + data[1]
    lon = "NA"
  username = data[0]
  ip = data[1]
  date = data[2]
  time = data[3]
  datetime = date + "T" + time
  # collect potential path data
  path_string = datetime + "," + lat + "," + lon
  paths[username].append(path_string)
  # collect data for each location

  if lon != "NA":
    locations[lat+','+lon][username] = "<a href='" + iname + "-" + username + ".html'>" + username + "</a><br>"
    locationmeta[lat+','+lon] = "IP: " + ip + "<br>City: " + city + "<br>Region: " + region + "<br>Country: " + country + "<br>lat,lon: " + lat + "," + lon + "<br><br>"
    users[username].append({'country':country, 'region':region, 'city':city, 'lat':lat, 'lon': lon, 'ip':ip, 'datetime':datetime, 'date':date, 'time':time})

for location in locations.keys():
  popup_string = locationmeta[location]
  for username in locations[location].keys():
    popup_string += locations[location][username]
  #print popup_string
  marker_string = 'L.marker(['+location+']).addTo(map).bindPopup("'+popup_string+'");'
  markers.append(marker_string)

for username in users.keys():
  csvout = 'datetime, date, time, country, region, city, lat, lon, ip\n'

  for connection in users[username]:
      csvout += connection['datetime'] + ',' + connection['date'] + ',' + connection['time'] + ',' + connection['country'] + ',' + connection['region'] \
      + ',' + connection['city'] + ',' + connection['lat'] + ',' + connection['lon'] + ',' + connection['ip'] + '\n'
      #print connection
print "-----------"
print csvout

for marker in sorted(markers): #sorting makes debugging easier, can be removed for production
  map_body += marker + '\n'

polylines = []
for key in paths.keys():
  #print key
  path_steps = []
  lastloc = ''
  for path_string in sorted(paths[key]): # because of the way the strings are built, these will now be in time-order
    #print "  " + path_string
    path_data = path_string.split(',')
    loc = '[' + str(path_data[1]) + ',' + str(path_data[2]) + ']'
    if loc != lastloc:
      path_steps.append(loc)
    lastloc = loc
  path_steps_string = '['
  for loc in path_steps:
    path_steps_string += loc + ','
  path_steps_string = path_steps_string[:-1] + ']'
  if len(path_steps) > 1:
    polylines.append('L.polyline('+path_steps_string+', {color: \'red\'}).addTo(map);')
    # L.polyline([[43.65,-79.36],[45.01,-93.15]], {color: 'red'}).addTo(map);
for polyline in polylines:
  map_body += polyline + '\n'

outfile.write(map_head + map_body + map_foot)
