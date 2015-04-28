
# coding: utf-8
import os
from docx import Document
from datetime import datetime
import pandas as pd
import json
import string
# importing my googleAddressLocator.py script as a module
import googleAddressLocator as goog
from nltk import word_tokenize
import re
from nltk.stem.porter import PorterStemmer

############ global variables ###############
data = {'date':[], 'country':[], 'region':[], 'story':[], 'title': [], 'link':[], 'file_name':[]}
flags = {'country':False,'story':False,'title':False,'link':False}
currs = {'region':'','country':'', 'title': '', 'story':'', 'link': ''}

regions_codes = {'GENERAL':'General',
                 'CEE/CIS':'Central and Eastern Europe and the Commonwealth of Independent States',
                 'CEE/ CIS':'Central and Eastern Europe and the Commonwealth of Independent States', 
                 'EAP':'East Asia and Pacific',
                 'EAPR':'East Asia and Pacific',
                 'ESA':'Eastern and Southern Africa',
                 'LAC':'Latin America and the Caribbean',
                 'MENA':'Middle East and North Africa',
                 'ROSA':'South Asia',
                 'WCA':'West and Central Africa',
                 'WCAR':'West and Central Africa',
                 'SA':'South Asia',
                 'GENERAL':'General'}

unique_countries = set()
c = open('data/countries.txt','rb')
for line in c:
    unique_countries.add(line.strip())

stop_at = set(['UNICEF Operations Centre','Disclaimer:','The Brief is produced'])
############################################

############ methods ###############
def get_bad_chars(df):
    s = set()
    for title in df.title.values:
        for c in title:
            try:
                c.decode('utf8')
            except:
                s.add(c)
    for story in df.story.values:
        for c in story:
            try:
                c.decode('utf8')
            except:
                s.add(c)
    return s

def norm_text(text, s):
    return ''.join([c for c in text if c not in s])

def get_date(doc, file_name):
    if file_name == 'UNICEF OPSCEN Brief – 29 December 2014.docx':
        date = datetime(year=2014, month=12, day=29)
    elif file_name == 'UNICEF OPSCEN Brief – 30 December 2014.docx': 
        date = datetime(year=2014, month=12, day=30)
    elif file_name == 'UNICEF OPSCEN Brief – 31 December 2014.docx':
        date = datetime(year=2014, month=12, day=31)
    else:
        date = doc.core_properties.modified
    return date

def read_lines(file_name, document, element): 
    global data
    global currs
    global flags
    global unique_countries
    global regions_codes
    global stop_at

    if sum([stop in element for stop in stop_at]) > 0:
        return 

    if len(element)< 3:
        return 

    if element in regions_codes:
        currs['region'] = regions_codes[element]
        flags['country'] = True
        return 

    if flags['link'] and 'http' in element:
        data['region'].append(currs['region'])
        data['country'].append(currs['country'])
        data['title'].append(currs['title'])
        data['story'].append(currs['story'])
        data['file_name'].append(file_name)
        data['link'].append(element)
        data['date'].append(get_date(document, file_name))
        flags['country'] = True
        flags['title'] = False
        flags['link'] = False
        currs['story'] = ''
        return

    if flags['country']:
        if element in unique_countries:
            currs['country'] = element
            flags['country'] = False
            flags['title'] = True
            return 
        else:
            flags['country'] = False
            flags['title'] = True

    if flags['title']:
        currs['title'] = element
        flags['title'] = False
        flags['story'] = True
        return 

    if flags['story']:
        currs['story'] = element
        flags['link'] = True
        return
    
    return 

def remove_punctuation(s):
    s=str(s)
    t = ''.join(l for l in s if l in string.ascii_letters or l == ' ')
    return t

def check_token(token):
    return len(token)>1 and not re.search('[^a-z]',token)


############################################

# reading the data
folder = 'OPSCEN Brief 2014/'
for file_name in os.listdir(folder):
    try:
        f = open(folder+file_name,'rb')
        document = Document(f)
        for p in document.paragraphs:
            a = p.text.split('\n')
            if len(a)> 1:
                for element in a:
                    read_lines(file_name, document, element.strip())
            else:
                read_lines(file_name, document, p.text.strip())

    except Exception as e:
        print str(e) + "file name: "+ file_name
    f.close()

# bulding the data frame
df = pd.DataFrame(data)
df['story_id']=df.index

