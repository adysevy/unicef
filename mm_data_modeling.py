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
    s_sans_punct = ""
    for letter in s:
        # this discards all non-ascii characters and replaces with a space
        if letter not in string.ascii_letters:
            s_sans_punct += ' '
        # removes all punctuation in the string above, saved as var punctuation
        elif letter in punctuation:
            s_sans_punct += ' '
        #all left over characters are letters, so we keep them as-is.
        else letter not in punctuation:
            s_sans_punct += letter
    return s_sans_punct

dates = []
file_names = []
countries = []
regions = []
stories = []
titles = []
links = []
# countries_simple is added for the stripped country names. We preserve
#countries, above, as they are entered in documents, for the display text
countries_simple = []

regions_codes = {'GENERAL':'General',\
                 'CEE/CIS':'Central and Eastern Europe and the Commonwealth of Independent States',\
                 'EAP':'East Asia and Pacific',\
                 'EAPR':'East Asia and Pacific',\
                 'ESA':'Eastern and Southern Africa',\
                 'LAC':'Latin America and the Caribbean',\
                 'MENA':'Middle East and North Africa',\
                 'ROSA':'South Asia',\
                 'WCA':'West and Central Africa',\
                 'SA':'South Asia'}

folder = 'OPSCEN Brief 2014/'

special_files = ['UNICEF OPSCEN Brief – 29 December 2014.docx',
    'UNICEF OPSCEN Brief – 30 December 2014.docx',
    'UNICEF OPSCEN Brief – 31 December 2014.docx']

flag_country = False
flag_title = False
flag_story = False
curr_story = ''
            
''' 
# FYI: I moved the code from a try-except statement to a try-except-else statement
# to fit with best practices. In try-except, you really just want the code that
# might thrown an exception in the try part. All of the code you want to execute
# if try is successful goes into the else statement. This prevents accidental
# triggering of the except clause because of some other warning, error or simply
# an if-else statement within code to be executed.
'''
for file_name in os.listdir(folder):
    try:
        f = open(folder+file_name)
        document = Document(f)

    except:
        print "Could not process file: " + file_name

    else:
        for p in document.paragraphs:
            
            if p.text == '' or 'Disclaimer:' in p.text or 'The Brief is produced' in p.text:
                    continue

            if p.text in regions_codes:
                curr_region = regions_codes[p.text]
                flag_country = True
                continue
                
            if 'http' in p.text:
                regions.append(curr_region)
                countries.append(curr_country)
                titles.append(curr_title)
                stories.append(curr_story)
                file_names.append(file_name)
                if file_name == 'UNICEF OPSCEN Brief – 29 December 2014.docx':
                    date = datetime(year=2014, month=12, day=29)
                elif file_name == 'UNICEF OPSCEN Brief – 30 December 2014.docx': 
                    date = datetime(year=2014, month=12, day=30)
                elif file_name == 'UNICEF OPSCEN Brief – 31 December 2014.docx':
                    date = datetime(year=2014, month=12, day=31)
                else:
                    date = document.core_properties.modified

                dates.append(date)
                links.append(p.text)

                formattedcountry = remove_punctuation(curr_country).strip().lower()
                countries_simple.append(formattedcountry)

                flag_country = True
                flag_title = False
                curr_story = ''
                continue
                
            if flag_country:
                if len(p.text.split())< 4:
                    curr_country = p.text
                    flag_country = False
                    flag_title = True
                    continue
                else:
                    flag_country = False
                    flag_title = True

            if flag_title:
                curr_title = p.text
                flag_title = False
                flag_story = True
                continue
                
            if flag_story:
                curr_story = curr_story + p.text
                continue

    f.close()

df = pd.DataFrame({'region':regions, 'country':countries, 'title': titles, 
                    'story':stories,\
                    'link': links,\
                    'file_name':file_names,\
                    'date':dates,
                    'country_simple': countries_simple})

# stripping all leading and trailing spaces from the country display field
df['country'] = df['country'].apply(lambda x: x.strip())

# debugging: checking the size of the dataframe
print df.shape

# creating a list of the unique country names from our files
uniqueCountryList = df.country_simple.unique()
# initializing lists to hold the lat and lng for country centroids
lat = []
lng = []

# looping through the list of unique countries, running them through
# google's geolocation API to get the lat and lng of the country's
# centroid point. This lets Google do the hard work of sorting out
# countries that are misspelled or which go by several spellings
# (i.e. DRC, DR Congo, Democratic Republic of Congo)
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
df.to_csv('OPSCENoutput.csv', encoding = 'utf-8')

