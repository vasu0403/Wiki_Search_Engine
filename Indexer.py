import xml.sax
from PreProcessing import *
import json
import sys
import os
docID = 0
Index = {}
total_tokens = 0
THRESHOLD =20000
SIZE_OF_INDEX = 10000
entry = 0
def flush(index_number, titles):
	global Index
	global entry
	if not os.path.exists("INDEX"):
		os.mkdir("INDEX")
	title_file = open("INDEX/titles" + str(entry) + ".txt", "w+")
	with open("INDEX/index" + str(index_number) + ".txt", "w+") as fp:
		for key in sorted(Index.keys()):
			fp.write(key)
			fp.write(":")
			fp.write(Index[key])
			fp.write("\n")
	for title in titles:
		title_file.write(title)
		title_file.write("\n")
	title_file.close()
	entry += 1	
def merge_files(total_files):
	while total_files > 1:
		i = 0
		print(total_files)
		while(i < total_files):
			print("merging: " + str(i) + " " + str(i + 1))
			if not os.path.isfile("INDEX/index" + str(i + 1) + ".txt"):
				f = open("INDEX/index" + str(i + 1) + ".txt", "w+")
				f.close()
			f1 = open("INDEX/index" + str(i) + ".txt", "r")
			f2 = open("INDEX/index" + str(i + 1) + ".txt", "r")
			f3 = open("INDEX/temp.txt", "w+")
			lines1 = f1.readline()
			lines2 = f2.readline()
			while lines1 and lines2:
				if lines1 == "\n":
					lines1 = f1.readline()
					continue
				if lines2 == "\n":
					lines2 = f2.readline()
					continue
				cur_line1 = lines1.split("\n")[0].split(":")
				cur_line2 = lines2.split("\n")[0].split(":")
				word1 = cur_line1[0].strip()
				word2 = cur_line2[0].strip()
				if word1 == word2:
					f3.write(word1 + ":" + cur_line1[1].strip() + cur_line2[1].strip())
					f3.write("\n")
					lines1 = f1.readline()
					lines2 = f2.readline()
				elif word1 < word2:
					f3.write(lines1)
					lines1 = f1.readline()
				else:
					f3.write(lines2)
					lines2 = f2.readline()
			while lines1:
				if lines1 == "\n":
					lines1 = f1.readline()
					continue
				f3.write(lines1)
				lines1 = f1.readline()
			while lines2:
				if lines2 == "\n":
					lines2 = f2.readline()
					continue
				lines2 = f2.readline()
			f1.close()
			f2.close()
			f3.close()
			os.remove("INDEX/index" + str(i) + ".txt")
			os.remove("INDEX/index" + str(i + 1) + ".txt")
			os.rename("INDEX/temp.txt", "INDEX/index" + str(i//2) + ".txt")
			i += 2
		if total_files % 2 == 1:
			total_files //= 2
			total_files += 1
		else:
			total_files //= 2

def split_into_files():
	print("SPLITTING")
	f1 = open("INDEX/complete_index.txt", "r")
	f2 = open("INDEX/first_words.txt", "w+")
	in_memory = 0
	lines = []
	first_word = True
	index_num = 0
	for line in f1:
		lines.append(line)
		in_memory += 1
		if first_word:
			word = line.split(":")[0]
			first_word = False
		if in_memory % SIZE_OF_INDEX == 0:
			print("index " + str(index_num))
			new_file = open("INDEX/index" + str(index_num) + ".txt", "w+")
			for cur_line in lines:
				new_file.write(cur_line)
			new_file.close()
			index_num += 1
			f2.write(word)
			f2.write("\n")
			lines = []
			in_memory = 0
			first_word = True
	if in_memory > 0:
		print("index " + str(index_num))
		f2.write(word)
		f2.write("\n")
		new_file = open("INDEX/index" + str(index_num) + ".txt", "w+")
		for cur_line in lines:
			new_file.write(cur_line)
		new_file.close()
		lines = []
		in_memory = 0
		first_word = True
		index_num += 1
	f1.close()
	f2.close()
def add_to_index(ID, title, body):
	global total_tokens
	current_index, add = Pre_Process(title, body)
	total_tokens += add
	text_type = ["t", "b", "i", "r", "c", "l"]
	for word in current_index:
		to_add = "D" + str(ID)
		cur_list = current_index[word]
		for i in range(6):
			if cur_list[i] != 0:
				to_add += text_type[i] + str(cur_list[i])
		if word not in Index:
			Index[word] = ""
		Index[word] += to_add
class Handler(xml.sax.ContentHandler):
	def __init__(self):
		self.tagType = ""
		self.title = ""
		self.body = ""
		self.content = ""	
		self.documentID = 0
		self.index_number = 0
		self.documents_in_memory = 0
		self.titles = []
	def startElement(self, tag, attributes):
		global docID
		tag = tag.strip()
		self.tagType = tag
		if tag == "page":
			self.documentID = docID
			docID += 1
	def characters(self, content):
		self.content += content
	def endElement(self, tag):
		print("\033[0;0H")
		print(docID)
		global Index
		if self.tagType == "title":
			self.title = self.content.strip()
			self.titles.append(self.title)
		elif self.tagType == "text":
			if self.documents_in_memory == THRESHOLD:
				flush(self.index_number, self.titles)
				self.titles = []
				self.index_number += 1
				Index = {}
				self.documents_in_memory = 0
			self.body = self.content
			add_to_index(self.documentID, self.title, self.body)
			self.documents_in_memory += 1
		elif tag == "mediawiki":
			flush(self.index_number, self.titles)
			self.titles = []
			self.index_number += 1
			Index = {}
			self.documents_in_memory = 0
		self.content = ""

if __name__ == '__main__':
	parser = xml.sax.make_parser()
	handler = Handler()
	parser.setContentHandler(handler)
	for filename in os.listdir("Adump"):
		parser.parse("Adump/" + str(filename))
	merge_files(handler.index_number)
	os.rename("INDEX/index0.txt", "INDEX/complete_index.txt")
	split_into_files()