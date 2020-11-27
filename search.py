import Stemmer
import re
import json 
import sys
import bisect
import math
import os
from collections import defaultdict
import time

DOC_COUNT = 9829059
tfidf_scores = defaultdict(lambda : [0] * 1)

# tfidf score weightage for different fields
# order should be t > i > c > b > r = l
weightage = {'t': 20, 'i': 15, 'c': 10, 'b': 5, 'r': 2, 'l': 2}

# Initialising stop words
stop_words_file = open("stop_words.txt", "r")
STOP_WORDS = set()
for line in stop_words_file:
	cur_line = line.split(" ")
	for word in cur_line:
		if word != "":
			STOP_WORDS.add(word)

# getting the first word of every index
first_words_file = open("INDEX/first_words.txt", "r")
FIRST_WORDS = first_words_file.readlines()

# Pre-processing the input query	
def tokenize(text):
	global STOP_WORDS
	tokens = re.split(r'[^A-Za-z0-9]+', text)
	stemmer = Stemmer.Stemmer('english')
	tokenized = []
	for token in tokens:
		cur_token = stemmer.stemWord(token.lower().casefold())
		if cur_token != "" and cur_token not in STOP_WORDS and token.lower() not in STOP_WORDS:
			tokenized.append(cur_token)
	return tokenized

# returns posting list for a given word
def find_posting_list(word):
	global FIRST_WORDS
	document_number = bisect.bisect_right(FIRST_WORDS, word) - 1
	with open("INDEX/index" + str(document_number) + ".txt", "r") as fp:
		for line in fp:
			line_splitted = line.split(":")
			if line_splitted[0] == word:
				return line_splitted[1]
	return ""
	
# get all field frequencies and document number for a given document
def get_doc_info(doc):
	doc_info = {'D': 0, 't': 0, 'i': 0, 'r': 0, 'c': 0, 'l': 0, 'b': 0}
	number = ""
	current = 'D'
	for char in doc:
		if char >= '0' and char <= '9':
			number = number + char
		else:
			doc_info[current] = int(number)
			number = ""
			current = char
	doc_info[current] = int(number)
	return doc_info

# update tf-idf scores of every document given individual word and field of input query
# t b i r c 
fields = ["D", "t", "i", "b", "c", "l", "r"]
def update_document_scores(word, Type):
	global weightage
	global tfidf_scores
	posting_list = find_posting_list(word)
	if posting_list == "":
		return
	field_freq = {'D': 0, 't': 0, 'c': 0, 'b': 0, 'r': 0, 'l': 0, 'i': 0}
	for character in posting_list:
		if (character >= '0' and character <= '9') or character == '\n':
			continue
		field_freq[character] += 1
	docs = posting_list.split("D")[1:]
	idf_total = {}
	for field in fields:
		if field_freq[field] != 0:
			idf_total[field] = math.log(1 + DOC_COUNT/field_freq[field])
		else:
			idf_total[field] = 0

	for doc in docs:
		doc_info = get_doc_info(doc.strip())
		doc_number = doc_info['D']
		total_freq = 100*doc_info['t'] + 20*doc_info['c'] + 20*doc_info['i'] + doc_info['b'] + 0.01*doc_info['r'] + 0.01*doc_info['l']
		tfidf_scores[doc_number] += 10000
		if Type == "":
			tf = math.log(total_freq + 1)
			idf = idf_total['D']
			tfidf_scores[doc_number] += tf*idf
		else:	
			tf = math.log(total_freq + 1)
			idf = idf_total['D']
			tfidf_scores[doc_number] += tf*idf
			if doc_info[Type] != 0:
				tfidf_scores[doc_number] += 1000
				tf = weightage[Type] * math.log(doc_info[Type] + 1)
				idf = idf_total[Type]
				tfidf_scores[doc_number] += tf*idf


# Handle each field of the input query separately
def show(words, Type):
	words = tokenize(words)
	for word in words:
		update_document_scores(word, Type)

def map_to_title(doc_id):
	doc_no = doc_id // 2000
	line_number = doc_id % 2000
	with open("INDEX/titles/titles" + str(doc_no) + ".txt", "r") as fp:
		for i in range(line_number + 1):
			line = fp.readline()
	return line.strip()
input_file = sys.argv[1]
queries = 0
output_file = open("queries_op.txt", "w+")
with open(input_file, "r") as fp:
	for line in fp:
		start_time = time.time()
		queries += 1
		split_index = line.find(',')
		if split_index == -1:
			print('Wrong input format')
			continue
		number_of_results = int(line[0:split_index])
		query = line[split_index + 1:].split(":")
		size = len(query)
		tfidf_scores = defaultdict(lambda: 0)
		for i in range(size):
			word = query[i].strip();
			if size == 1:
				show(word, "")
			elif i == 0:
				if len(word) == 1:
					continue
				else:
					word = word[:-1]
					show(word, "")
			elif i == size - 1:
				Type = query[i-1].strip()[-1:]
				show(word, Type)
			else:
				Type = query[i-1].strip()[-1:]
				word = word[:-1]
				show(word, Type)
		tfidf_scores = sorted(tfidf_scores.items(), key=lambda kv: kv[1], reverse = True)
		printed = 0
		for title in tfidf_scores:
			output_file.write((str(title[0]) + ", " + map_to_title(title[0])))
			output_file.write("\n")
			printed += 1
			if printed == number_of_results:
				break
		final_time = time.time()
		output_file.write((str(final_time - start_time) + ", " + str((final_time - start_time)/number_of_results)))
		output_file.write("\n") 
		output_file.write("\n")
output_file.close()