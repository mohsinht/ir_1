import config
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join
import re
from nltk.stem import PorterStemmer

class Doc:
    id = 0
    value = "null"
    def __init__(self, id, value):
        self.id = id
        self.value = value


class Term:
    id = 0
    value = "null"
    docids = []
    positions = []
    totalCount = 0
    docFreq = 0
    def __init__(self, id, value):
        self.id = id
        self.value = value
        self.docids = []
        self.positions = []

    def add(self, docid, position):
        if docid not in self.docids:
            self.docFreq += 1
        self.docids.append(docid)
        self.positions.append(position)
        self.totalCount += 1


    def getStats(self):
        stats = str(self.id) + " " + str(self.totalCount) + " " + str(self.docFreq)
        i = 0
        for docId in self.docids:
            stats += " " + str(docId) + "," + str(self.positions[i])
            i += 1
        return stats


def readDocIds(docids_file):
    file_pointer = open(docids_file, "r", encoding="utf8", errors='ignore')
    file_data = file_pointer.read()
    file_lines = file_data.split('\n')
    documents = []
    for line in file_lines:
        if len(line) > 1:
            arr = line.split('\t')
            documents.append(Doc(int(arr[0]), arr[1]))
    return documents


def readTermIds(termids_file):
    file_pointer = open(termids_file, "r", encoding="utf8", errors='ignore')
    file_data = file_pointer.read()
    file_lines = file_data.split('\n')
    terms = []
    for line in file_lines:
        if len(line) > 1:
            arr = line.split('\t')
            terms.append(Term(int(arr[0]), arr[1]))
    return terms


def parseHtml(file_html):
    if file_html.find('<!DOCTYPE html') != -1:
        file_html = '<!DOCTYPE html' + file_html.split('<!DOCTYPE html', 1)[1]  # skipping all info before html starts

    file_soup = BeautifulSoup(file_html, features="html.parser")

    # kill all script and style elements
    for script in file_soup(["script", "style"]):
        script.extract()
    file_text = file_soup.get_text(separator=' ')
    lines = (line.strip() for line in file_text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    file_text = '\n'.join(chunk for chunk in chunks if chunk)
    return file_text


def tokenize(text):
    file_text = text.lower()
    return re.split("[ .,!?:;'\n\"\-—–_=^()*‘’”“%+@#»<>\t…{}→\\\\/\[\]]+", file_text)


def stopwording(tokens):
    stop_file = open(config.STOPLIST_FILE, "r")
    stop_file_data = stop_file.read()
    stop_words = re.split("[ \n]+", stop_file_data.lower())
    for stop_word in stop_words:
        while stop_word in tokens:
            tokens.remove(stop_word)
    stop_file.close()
    return tokens


def stemming(words):
    ps = PorterStemmer()
    for i in range(0, len(words)):
        words[i] = ps.stem(words[i])
    return words


def saveDocInTerm(term_value, terms_array, doc_id, doc_pos):
    # linear search to find the term id.
    for term in terms_array:
        if term_value == term.value:
            term.add(doc_id, doc_pos)


def invertedIndex():
    documents = readDocIds(config.DOCID_FILE)
    terms = readTermIds(config.TERMID_FILE)
    count = 1
    for doc in documents:
        file_pointer = open(config.CORPUS_DIR + doc.value, "r", encoding="utf8", errors='ignore')
        file_html = file_pointer.read()
        file_text = parseHtml(file_html)
        tokens = tokenize(file_text)
        tokens = stopwording(tokens)
        words = stemming(tokens)
        position_count = 1
        for word in words:
            saveDocInTerm(word, terms, doc.id, position_count)
            position_count += 1
        count += 1
        if count > 10:
            break
    for term in terms:
        if len(term.docids) > 0:
            print(term.getStats())


invertedIndex()