# -*- coding: utf-8 -*-
# google maps geocoding API documentation: 
# https://developers.google.com/maps/documentation/geocoding/#Geocoding

import os
import sys
import pandas as pd
import json
from urllib2 import Request, urlopen, URLError, quote
import time

baseurl = "http://maps.googleapis.com/maps/api/geocode/json?address="

def address_locator(locationName):
    locationName = quote(locationName)
    request = Request(baseurl+locationName)
    try: 
        response= urlopen(request)
        locationdata = json.load(response)
    except URLError, e:
        print e
        # print locationdata
        time.sleep(0.2)
        return {u'lat': 0.0, u'lng': 0.0}
    else:
        if locationdata['status']!='OK':
            print locationdata['status']
            return {u'lat': 0.0, u'lng': 0.0}
        else:
            # 
            centroid = locationdata['results'][0]['geometry']['location']
        # print response
            time.sleep(0.2)
            return centroid

