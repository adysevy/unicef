from ner import extract_entities
import pandas as pd

# use this if your computer cannot find java
# os.environ['JAVAHOME'] = 'C:/Program Files/Java/jdk1.8.0/bin/java.exe'

# reading the data
df = pd.DataFrame.from_csv("../WebApp/data/news_stories_final.csv")

f_entities = open('data/entities.txt','w')
f_entities.write('story_id,entity,type')
for ind,story in zip(df.story_id,df.story):
    entities = extract_entities(story)
    for s,t in entities:
        f_entities.write(str(ind) + ',\"' + s + '\",' + t + '\n')

f_entities.close()