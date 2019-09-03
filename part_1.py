import config
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join


def extractTextFromHtml(dir):
    #read file names
    onlyfiles = [f for f in listdir(dir) if isfile(join(dir, f))]
    print(onlyfiles)


print("getting files from " + config.DIR)
extractTextFromHtml(config.DIR)

