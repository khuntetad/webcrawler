import csv
import datetime
import requests
import requests.compat
import os, os.path
import nltk

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from whoosh import index
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID

from bs4 import BeautifulSoup

# need to define a schema for whoosh to be able to index
# schema sets the fields and types we are searching for
def setup_whoosh_schema():
    return Schema(url=ID(stored=True, unique=True), content=TEXT)

# make a index object https://whoosh.readthedocs.io/en/latest/indexing.html
def create_index():
    if not os.path.exists("indexdir"):
        os.mkdir("indexdir")
    ix = index.create_in("indexdir", schema=setup_whoosh_schema())
    return ix

# given a seed url and an index writer
def crawl(seed_url, index_writer, max_pages = 1000):
    # set something to track what we have visited to prevent duplicateds
    visited = set()

    # instantiate something for the crawler to process
    crawler_process = [seed_url]
    count = 0

    # store all of the information into a csv file
    with open("crawled_data.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["URL", "TIMESTAMP", "KEYWORDS", "CONTENT"])
        # pop the instances from the crawler_process and keep going
        # while we are less than the max_pages and have a nonempty queue

        while count < max_pages and len(crawler_process) > 0:
            # pop the url
            # if we have already visited it we don't need to process
            current_url = crawler_process.pop(0)
            if current_url in visited:
                continue
            else:
                # now we need to get all of the links on the webpage
                # this requires us to visit the url
                # in the url search for anything with a href
                try:
                    response = requests.get(current_url, timeout=10)

                    # check to see if we have a successful request
                    # if we do this means that we need to add to the index writer
                    if response.status_code == 200:
                        # use beautiful soup here to get content
                        soup = BeautifulSoup(response.text, 'html.parser')

                        # use the soup to get the relevant text
                        soup_content = soup.get_text()
                        index_writer.add_document(url=current_url, content=soup.get_text())
                        visited.add(current_url)
                        count += 1

                        keywords = get_keywords(soup_content)

                        # pass the url, timestamp of when accessed, get top keywords, and content
                        writer.writerow([
                            current_url,
                            datetime.now().isoformat(),
                            ", ".join(keywords[:20]),
                            soup_content[:300]
                        ])

                        # now we have added a document for the current url
                        # extract everything else
                        for link in soup.find_all('a', href=True):
                            new_url = requests.compat.urljoin(current_url, link['href'])
                            # if this is extended off of our seed_url we need to visit it
                            if new_url.startswith(seed_url) and new_url not in visited and new_url not in crawler_process:
                                print(new_url)
                                crawler_process.append(new_url)
                except:
                    print(f"There was an error in parsing the {current_url} page")
    return visited

# now we need to extract the keywords for each of the subsections
def get_keywords(text):
    # get the stopwords so we know what is irrelevant
    nltk.download("stopwords", quiet=True)

    # need this so we can be able to break up the text into words
    nltk.download("punkt", quiet=True)
    stop = set(stopwords.words("english"))
    words = word_tokenize(text.lower())

    # return a list of all of the words that are alphanum and not a irrelevant stopword
    return [word for word in words if word.isalnum() and word not in stopwords]

if __name__ == "__main__":
    seed_url = "https://www.cc.gatech.edu/"
    use_index = create_index()

    with use_index.writer() as writer:
        url_list = crawl(seed_url, writer, max_pages=100)
    print(f"Crawled {len(url_list)}")