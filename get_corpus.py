import requests

API_BEFORE = "https://en.wikipedia.org/w/api.php?format=json&redirects=1&titles="
API_AFTER = "&action=query&prop=extracts&explaintext&origin=*&limit=1"

def fetch(name):	
	req = requests.get(API_BEFORE + name + API_AFTER)
	page_id = list(req.json()['query']['pages'].keys())[0]

	corpus = req.json()['query']['pages'][page_id]['extract']
	return corpus

if __name__ == '__main__':
	fetch('sports')
