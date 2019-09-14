import config
from bs4 import BeautifulSoup
import re
from nltk.stem import PorterStemmer


def readDocIds(docids_file):
    file_pointer = open(docids_file, "r", encoding="utf8", errors='ignore')
    file_data = file_pointer.read()
    file_lines = file_data.split('\n')
    documents = dict()
    for line in file_lines:
        if len(line) > 1:
            arr = line.split('\t')
            documents[arr[1]] = int(arr[0]) # <DOC_NAME, DOC_ID>
    return documents


def readTermIds(termids_file):
    file_pointer = open(termids_file, "r", encoding="utf8", errors='ignore')
    file_data = file_pointer.read()
    file_lines = file_data.split('\n')
    terms = dict()
    for line in file_lines:
        if len(line) > 1:
            arr = line.split('\t')
            terms[arr[1]] = int(arr[0]) # <TERM, TERM_ID>

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


def deltaEncoding(index):
    retval = ""
    for ind in index:
        if len(index[ind]) > 0:
            total_occ = 0
            output = ""
            doc_ids = []
            i = 0
            for doc in index[ind]:
                j = 0
                for pos in index[ind][doc]:
                    if j == 0:
                        last_position = pos
                        index[ind][doc][j] = last_position
                    else:
                        index[ind][doc][j] = index[ind][doc][j] - last_position
                        last_position = last_position + index[ind][doc][j]
                    doc_ids.append(doc)
                    total_occ+=1
                    if (i == 0):
                        last_docid = doc_ids[i]
                        doc_ids[i] = last_docid
                    else:
                        doc_ids[i] = doc_ids[i] - last_docid
                        last_docid = last_docid + doc_ids[i]
                    output += " " + str(doc_ids[i]) + "," + str(index[ind][doc][j])
                    j += 1
                    i += 1

            retval += str(ind) + " " + str(total_occ) + " " + str(len(index[ind])) + output + "\n"

    return retval

#   10  18  25  25  29  35  39
#   10  8   7   0   4   6   4



def saveIndex(output):
    termindex_file = open(config.TERM_INDEX_FILE, "w", encoding="utf-8", errors='ignore')
    termindex_file.write(output)


def invertedIndex():
    documents = readDocIds(config.DOCID_FILE)
    terms = readTermIds(config.TERMID_FILE)
    count = 1

    # I'm going to save like index = <term_id, <doc_id, positons[]>>

    index = dict()
    for val in terms:
        index[terms[val]] = dict() # index = <term_id, <>>

    for doc in documents:
        file_pointer = open(config.CORPUS_DIR + doc, "r", encoding="utf8", errors='ignore')
        file_html = file_pointer.read()
        file_text = parseHtml(file_html)
        tokens = tokenize(file_text)
        tokens = stopwording(tokens)
        words = stemming(tokens)
        position_count = 1
        doc_index = dict()
        doc_id = documents[doc]
        for word in words:
            try:
                term_id = terms[word]
                index[term_id][doc_id].append(position_count)
            except:
                temp_word = str(word)
                term_id = terms[temp_word]
                index[term_id][doc_id] = []
                index[term_id][doc_id].append(position_count)
            position_count += 1
        if count > 100:
            break
        count += 1
        print("files done: " + str(count-1))

    output = deltaEncoding(index)
    saveIndex(output)
    print(output)

invertedIndex()