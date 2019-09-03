import config
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join

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

def processFiles(dir):
    #read file names
    file_names = [dir+file for file in listdir(dir) if isfile(join(dir, file))]
    for file_name in file_names:
        file_pointer = open(file_name, "r")
        file_html = file_pointer.read()
        parseHtml(file_html)
        file_text = parseHtml(file_html)
        print(file_text)
        file_pointer.close()
        break


print("getting files from " + config.DIR)
processFiles(config.DIR)

