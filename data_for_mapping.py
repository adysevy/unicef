# -*- coding: utf-8 -*-
import os
from docx import Document
from datetime import datetime
import pandas as pd
import json
import string
# importing my googleAddressLocator.py script as a module
import googleAddressLocator as goog

punctuation = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
def remove_punctuation(s):
    s = str(s)
    # s_sans_punct = ""
    # for letter in s:
    #     # this discards all non-ascii characters and replaces with a space
    #     if letter not in string.ascii_letters:
    #         s_sans_punct += ' '
    #     # removes all punctuation in the string above, saved as var punctuation
    #     elif letter in punctuation:
    #         s_sans_punct += ' '
    #     #all left over characters are letters, so we keep them as-is.
    #     else:# letter not in punctuation:
    #         s_sans_punct += letter
    # return s_sans_punct
    t = ''.join(l for l in s if l not in string.digits and l not in string.punctuation)
    return t

df = pd.read_csv('data/news_stories.csv', index_col=[0])

# countries_simple is added for the stripped country names. We preserve
#countries, above, as they are entered in documents, for the display text
countries_simple = []

for curr_country in df['country'].values:
    formattedcountry = remove_punctuation(curr_country).strip().lower()
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