# removing 5 stories with multiple urls
ind = []
for i,s in enumerate(df.story.values):
    if 'http' in s:
        ind.append(i)
df = df.drop(df.index[[ind]])
print "removed "+ str(len(ind)) + " records"

ind = []
for i,s in enumerate(df.title.values):
    if 'http' in s:
        ind.append(i)
df = df.drop(df.index[[ind]])
print "removed "+ str(len(ind)) + " records"

# remove non utf chars
s = get_bad_chars(df)
df.title = df.title.apply(lambda x: norm_text(x,s))
df.story = df.story.apply(lambda x: norm_text(x,s))

print 'DATAFRAME STEP 1:'
print len(df)

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

df = pd.merge(df, centroids, how='left', on='country_simple', left_index=False)

regions = ['Across Regions', 'LAC', 'CEE', 'WCAR', 'ESA',  'MENA', 'EAP', 'EAPR', 'ROSA', 'Across SA']

regional_lat = 19.5
regional_lng = -136.4
for region in regions:
    df['lat'][(df['country'].str.contains(region))] = regional_lat
    df['lng'][(df['country'].str.contains(region))] = regional_lng
    regional_lat = regional_lat - 7.5

print 'DATAFRAME STEP 2:'
print len(df)

cats = pd.read_csv('data/news_stories_plus_LDA.csv', usecols=['row_index','link', 'title', '250topics_NER'], index_col=['row_index'])

newsLDA = pd.merge(df, cats)

newsLDA = newsLDA.drop_duplicates(['link', 'title'])

print 'STEP 3'
print len(newsLDA)
print newsLDA.head()
print newsLDA.columns

newsLDA[str(250)+'_topic']=""
for index, row in newsLDA.iterrows():
    try:
        maxes  = max(eval(newsLDA[str(250)+'topics_NER'][index]), key = lambda x: x[1])
        newsLDA[str(250)+'_topic'][index] = maxes[0]

    except:
        continue

tops = pd.read_csv('LDATopics.csv')
df = pd.merge(newsLDA, tops, left_on= '250_topic', right_on = 'Topic')
df = df.drop('250_topic', axis = 1)

word_dic = {'famine': 'food insecurity', 'food': 'food insecurity', 'harvest': 'food insecurity', 'hunger': 'food insecurity', 'drown': 'disaster', 'cyclone': 'disaster', 'tsunami': 'disaster', 'climate': 'disaster', 'flood': 'disaster', 'hurricane': 'disaster', 'storm': 'disaster', 'rain': 'disaster', 'wind': 'disaster', 'weather': 'disaster', 'typhoon': 'disaster', 'tornado': 'disaster', 'earthquake': 'disaster', 'MERS': 'disease', 'polio': 'disease', 'vaccine': 'disease', 'respiratory': 'disease', 'ebola': 'disease', 'disease': 'disease', 'dengue': 'disease', 'fever': 'disease', 'virus': 'disease', 'chikunguny': 'disease', 'Boko': 'conflict', 'diarrhea': 'disease', 'diarrhoea': 'disease', 'drought': 'water insecurity', 'water': 'water insecurity', 'refugee': 'population displacement', 'evacuate': 'population displacement', 'displace': 'population displacement', 'exodus': 'population displacement', 'flee': 'population displacement', 'HIV': 'disease', 'WHO': 'disease', 'health': 'disease','epidemic': 'disease', 'hospital': 'disease', 'health': 'disease', 'cholera': 'disease'}

df['category2']=''
df['category3']=''
df['category4']=''
stemmer = PorterStemmer()
for index, row in df.iterrows():
    topics = []
    texts = [stemmer.stem(word) for word in word_tokenize(df.title[index]) if check_token(word)]
    for word in texts:
        if word in word_dic:
            topics.append(word_dic[word])
    for i, topic in enumerate(topics):
        i = i+2
        df['category'+str(i)][index]=topic

df['category'][(df['category'] == 'conflict') & (df['category2'] == 'disease')] = 'Political/social unrest'

print 'STEP 4'
print len(df)

df['week/year']=''
df['week/year']=df['date'].map(lambda x:str('{week}/{year}'.format(week=x.weekofyear,year=x.year)))

df.to_csv('WebApp/data/news_stories_final.csv', index_label='row_index', index=True, date_format='%m/%d/%y')

