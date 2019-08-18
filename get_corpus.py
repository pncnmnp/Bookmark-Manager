from newspaper import Article
from time import sleep
import requests
import json
import os

API_BEFORE = "https://en.wikipedia.org/w/api.php?format=json&redirects=1&titles="
API_AFTER = "&action=query&prop=extracts&explaintext&origin=*&limit=1"
DIR_LOC = './corpus/'
CORPUSES = './corpus/layout.json'
TEMP_LOC = './corpus/programming_jargon_links.json'

def wiki_fetch(name):	
	req = requests.get(API_BEFORE + name + API_AFTER)
	page_id = list(req.json()['query']['pages'].keys())[0]

	corpus = {"text": req.json()['query']['pages'][page_id]['extract']}
	return corpus

def any_fetch():
	links = json.load(open(TEMP_LOC))
	vocab = str()
	DIR = './corpus/programming.json'

	for link in links:
		try:
			print(link)
			req = Article(link)
			req.download()
			req.parse()
			vocab += ' ' + req.text
			with open(DIR, 'a') as fp:
				fp.write(req.text+'\n\n')
			sleep(4)
		except:
			print("FAILED: " + link)
			sleep(10)
	vocab = {'text': vocab}

if __name__ == '__main__':
	# This automation should be started from the '/' dir of the project.
	layouts = json.load(open(CORPUSES))

	for category in list(layouts.keys()):
		if os.path.exists(DIR_LOC+category) == False:
			os.mkdir(DIR_LOC+category)

		for title in layouts[category]:
			TARGET_DIR = DIR_LOC+category+'/'+title+'.json'
			if os.path.exists(TARGET_DIR) == False:
				corpus = wiki_fetch(title)
				with open(TARGET_DIR, 'w') as fp:
					json.dump(corpus, fp)
