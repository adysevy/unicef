# -*- coding: utf-8 -*-
import os
from docx import Document
from datetime import datetime
import pandas as pd
import json
import string
# importing my googleAddressLocator.py script as a module
import googleAddressLocator as goog

def remove_punctuation(s):
    s=str(s)
    t = ''.join(l for l in s if l in string.ascii_letters or l == ' ')
    return t

df = pd.read_csv('data/news_stories.csv', index_col=[0])

# countries_simple is added for the stripped country names. We preserve
#countries, above, as they are entered in documents, for the display text
countries_simple = []

for curr_country in df['country'].values:
    formattedcountry = remove_punctuation(curr_country).strip().lower()
    if formattedcountry == 'car':
        formattedcountry = 'central african republic'
    if 'across' in formattedcountry:
        formattedcountry = ''
    if 'palestine' in formattedcountry:
        formattedcountry = 'israel'
    if 'dpr' in formattedcountry:
        formattedcountry = 'north korea'
    if formattedcountry == 'georgia':
        formattedcountry = 'republic of georgia'
    countries_simple.append(formattedcountry)

#adding the simplified country names to the dataframe for merging with 
#centroid file created below.
df['country_simple'] = countries_simple
df['story_title'] = df['title']
df['story_link'] = df['link']

# creating a list of the unique country names from our files
uniqueCountryList = df.country_simple.unique()
# initializing lists to hold the lat and lng for country centroids
lat = []
lng = []

# looping through the list of unique countries, running them through
# google's geolocation API to get the lat and lng of the country's
# centroid point. This lets Google do the hard work of sorting out
# countries that are misspelled or which go by several spellings
# (i.e. DRC, DR Congo, Democratic Republic of Congo). 
for i in uniqueCountryList:
    googleGeolocation = goog.address_locator(i)
    lat.append(googleGeolocation['lat'])
    lng.append(googleGeolocation['lng'])

# creating a dataframe with just the unique country names and their centroids
centroids = pd.DataFrame(data={'country_simple': uniqueCountryList,
    'lat': lat, 'lng': lng})

# saving that list to a csv
centroids.to_csv('countryLatLngs.csv')

# adding country centroids to our main dataframe, by joining on the
# simplified country name field.
df = pd.merge(df, centroids, how='left', on='country_simple', 
    left_index=False)

# finally, saving all our hard work to csv
df.to_csv('data/news_stories_with_lat_long.csv', encoding = 'utf-8', index_label='row_index')