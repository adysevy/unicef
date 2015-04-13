
# coding: utf-8
import os
from docx import Document
from datetime import datetime
import pandas as pd

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

# removing 5 stories with multiple urls
ind = []
for i,s in enumerate(df.story.values):
    if 'http' in s:
        ind.append(i)
df = df.drop(df.index[[ind]])

# remove non utf chars
s = get_bad_chars(df)
df.title = df.title.apply(lambda x: norm_text(x,s))
df.story = df.story.apply(lambda x: norm_text(x,s))

# saving the data to a csv
df.to_csv("data/news_stories.csv", encoding="utf8")

