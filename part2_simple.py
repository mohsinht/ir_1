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
    positons = []
    totalCount = 0
    def __init__(self, id, value):
        self.id = id
        self.value = value
    def add(self, docid, position):
        self.docids.append(docid)
        self.positons.append(position)
        self.totalCount += 1


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


def invertedIndex():
    documents = readDocIds(config.DOCID_FILE)
    terms = readTermIds(config.TERMID_FILE)


invertedIndex()