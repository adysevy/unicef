# Visualizing Crisis News Briefs

The goal of this project was to take texts containing summaries of important news events around the world (”Crisis News Briefs”) and extract meaningful data to reveal spatial, temporal and categorical trends. Working with our client, UNICEF, we found that it was important to show broad trends while still making the most granular parts of the data accessible for users. Natural language processing tools, including Latent Dirichlet Allocation (LDA), Name Entity Recognition (NER), text parsing tools and k-means clustering were used to process the raw textual data provided by the client. Briefs are sent out on a daily basis, which provided reliable date information for temporal trends. Geospatial data was extracted from the texts and mapped on the country level, unless documents specified the news stories as regional or global in scope.

### Link to working demo 
`http://adysevy.github.io/unicef/WebApp/`

### Link to video demo
`https://vimeo.com/127950984`
	
### Run visualization localy
1. Clone the repository
2. Navigate to unicef/WebApp
3. Run a local Web server `python -m SimpleHTTPServer 8888 &`

### Data Pre Proccessing
Running the preprocessing scripts are not necessary for running the app, but for reproducibility purposes, we outlined the stages below.
The data preproccessing is comprised out of several Python scripts that should be ran from the "Preproccessing" folder:
1. Parsing the data, assigning categories and getting geo location: create_map_categories_df.py
2. Extracting entities: extract_ner.py
3. Normalizing entities: normalize_entities.py

In order to run those scripts, some environment configurations are required:

#### Downloding Packages
```
	easy_install python-docx
	sudo pip install -U nltk
	easy_install -U gensim
```

#### Configure Packages
1. Python_docx: edit file according to: https://github.com/python-openxml/python-docx/issues/85
2. NLTK: Download NTLK stuff:
```	
	import nltk
	nltk.download() #download stop words from Corpora and punkt from Models
```
