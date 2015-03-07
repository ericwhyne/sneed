#!/usr/bin/python
import GeoIP
import re

gi = GeoIP.open("/GeoIPCity.dat", GeoIP.GEOIP_STANDARD)

infilename = "/lacie/logs/vpn/memex-vpn-logins.txt"
outfilename = "/lacie/logs/vpn/memex-vpn-logins.csv"

infile = open(infilename,'r')
outfile = open(outfilename, 'w')

out = "username,ip,lon,lat,date,time,datetime\n"
for line in infile.readlines():
#  print line
  line = re.sub('\n','',line)
  data = line.split(' ')
  geodata = gi.record_by_addr(data[1])
  lon = str(geodata['longitude'])
  lat = str(geodata['latitude'])
  username = data[0]
  ip = data[1]
  date = data[2]
  time = data[3]
  datetime = date + "T" + time
  out += username + "," + ip + "," + lon + "," + lat + "," + date + "," + time + "," + datetime + "\n"
outfile.write(out)
