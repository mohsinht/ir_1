import sys
import config
from bs4 import BeautifulSoup
import re
from nltk.stem import PorterStemmer
from xml.dom import minidom
import math


def main():
    topics = read_topic_file()
    process_all_queries(topics)
    # print_topics(topics)
    terms = readTermIds(config.TERMID_FILE)
    index = readTermIndex()
    docs_length, avg_doc_length, total_length = count_words_in_all_docs(index)

    print("avg: " + str(avg_doc_length))
    print("total length: " + str(total_length))

    bm25_score = okapi_bm25(topics, terms, index, docs_length, avg_doc_length, total_length)

    query_count = 0
    for q in topics:
        print(topics[q])
        for j in range(0, len(docs_length)):
            if bm25_score[query_count][j] > 0:
                print("DOC: " + str(j) + "; Score: " + str(bm25_score[query_count][j]))

        query_count+=1


def okapi_bm25(topics, terms, index, docs_length, avg_doc_length, total_length):
    print("calculating relevance score using BM25...")
    doc_score = [0]*len(topics)
    print("len: " + str(len(docs_length)))
    for i in range(0, len(topics)):
        doc_score[i] = [0]*len(docs_length)

    k1 = 1.2
    k2 = 140
    b = 0.75
    D = len(docs_length) # number of documents

    for dl in range(0, len(docs_length)): # for every document in corpus
        query_count = 0
        for q in topics: # for every query 'q' in topics
            for i in topics[q]: # for every word 'i' in the query

                K = k1*((1-b) + b * (docs_length[dl]/avg_doc_length))

                term_id = terms[i]
                res = index[term_id]
                dfi = len(res)
                tfdi = calc_term_freq_doc(dl+1, res)
                tfqi = 1 # calc_term_freq_query(q, i)
                x1 = math.log2((D + 0.5)/dfi + 0.5)
                y1 = ((1 + k1)*tfdi)/(K+tfdi)
                z1 = ((1 + k2)*tfqi)/(k2 + tfqi)
                score = x1 * y1 * z1
                doc_score[query_count][dl] += score
                if doc_score[query_count][dl] > 0:
                    print(doc_score[query_count][dl])
            query_count += 1

    print("calculating relevance score using BM25: COMPLETE!")
    return doc_score




def calc_term_freq_doc(doc_id, res):
    for doc in res:
        if doc == doc_id:
            return len(res[doc]) # counting positions in document
    return 0


def calc_term_freq_query(query, word):
    return query.count(word)

def read_topic_file():
    print("Reading topics.xml file...")
    topics = dict()
    xmldoc = minidom.parse(config.TOPICS_FILE)
    topiclist = xmldoc.getElementsByTagName('topic')
    totalQueries = len(topiclist)
    print("Total Queries: " + str(totalQueries))
    for s in range(0, totalQueries):
        topic_number = topiclist[s].attributes['number'].value
        query_child = topiclist[s].getElementsByTagName('query')
        topics[topic_number] = query_child[0].childNodes[0].nodeValue
    print("Reading topics.xml file: COMPLETE!")
    return topics


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


def process_all_queries(topics):
    for topic in topics:
        tp = topics[topic]
        tokens = tokenize(tp)
        tokens = stopwording(tokens)
        words = stemming(tokens)
        topics[topic] = words


def print_topics(topics):
    for topic in topics:
        print(topics[topic])


def readDocIds(docids_file):
    print("reading document ids...")
    file_pointer = open(docids_file, "r", encoding="utf8", errors='ignore')
    file_data = file_pointer.read()
    file_lines = file_data.split('\n')
    documents = dict()
    for line in file_lines:
        if len(line) > 1:
            arr = line.split('\t')
            documents[arr[1]] = int(arr[0]) # <DOC_NAME, DOC_ID>
    print("reading document ids: COMPLETE!")
    return documents


def readTermIds(termids_file):
    print("reading term ids...")
    file_pointer = open(termids_file, "r", encoding="utf8", errors='ignore')
    file_data = file_pointer.read()
    file_lines = file_data.split('\n')
    terms = dict()
    for line in file_lines:
        if len(line) > 1:
            arr = line.split('\t')
            terms[arr[1]] = int(arr[0]) # <TERM, TERM_ID>
    print("reading term ids: COMPLETE!")
    return terms


def readTermIndex():
    print("reading term index file...")
    file_pointer = open(config.TERM_INDEX_FILE, "r", encoding="utf8", errors='ignore')
    file_data = file_pointer.read()
    file_lines = file_data.split('\n')
    index = dict() # index = <>
    for line in file_lines:
        arr = line.split(' ')
        if len(arr[0]) < 1:
            continue
        i = 0
        term_id = int(arr[0])
        firstDocId = True
        totalId = 0
        positions = []
        index[term_id] = dict() # index = <term_id, <>>
        for part in arr:
            if i > 2: # skipping the first 3 numbers which are term_id, count_in_corpus, document_count
                doc_pos = part.split(',') # split doc_id and position
                if firstDocId: # no decoding is needed in first doc_id
                    try:
                        index[term_id][int(doc_pos[0])].append(int(doc_pos[1])) # index = <term_id, <doc_id, positions[]>>
                    except:
                        index[term_id][int(doc_pos[0])] = []
                        index[term_id][int(doc_pos[0])].append(int(doc_pos[1]))
                    totalId = int(doc_pos[0])
                    firstDocId = False
                else:
                    totalId += int(doc_pos[0])
                    try:
                        index[term_id][int(totalId)].append(int(doc_pos[1]))
                    except:
                        index[term_id][int(totalId)] = []
                        index[term_id][int(totalId)].append(int(doc_pos[1]))
            i+=1
    print("reading term index file: COMPLETE!")
    return index


def count_words_in_all_docs(index):
    print("counting words in doc...")
    docs_length = [0]
    total_length = 0
    avg_doc_length = 0

    for i in range (0, 3000):
        docs_length.append(0)

    for term_id in index: # index = <term_id, <doc_id, positions[]>>
        for doc_id in index[term_id]: # <doc_id, positions[]>
            docs_length[int(doc_id)-1] += len(index[term_id][doc_id]) # sum of length of positions array
            total_length += len(index[term_id][doc_id])

    avg_doc_length = (total_length/len(docs_length))

    return docs_length, avg_doc_length, total_length

main()
