from scrape_filter_link import Scrape_Filter
from get_corpus import DIR_LOC, CORPUSES
from glob import glob
from string import punctuation
from math import log10
import json

class Categorize():
	def __init__(self):
		self.scrape = Scrape_Filter()
		self.layout = json.load(open(CORPUSES))

	def get_vocabulary(self, link):
		soup, req_text = self.scrape.get_bookmark_link(link)

		desc_keywords = self.scrape.get_keywords_and_description(soup)
		title = self.scrape.get_title(soup)
		content = self.scrape.filter_text(req_text)
		wiki, keywords, desc = str(), str(), list()

		if desc_keywords == None and content == list():
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
		return vocab

	def naive_bayes(self, bookmark_vocab):
		bookmark_vocab = bookmark_vocab.lower().split(' ')
		corpus_dir = glob(DIR_LOC + '*/')
		total_len_corpus = len(glob(DIR_LOC + '*/*.json'))

		entire_corpus = self.get_entire_corpus_vocab()
		vocab_entire_corpus = len(set(entire_corpus.split(' ')))

		target_dir = str()
		target_dir_score = -100000000000

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
				if corpus_is > target_dir_score:
					target_dir = corpus
					target_dir_score = corpus_is

			print(target_dir, corpus_is, corpus_is_not)

		return target_dir, target_dir_score

if __name__ == '__main__':
	obj = Categorize()
	vocab = obj.get_vocabulary('https://facebook.com')
	bookmark_vocab = obj.convert_vocabulary(vocab)
	category = obj.naive_bayes(bookmark_vocab)
	print("\nCATEGORY: \n")
	print(category)
