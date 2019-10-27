import sys
import config
import re
from nltk.stem import PorterStemmer
from xml.dom import minidom


def main():
    topics = read_topic_file()
    process_all_topics(topics)
    print_topics(topics)


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


def process_all_topics(topics):
    for topic in topics:
        tp = topics[topic]
        tokens = tokenize(tp)
        tokens = stopwording(tokens)
        words = stemming(tokens)
        topics[topic] = words


def print_topics(topics):
    for topic in topics:
        print(topics[topic])


main()
