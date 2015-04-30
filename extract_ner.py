from ner import extract_entities
import pandas as pd

# use this if your computer cannot find java
# os.environ['JAVAHOME'] = 'C:/Program Files/Java/jdk1.8.0/bin/java.exe'

# reading the data
df = pd.DataFrame.from_csv("data/news_stories.csv")

f_entities = open('data/entities.txt','w')
for ind,story in zip(df.index,df.story):
    entities = extract_entities(story)
    for s,t in entities:
        f_entities.write(str(ind) + ',\"' + s + '\",' + t + '\n')

f_entities.close()