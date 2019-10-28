import sys
import config
from bs4 import BeautifulSoup
import re
from nltk.stem import PorterStemmer
from xml.dom import minidom
import math
import numpy


def main():
    topics = read_topic_file()
    process_all_queries(topics)
    # print_topics(topics)
    terms = readTermIds(config.TERMID_FILE)
    index = readTermIndex()
    doc_ids = readDocIds(config.DOCID_FILE)
    docs_length, avg_doc_length, total_length = count_words_in_all_docs(index)


    print("avg: " + str(avg_doc_length))
    print("total length: " + str(total_length))

    ds_score = okapi_bm25(topics, terms, index, docs_length, avg_doc_length)
    #ds_score = dirichlet_smoothing(topics, terms, index, docs_length, avg_doc_length, total_length)

    ds_score_sorted = [0]*len(topics)
    for i in range(0, len(topics)):
        ds_score_sorted[i] = [0]*len(docs_length)

    # sort these scores:
    for i in range(0, len(topics)):
        ds_score_sorted[i] = numpy.argsort(ds_score[i], -1) # argsort sorts in ascending order
        ds_score_sorted[i] = ds_score_sorted[i][::-1] # reverse

    # for i in range(0, len(topics)):
    #     for j in ds_score_sorted[i]:
    #         print("DOC: " + str(j+1) + "; Score: " + str(ds_score[i][j]))
    #     break

    evaluate_score(ds_score, ds_score_sorted, doc_ids, topics)
    # query_count = 0
    # for q in topics:
    #     print(topics[q])
    #     for j in range(0, len(docs_length)):
    #         if ds_score[query_count][j] > 0:
    #             print("DOC: " + str(j) + "; Score: " + str(ds_score[query_count][j]))
    #     break;
    #     query_count+=1


def okapi_bm25(topics, terms, index, docs_length, avg_doc_length):
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


def dirichlet_smoothing(topics, terms, index, docs_length, avg_doc_length, total_length):
    print("calculating relevance score using Dirichlet Smoothing...")
    doc_score = [1]*len(topics)
    print("len: " + str(len(docs_length)))
    for i in range(0, len(topics)):
        doc_score[i] = [1]*len(docs_length)

    for dl in range(0, len(docs_length)): # for every document in corpus
        query_count = 0
        for q in topics: # for every query 'q' in topics
            for i in topics[q]: # for every word 'i' in the query
                term_id = terms[i]
                res = index[term_id]
                term_count_in_doc = calc_term_freq_doc(dl+1, i)

                N = docs_length[dl]
                meu = avg_doc_length
                term_count_in_collection = calc_term_freq_col(res)

                # prob of i:

                probDOC = (term_count_in_doc)/docs_length[dl]
                probCOL = (term_count_in_collection)/total_length
                prob = (N/(N+meu))*probDOC + (meu/(N+meu))*probCOL
                doc_score[query_count][dl] *= prob


            query_count += 1

    print("calculating relevance score using Dirichlet Smoothing: COMPLETE")
    return doc_score


def evaluate_score(score, score_sorted, doc_ids, topics):
    print("Evaluating relevance score...")

    # read corpus query relevance judgement file
    file_pointer = open(config.CORPUS_GRADES_FILE, "r", encoding="utf8", errors='ignore')
    file_data = file_pointer.read()
    file_lines = file_data.split('\n')

    rel_score = dict()

    for t in topics:
        rel_score[t] = dict()

    for line in file_lines:
        if len(line) > 1:
            arr = line.split(' ')
            query_number = arr[0]
            document_name = arr[2]
            relevency_score = arr[3]
            doc_id = doc_ids[document_name]
            rel_score[query_number][doc_id] = int(relevency_score)
            # print("doc_id: " + str(doc_id) + "; query_number" + str(arr[0]) + "; score: " + str(rel_score[query_number][doc_id]))

    # reading done

    # PM@5:
    pm5 = dict()
    i = 0
    for q in topics:
        total_relevant_docs_retrieved = 0
        total_documents_retrieved = 0
        for j in score_sorted[i]:
            total_documents_retrieved += 1
            try:
                if rel_score[q][j+1] > 0:
                    total_relevant_docs_retrieved+=1
            except:
                total_relevant_docs_retrieved = total_relevant_docs_retrieved
            if total_documents_retrieved == 5:
                break
        i += 1
        # print("relevant docs: " + str(total_relevant_docs_retrieved) + "; retrieved: " + str(total_documents_retrieved))
        pm5[q] = total_relevant_docs_retrieved/total_documents_retrieved

    for q in pm5:
        print("pm@5 of Q" + str(q) + ": " + str(pm5[q]))


    # PM@10:
    pm10 = dict()
    i = 0
    for q in topics:
        total_relevant_docs_retrieved = 0
        total_documents_retrieved = 0
        for j in score_sorted[i]:
            total_documents_retrieved += 1
            try:
                if rel_score[q][j+1] > 0:
                    total_relevant_docs_retrieved+=1
            except:
                total_relevant_docs_retrieved = total_relevant_docs_retrieved
            if total_documents_retrieved == 10:
                break
        i += 1
        # print("relevant docs: " + str(total_relevant_docs_retrieved) + "; retrieved: " + str(total_documents_retrieved))
        pm10[q] = total_relevant_docs_retrieved/total_documents_retrieved

    for q in pm10:
        print("pm@10 of Q" + str(q) + ": " + str(pm10[q]))



    # PM@20:
    pm20 = dict()
    i = 0
    for q in topics:
        total_relevant_docs_retrieved = 0
        total_documents_retrieved = 0
        for j in score_sorted[i]:
            total_documents_retrieved += 1
            try:
                if rel_score[q][j + 1] > 0:
                    total_relevant_docs_retrieved += 1
            except:
                total_relevant_docs_retrieved = total_relevant_docs_retrieved
            if total_documents_retrieved == 20:
                break
        i += 1
        # print("relevant docs: " + str(total_relevant_docs_retrieved) + "; retrieved: " + str(total_documents_retrieved))
        pm20[q] = total_relevant_docs_retrieved / total_documents_retrieved

    for q in pm20:
        print("pm@20 of Q" + str(q) + ": " + str(pm20[q]))



    # PM@30:
    pm30 = dict()
    i = 0
    for q in topics:
        total_relevant_docs_retrieved = 0
        total_documents_retrieved = 0
        for j in score_sorted[i]:
            total_documents_retrieved += 1
            try:
                if rel_score[q][j + 1] > 0:
                    total_relevant_docs_retrieved += 1
            except:
                total_relevant_docs_retrieved = total_relevant_docs_retrieved
            if total_documents_retrieved == 30:
                break
        i += 1
        # print("relevant docs: " + str(total_relevant_docs_retrieved) + "; retrieved: " + str(total_documents_retrieved))
        pm30[q] = total_relevant_docs_retrieved / total_documents_retrieved

    for q in pm30:
        print("pm@30 of Q" + str(q) + ": " + str(pm30[q]))

    print("Evaluating relevance score: COMPLETE!")


def calc_term_freq_col(res):
    count = 0
    for doc in res:
        count += len(res[doc])
    return count


def calc_term_freq_doc(doc_id, res):
    for doc in res:
        if doc == doc_id:
            return len(res[doc]) # counting positions in document
    return 0


def calc_term_freq_query(query, word):
    count = 0
    for i in query:
        if i == word:
            count+=1
    return count


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
    print("counting words in doc: COMPLETE!")
    return docs_length, avg_doc_length, total_length

main()
