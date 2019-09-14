import sys
import config
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


def readTermIndex():
    file_pointer = open(config.TERM_INDEX_FILE, "r", encoding="utf8", errors='ignore')
    file_data = file_pointer.read()
    file_lines = file_data.split('\n')
    index = dict()
    for line in file_lines:
        arr = line.split(' ')
        if len(arr[0]) < 1:
            continue
        i = 0
        term_id = int(arr[0])
        firstDocId = True
        totalId = 0
        positions = []
        index[term_id] = dict()
        for part in arr:
            if i > 2:
                doc_pos = part.split(',')
                if firstDocId:
                    try:
                        index[term_id][int(doc_pos[0])].append(int(doc_pos[1]))
                    except:
                        index[term_id][int(doc_pos[0])] = []
                        index[term_id][int(doc_pos[0])].append(int(doc_pos[1]))

                    totalId = int(doc_pos[1])
                    firstDocId = False
                else:
                    totalId += int(doc_pos[0])
                    try:
                        index[term_id][int(totalId)].append(int(doc_pos[1]))
                    except:
                        index[term_id][int(totalId)] = []
                        index[term_id][int(totalId)].append(int(doc_pos[1]))
            i+=1

    return index



ps = PorterStemmer()
searched_term = ps.stem(str(sys.argv[1]))

print("Listing for term (stemmed): " + searched_term)
terms = readTermIds(config.TERMID_FILE)

index = readTermIndex()

term_id = terms[searched_term]

if term_id is None:
    print("Term not found.")
else:
    try:
        res = index[term_id]
        print("TERMID: " + str(term_id))
        print("Number of documents containing term: " + str(len(res)))

        total_occ = 0
        for doc in res:
            for pos in res[doc]:
                total_occ += 1

        print("Term frequency in corpus: " + str(total_occ))
    except:
        print("not found")




