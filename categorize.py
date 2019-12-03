from scrape_filter_link import Scrape_Filter, LangError, fetch_bookmarks
from get_corpus import DIR_LOC, CORPUSES
from glob import glob
from string import punctuation
from math import log10
import json
from random import shuffle
from time import time
from collections import Counter
import os

class Categorize():
	def __init__(self):
		self.scrape = Scrape_Filter()
		self.layout = json.load(open(CORPUSES))
		self.bookmark_data = dict()

	def load_bookmarks_data(self, bookmark_data):
		self.bookmark_data = bookmark_data

	def get_vocabulary(self, link):
		desc_keywords = self.bookmark_data[link]["desc"]
		title = self.bookmark_data[link]["title"]
		content = self.bookmark_data[link]["desc"]
		wiki, keywords, desc = str(), str(), list()

		if desc_keywords == None and content == list() and title != str():
			wiki = self.scrape.get_wikipedia(title)
		else:
			try:
				keywords = desc_keywords['keywords'][0]
			except:
				pass
			try:
				desc = desc_keywords['desc']
			except:
				pass

		return {
			'title': title,
			'keywords': keywords,
			'wiki': wiki,
			'desc': desc,
			'content': content
		}

	def convert_vocabulary(self, vocab):
		bookmark_vocab = str()
		bookmark_vocab += ' ' + vocab['title']
		bookmark_vocab += ' ' + vocab['keywords']
		bookmark_vocab += ' ' + vocab['wiki']

		for content in vocab['desc']:
			bookmark_vocab += ' ' + content
		# Commenting the below tow lines will drastically increase the speed
		# for content in vocab['content']:
		# 	bookmark_vocab += ' ' + content

		for punct in punctuation:
			if punct in bookmark_vocab:
				bookmark_vocab.replace(punct, ' ')

		return bookmark_vocab

	def get_corpus_vocab(self, directory):
		json_files = glob(directory + '*.json')
		vocab = str()

		for file in json_files:
			vocab += ' ' + json.load(open(file))['text']

		for punct in punctuation:
			if punct in vocab:
				vocab.replace(punct, ' ')

		return vocab.lower(), len(json_files)

	def get_entire_corpus_vocab(self):
		corpus_dir = glob(DIR_LOC + '*/')
		vocab = str()

		for directory in corpus_dir:
			corpus_vocab, len_corpus = self.get_corpus_vocab(directory)
			vocab += ' ' + corpus_vocab
		return vocab

	def get_non_corpus_vocab(self, directory):
		corpus_dir = glob(DIR_LOC + '*/')
		corpus_dir = [folder for folder in corpus_dir 
		                        if folder.find(directory) == -1]
		vocab = str()

		for directory in corpus_dir:
			corpus_vocab, len_corpus = self.get_corpus_vocab(directory)
			vocab += ' ' + corpus_vocab

		for punct in punctuation:
			if punct in vocab:
				vocab.replace(punct, ' ')

		return vocab

	def naive_bayes(self, bookmark_vocab):
		bookmark_vocab = bookmark_vocab.lower().split(' ')
		corpus_dir = glob(DIR_LOC + '*/')
		total_len_corpus = len(glob(DIR_LOC + '*/*.json'))

		entire_corpus = self.get_entire_corpus_vocab()
		vocab_entire_corpus = len(set(entire_corpus.split(' ')))

		target_dir = str()
		target_dir_score, target_dir_delta = -100000000000, 100000000000

		for corpus in corpus_dir:
			corpus_vocab, len_corpus = self.get_corpus_vocab(corpus)
			corpus_non_vocab = self.get_non_corpus_vocab(corpus)
			p_vj = len_corpus/total_len_corpus

			corpus_is = log10(p_vj)
			corpus_is_not = log10(1 - p_vj)

			for word in bookmark_vocab:
				word_match = corpus_vocab.count(word)
				words_corpus = len(corpus_vocab.split(' '))
				p_is = log10((word_match + 1)/(words_corpus + vocab_entire_corpus))

				non_word_match = corpus_non_vocab.count(word)
				non_words_corpus = len(corpus_non_vocab.split(' '))
				p_is_not = log10((non_word_match + 1)/(non_words_corpus + vocab_entire_corpus))

				corpus_is += p_is
				corpus_is_not += p_is_not
				delta = abs(corpus_is_not - corpus_is)

			if corpus_is > corpus_is_not or delta < 10:
				if ((corpus_is > target_dir_score) or 
				    (delta < target_dir_delta and 
				        abs(target_dir_score - corpus_is) <= 1)):
					target_dir = corpus
					target_dir_score = corpus_is
					target_dir_delta = delta

		return target_dir, target_dir_score

	def naive_bayes2(self, bookmark_vocab):
		bookmark_vocab = [w for w in bookmark_vocab.lower().split(" ") if len(w) > 1]
		corpus_dir = glob(DIR_LOC + "*/")
		total_len_corpus = len(glob(DIR_LOC + "*/*.json"))

		entire_corpus = self.get_entire_corpus_vocab()
		vocab_entire_corpus = len(set(entire_corpus.split(" ")))

		target_dir = str()
		target_dir_score, target_dir_delta = -100000000000, 100000000000

		for corpus in corpus_dir:

			cache_path = os.path.join(corpus, "cache.json.ext")
			if os.path.exists(cache_path):
				with open(cache_path, "r") as f:
					data = json.load(f)
				frequency_corpus_vocab=data["frequency_corpus_vocab"]
				frequency_corpus_non_vocab=data["frequency_corpus_non_vocab"]
				words_corpus=data["words_corpus"]
				non_words_corpus=data["non_words_corpus"]
				corpus_is=data["corpus_is"]
				corpus_is_not=data["corpus_is_not"]

			else:
				corpus_vocab, len_corpus = self.get_corpus_vocab(corpus)
				corpus_non_vocab = self.get_non_corpus_vocab(corpus)
				p_vj = len_corpus / total_len_corpus

				corpus_is = log10(p_vj)
				corpus_is_not = log10(1 - p_vj)
				corpus_vocab = [w for w in corpus_vocab.split() if len(w) > 1]
				corpus_non_vocab = [w for w in corpus_non_vocab.split() if len(w) > 1]

				frequency_corpus_vocab = Counter(corpus_vocab)
				frequency_corpus_non_vocab = Counter(corpus_non_vocab)

				words_corpus = len(corpus_vocab)
				non_words_corpus = len(corpus_non_vocab)

				data = {
					"frequency_corpus_vocab": frequency_corpus_vocab,
					"frequency_corpus_non_vocab": frequency_corpus_non_vocab,
					"words_corpus": words_corpus,
					"non_words_corpus": non_words_corpus,
					"corpus_is": corpus_is,
					"corpus_is_not": corpus_is_not,
				}
				with open(cache_path, "w") as f:
					json.dump(data, f,indent=2)

			for word in bookmark_vocab:
				word_match = frequency_corpus_vocab.get(word, 0)
				p_is = log10((word_match + 1) / (words_corpus + vocab_entire_corpus))

				non_word_match = frequency_corpus_non_vocab.get(word, 0)
				p_is_not = log10(
					(non_word_match + 1) / (non_words_corpus + vocab_entire_corpus)
				)

				corpus_is += p_is
				corpus_is_not += p_is_not
				delta = abs(corpus_is_not - corpus_is)

			if corpus_is > corpus_is_not or delta < 10:
				if (corpus_is > target_dir_score) or (
					delta < target_dir_delta and abs(target_dir_score - corpus_is) <= 1
				):
					target_dir = corpus
					target_dir_score = corpus_is
					target_dir_delta = delta

		return target_dir, target_dir_score

if __name__ == '__main__':
	obj = Categorize()
	links = json.load(open('links.json'))
	# links = ["https://old.reddit.com/"]
	result = {}

	BOOKMARKS_DATA = fetch_bookmarks(links)
	obj.load_bookmarks_data(BOOKMARKS_DATA)
	# shuffle(links)

	for link in links[:10]:
		try:
			vocab = obj.get_vocabulary(link)
			bookmark_vocab = obj.convert_vocabulary(vocab)
			category = obj.naive_bayes2(bookmark_vocab)
			print(link + ' : ' + category[0])
			result[link] = category[0]
		except LangError:
			print(link + ' : ' + "Failed, Language not english!")
		except Exception as err:
			print(link + ' : ' + "Failed")
			print(err)

	with open('result.json', 'w') as fp:
		json.dump(result, fp)
