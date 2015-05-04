# Visualizing Crisis News Briefs

## Link to working demo 
`http://adysevy.github.io/unicef/WebApp/`
	
## Run visualization localy:
1. Clone the repository
2. Navigate to unicef/WebApp
3. Run a local Web server `python -m SimpleHTTPServer 8888 &`

In order to run the pre processing part, these configurations are required:

## Downloding Packages
	easy_install python-docx
	
	sudo pip install -U nltk
	
	easy_install -U gensim

## Configure Packages
1. Python_docx: edit file according to: https://github.com/python-openxml/python-docx/issues/85
2. NLTK: Download NTLK stuff:
```	
	import nltk
	nltk.download() #download stop words from Corpora and punkt from Models
```
