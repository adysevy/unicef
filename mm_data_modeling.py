# -*- coding: utf-8 -*-
import os
from docx import Document
from datetime import datetime
import pandas as pd

punctuation = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
def remove_punctuation(s):
    s_sans_punct = ""
    for letter in s:
        if letter not in punctuation:
            s_sans_punct += letter
    return s_sans_punct

centroids = pd.read_csv('countrycentroidsmm.csv', usecols=['Country_name', 
    'UNc_latitude', 'UNc_longitude'], index_col='ISO3166A2')
# centroidcountrynames = []
# for country in centroids['Country_name']:
#     country.strip().lower()
#     remove_punctuation(country)
#     centroidcountrynames.append(country)

#stripping the country names in my centroid file of punctuation, 
#leading/trailing spaces, and converting to all lower-case.
centroids['Country_name'].apply(lambda x: remove_punctuation(x))
centroids['Country_name'].apply(lambda x: x.strip())
centroids['Country_name'].apply(lambda x: x.lower())

dates = []
file_names = []
countries = []
regions = []
stories = []
titles = []
links = []
lat = []
lng = []

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
# folder = 'test/'

special_files = ['UNICEF OPSCEN Brief – 29 December 2014.docx','UNICEF OPSCEN Brief – 30 December 2014.docx','UNICEF OPSCEN Brief – 31 December 2014.docx']

flag_country = False
flag_title = False
flag_story = False
curr_story = ''
            
for file_name in os.listdir(folder):
    try:
        f = open(folder+file_name)
        document = Document(f)
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


    except:
        print "Could not process file: " + file_name

    f.close()

print len(regions)
print len(stories)
print len(countries)
print len(titles)
print len(links)
print len(dates)

formattedcountries = []

for country in countries:
    country.strip()
    remove_punctuation(country)
    country.lower()
    formattedcountries.append(country)

df = pd.DataFrame({'region':regions, 'country':formattedcountries, 'title': titles , 'story':stories,\
                   'link': links,\
                   'file_name':file_names,\
                   'date':dates})

df.link.unique()

    #!!!! There's a lot of data cleaning to do in there -- some of the country names include 
    # line breaks or tabs included in the name. We also have issues with more than one country being
    # in a title (See: DR Congo/Rwanda) -- this will be challenging to sort out which country to assign to. 
    # Several countries are referenced with slightly different names -- Laos == Lao DPR, DR Congo == DRC, 
    # State of Palestine/Israel == Israel/State of Palestine (these are also trouble because arguably (controversially) 
    # different countries), DPRK == DPR Korea ("North Korea" isn't the accepted UN term for the country), etc.
df.country.unique()

df.region.unique()

df.to_csv('OPSCENoutput.csv', encoding = 'utf-8')


print df.head()
