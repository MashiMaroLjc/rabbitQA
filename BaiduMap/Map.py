#coding:utf8

import urllib.request, urllib.error, urllib.parse
import json

mode = 'transit'
origin = '清华大学'
destination = '天安门'
origin_region  = ''
destination_region = ''
output = ''


url = "http://api.map.baidu.com/direction/v1?mode="+mode\
      +"&origin="+origin\
      +"&destination="+destination\
      +"&origin_region="+origin_region\
      +"&destination_region="+destination_region\
      +"&output="+output\
      +"&ak=GuGZ01jekpjxCa1IGQCDNv608jm48wDt"

req = urllib.request.Request(url)
res = urllib.request.urlopen(req)

print(res.read())
