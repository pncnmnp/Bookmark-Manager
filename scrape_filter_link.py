from newspaper import Article
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from string import punctuation
import requests

class Scrape_Filter():
	def __init__(self):
		self.stopwords = stopwords.words('english')
		self.lemm = WordNetLemmatizer()

	def get_bookmark_link(self, url):
		req = Article(url)
		req.download()
		soup = BeautifulSoup(req.html, 'html.parser')
		return soup, req

	def get_title(self, soup):
		if soup.title.string.find('|') != -1:
			title = soup.title.string.split('|')[0]
			return title.strip()
		else:
			return soup.title.string

	def get_keywords_and_description(self, soup):
		desc = [soup.find_all('meta', attrs={'name':'og:description'}), 
		        soup.find_all('meta', attrs={'property':'description'}), 
		        soup.find_all('meta', attrs={'name':'description'}), 
		        soup.find_all('meta', attrs={'property': 'og:description'})]
		keywords = soup.find_all('meta', attrs={'name': 'keywords'})

		desc = [content[0]['content'] for content in desc if content != list()]

		if desc == list() and keywords == list():
			return None
		else:
			return {'keywords': keywords, 'desc': desc}

	def filter_text(self, text):
		vocabulary = list()
		for punc in punctuation:
			if punc in text:
				text = text.replace(punc, ' ')

		for word in text.split():
			if word.isalpha() and word not in self.stopwords:
				vocabulary.append(self.lemm.lemmatize(word))

		return vocabulary

	def get_wikipedia(self, title):
		API_BEFORE = "https://en.wikipedia.org/w/api.php?action=opensearch&origin=*&search="
		API_AFTER = "&limit=1&namespace=0&format=json"
		req = requests.get(API_BEFORE+title+API_AFTER)
		corpus = req.json()[2][0]
		return corpus

if __name__ == '__main__':
	obj = Scrape_Filter()
	soup, req = obj.get_bookmark_link('https://gmail.com')
	req.parse()
	title = obj.get_title(soup)
	desc_keywords = obj.get_keywords_and_description(soup)
	content = obj.filter_text(req.text)

	print(title)
	print(desc_keywords)
	print(content)

	if desc_keywords == None and content == list():
		wiki = obj.get_wikipedia(title)
		print(wiki)
