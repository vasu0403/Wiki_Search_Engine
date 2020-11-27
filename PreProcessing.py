import re 
import Stemmer
index = {}
stop_words_file = open("stop_words.txt", "r")
STOP_WORDS = set()
for line in stop_words_file:
	cur_line = line.split(" ")
	for word in cur_line:
		if word != "":
			STOP_WORDS.add(word)
current_token = 0
def tokenize(text, Type):
	global STOP_WORDS
	global current_token
	tokens = re.split(r'[^A-Za-z0-9]+', text)
	length = len(tokens)
	current_token += length
	stemmer = Stemmer.Stemmer('english')
	if Type == 1:
		if length > 0 and tokens[0] == 'redirect':
			return
		if length > 1 and tokens[1] == 'redirect':
			return
	for token in tokens:
		cur_token = stemmer.stemWord(token.lower().casefold())
		if cur_token != "" and cur_token not in STOP_WORDS and token.lower() not in STOP_WORDS:
			if cur_token not in index:
				index[cur_token] = [0, 0, 0, 0, 0, 0]
			index[cur_token][Type] += 1
def findInbox(text):
	infobox = re.findall("\{\{Infobox (.*?)\}\}[\r\n]", text, flags=re.DOTALL)		# gives the infobox
	text = re.sub("\{\{Infobox (.*?)\}\}[\r\n]", "", text, flags=re.DOTALL)
	for box in infobox:
		tokenize(box, 2)
	return text

def findReferences(text):
	references = re.findall("<ref[^/]*?>(.*?)</ref>", text, flags=re.DOTALL)		# gives all the references
	text = re.sub("<ref[^/]*?>(.*?)</ref>", "", text, flags=re.DOTALL)
	for reference in references:
		tokenize(reference, 3)
	return text

def findCategories(text):
	categories = re.findall("\[\[Category:(.*?)\]\]", text, flags=re.DOTALL)		# gives all the categories
	text = re.sub("\[\[Category:(.*?)\]\]", "", text, flags=re.DOTALL)
	for categorie in categories:
		tokenize(categorie, 4)
	return text

def findExternalLinks(text):				
	possible = ["==External Links==", "== External Links==", "==External Links ==", "== External Links ==", "==External links==", "== External links==", "==External links ==", "== External links =="]
	for pos in possible:
		new_text = text.split(pos);
		if len(new_text) > 1:
			links = new_text[1].split("\n")
			for line in links:
				if line and line[0] == '*':
					tokenize(line, 5)
			return new_text[0]
	return text

def Pre_Process(title, body):
	global index
	global current_token
	current_token = 0
	index = {}
	body = findInbox(body)
	body = findReferences(body)
	body = findCategories(body)
	body = findExternalLinks(body)
	tokenize(body, 1)
	tokenize(title, 0)
	return index, current_token