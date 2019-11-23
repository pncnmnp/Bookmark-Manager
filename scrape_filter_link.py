from newspaper import fulltext, Article
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from string import punctuation
import requests

import scrapy
from scrapy.crawler import CrawlerProcess

fetched = dict()

def start_scrapy(urls):
	process = CrawlerProcess(settings={
		'FEED_FORMAT': 'json',
		'FEED_URI': 'items.json'
	})

	process.crawl(Fetch, kwargs={"url": urls})
	process.start()

class Fetch(scrapy.Spider):
	def __init__(self, **kwargs):
		self.url = kwargs["kwargs"]["url"]

	def start_requests(self):
		urls = self.url

		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		page = response.text
		fetched[response.url] = page

class LangError(Exception):
	pass

class Scrape_Filter():
	def __init__(self):
		self.stopwords = stopwords.words('english')
		self.lemm = WordNetLemmatizer()

	def check_lang(self, soup):
		try:
			lang = soup.find('html', attrs={'lang': True})['lang']
			if 'en' in lang or "mul" in lang:
				return None
			else:
				raise LangError("Language not english!")
		except:
			return None		

	def get_bookmark_link(self, url):
		# req = Article(url)
		# req.download()
		if isinstance(url, list) == False:
			url = [url]
		start_scrapy(url)
		req = list(fetched.values())[0]
		soup = BeautifulSoup(req, 'html.parser')
		self.check_lang(soup)
		# req.parse()
		text = fulltext(req)
		return soup, text

	def get_title(self, soup):
		if soup.title != None and soup.title.string.find('|') != -1:
			title = soup.title.string.split('|')[0]
			return title.strip()
		elif soup.title != None:
			return soup.title.string
		else:
			return str()

	def get_keywords_and_description(self, soup):
		desc = [soup.find_all('meta', attrs={'name':'og:description'}), 
		        soup.find_all('meta', attrs={'property':'description'}), 
		        soup.find_all('meta', attrs={'name':'description'}), 
		        soup.find_all('meta', attrs={'property': 'og:description'})]
		keywords = soup.find_all('meta', attrs={'name': 'keywords'})

		try:
			desc = [content[0]['content'] for content in desc if content != list()]
			keywords = keywords[0]['content']
		except:
			pass

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
		corpus = str()
		try:
			corpus = req.json()[2][0]
		except:
			pass
		return corpus

def fetch_bookmarks(urls):
	obj = Scrape_Filter()

	bookmark_data = dict()
	start_scrapy(urls)

	for url in fetched:
		req = fetched[url]
		soup = BeautifulSoup(req, 'html5lib')
		obj.check_lang(soup)

		try:
			text = fulltext(req)
		except:
			article = Article(url)
			article.download()
			article.parse()
			text = article.text
		title = obj.get_title(soup)
		desc_keywords = obj.get_keywords_and_description(soup)
		content = obj.filter_text(text)

		bookmark_data[url] = dict()
		bookmark_data[url]["title"] = title
		bookmark_data[url]["desc"] = desc_keywords
		bookmark_data[url]["content"] = content

	return bookmark_data

if __name__ == '__main__':
	obj = Scrape_Filter()
	soup, req_text = obj.get_bookmark_link('https://cashkaro.com')
	title = obj.get_title(soup)
	desc_keywords = obj.get_keywords_and_description(soup)
	content = obj.filter_text(req_text)

	print(title)
	print(desc_keywords)
	print(content)

	if desc_keywords == None and content == list():
		wiki = obj.get_wikipedia(title)
		print(wiki)
