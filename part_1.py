import config
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join
import re
from nltk.stem import PorterStemmer

def parseHtml(file_html):
    file_html = '<!DOCTYPE html' + file_html.split('<!DOCTYPE html', 1)[1]  # skipping all info before html starts

    file_soup = BeautifulSoup(file_html)
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
    return re.split("[ .,!?:;'\n\"\-—()\[\]]+", file_text)

def stopwording(tokens):
    stop_file = open(config.STOPLIST_FILE, "r")
    stop_file_data = stop_file.read()
    stop_words = re.split("[ \n]+", stop_file_data.lower())
    for stop_word in stop_words:
        if stop_word in tokens:
            tokens.remove(stop_word)
    stop_file.close()
    return tokens

def stemming(words):
    ps = PorterStemmer()
    for i in range(0, len(words)):
        words[i] = ps.stem(words[i])
    words = list(dict.fromkeys(words)) #remove duplicates
    return words

def createDocIDs(file_names):
    id = 1
    docids_file = open(config.DOCID_FILE, "w+")
    docids_mapping = ""
    for file_name in file_names:
        docids_mapping = docids_mapping + str(id) + "\t" + file_name + "\n"
        id = id + 1

    docids_file.write(docids_mapping)

def appendTermId(term, id):
    docids_file = open(config.TERMID_FILE, "a")
    docids_file.write(str(id) + '\t' + term + '\n')

def saveAllTokens(words):
    id = 1
    for word in words:
        appendTermId(word, id)
        id = id+1

def processFiles(dir):
    #read file names
    file_names = [file for file in listdir(dir) if isfile(join(dir, file))]
    print("Total Files: " + str(len(file_names)))
    createDocIDs(file_names)
    for file_name in file_names:
        file_pointer = open(config.CORPUS_DIR + file_name, "r")
        file_html = file_pointer.read()
        parseHtml(file_html)
        file_text = parseHtml(file_html)
        tokens = tokenize(file_text)
        tokens = list(dict.fromkeys(tokens))
        tokens = stopwording(tokens)
        words = stemming(tokens)
        saveAllTokens(words)
        file_pointer.close()
        break

print("getting files from " + config.CORPUS_DIR)
processFiles(config.CORPUS_DIR)

