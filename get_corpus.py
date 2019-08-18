import requests
import json
import os

API_BEFORE = "https://en.wikipedia.org/w/api.php?format=json&redirects=1&titles="
API_AFTER = "&action=query&prop=extracts&explaintext&origin=*&limit=1"
DIR_LOC = './corpus/'
CORPUSES = './corpus/layout.json'

def fetch(name):	
	req = requests.get(API_BEFORE + name + API_AFTER)
	page_id = list(req.json()['query']['pages'].keys())[0]

	corpus = {"text": req.json()['query']['pages'][page_id]['extract']}
	return corpus

if __name__ == '__main__':
	# This automation should be started from the '/' dir of the project.
	layouts = json.load(open(CORPUSES))

	for category in list(layouts.keys()):
		if os.path.exists(DIR_LOC+category) == False:
			os.mkdir(DIR_LOC+category)

		for title in layouts[category]:
			TARGET_DIR = DIR_LOC+category+'/'+title+'.json'
			if os.path.exists(TARGET_DIR) == False:
				corpus = fetch(title)
				with open(TARGET_DIR, 'w') as fp:
					json.dump(corpus, fp)
