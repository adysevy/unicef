import csv
import sys
import re

f = open('WebApp/data/entities.txt')
reader = csv.reader(f)
reader.next()

acronyms = set()
all_ents = set()
non_norms = set()
headers = ['story_id','entity','type']

with open('normalized_entities.txt', 'wb') as outfile:
    outfile.write(','.join(headers) + '\n')
    for row in reader:
        temp = row
        word = row[1]
        non_norms.add(word)
        # print re.findall(r'(?<!\.\s)\b[A-Z][a-z]*\b', word)
        acros = re.findall(r'[A-Z]{2,}', word)
        if acros != []:
            acronyms.add(acros[0].title())
        word = word.lower().strip() 
        word = word.replace('.', '')
        word = word.replace('\s+', ' ')
        word = word.title()
        word = word.replace('Al-', 'al-')
        
        splits = word.split()
        phrase = []
        for el in splits:
            if el in acronyms:
                phrase.append(el.upper())
            else:
                phrase.append(el)
        word = ' '.join(el for el in phrase)

        all_ents.add(word)
        temp[1] = word
        outfile.write(','.join(temp) + '\n')
        




