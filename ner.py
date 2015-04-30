import os
from nltk.tag.stanford import NERTagger
from nltk.tokenize.stanford import StanfordTokenizer
import nltk

# use this if your computer cannot find java
# os.environ['JAVAHOME'] = 'C:/Program Files/Java/jdk1.8.0/bin/java.exe'

#download the model files from http://nlp.stanford.edu/software/tagger.shtml#Download
tokenizer = StanfordTokenizer('NER/stanford-postagger.jar') 

#download the model files from http://nlp.stanford.edu/software/CRF-NER.shtml#Download
ner_tagger = NERTagger('NER/english.all.3class.distsim.crf.ser.gz',
               'NER/stanford-ner.jar') 

#download with nltk.download() 
sent_tokenizer = nltk.data.load('NER/english.pickle')


def extract_phrases(tagged_words):
    tagged_phrases = []
    i=0
    while i<len(tagged_words):
        w,t=tagged_words[i]
        if t<>'O':
            phrase=w
            j=i+1
            while j<len(tagged_words) and tagged_words[j][1]==t:
                phrase+=' ' + tagged_words[j][0]
                j+=1
            i=j
            tagged_phrases.append((phrase,t))
        else:   
            i+=1
    return tagged_phrases

def extract_entities(text):
    entities = []
    for sent in sent_tokenizer.tokenize(text):
        tagged_words = ner_tagger.tag(sent.encode('utf8').split())
        entities += extract_phrases(tagged_words)
    
    return set(entities)



