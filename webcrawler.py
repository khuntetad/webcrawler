import csv
import time
import requests
import requests.compat
import os, os.path
import nltk
import matplotlib.pyplot as plt

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from datetime import datetime

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

    # need to set a start time, url count, keyword count
    start_time = time.time()
    crawl_times = []
    url_count = []
    keyword_count = []

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
                        print("FINISHED WRITING")

                        # pass the url, timestamp of when accessed, get top keywords, and content trimmed
                        writer.writerow([
                            current_url,
                            datetime.now().isoformat(),
                            ", ".join(keywords[:20]),
                            soup_content[:200]
                        ])

                        crawl_times.append(time.time() - start_time)
                        keyword_count.append(len(keywords))
                        url_count.append(len(url_count))
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

    crawl_stats = {
        "crawl_times": crawl_times,
        "keywords_count": keyword_count,
        "url_count": url_count
    }

    return visited, crawl_stats

# now we need to extract the keywords for each of the subsections
def get_keywords(text):
    # get the stopwords so we know what is irrelevant

    if not text.strip():
        return []

    # downgraded to nltk 3.8.1, there is a bug in the current version
    nltk.download("stopwords", quiet=True)
    print("stopwords downloaded")
    # need this so we can be able to break up the text into words
    nltk.download("punkt", quiet=True)
    print("second downloaded")
    stop = set(stopwords.words("english"))
    print(len(stop))
    # there might be an issue if we pass in too much data
    try:
        print(f"Text that we are passing in: {text[:100]}")
        words = word_tokenize(text.lower()[:100])
        print("TOKENIZED")
    except Exception as e:
        print(f"Error during tokenization: {e}")

    # return a list of all of the words that are alphanum and not a irrelevant stopword
    return [word for word in words if word.isalnum() and word not in stop]

if __name__ == "__main__":
    seed_url = "https://www.cc.gatech.edu/"
    use_index = create_index()

    with use_index.writer() as writer:
        url_list, crawl_stats = crawl(seed_url, writer, max_pages=5)

    crawl_timing = crawl_stats["crawl_times"]
    keywords_count = crawl_stats["keywords_count"]
    url_count = crawl_stats["url_count"]

    # Crawl Statistics (Crawl speed #pages/minute, ratio of #URL crawled / #URL to be crawled, etc.)

    # first we find the pages crawled per minute
    plt.plot(crawl_timing, url_count, label="URLs Crawled")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Number of URLs Crawled")
    plt.title("URLs Crawled over Time")
    plt.legend()
    plt.savefig("crawl_over_time.png")
    plt.show()

    # plot the keywords that we have extracted over a period of time
    plt.plot(crawl_timing, keywords_count, label="Keywords Extracted", color="green")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Number of Keywords Extracted")
    plt.title("Keywords Extracted over Time")
    plt.legend()
    plt.savefig("keywords_over_time.png")
    plt.show()

    # also need to plot the speed of the crawl
    crawl_speed = [urls / time if time > 0 else 0 for urls, time in zip(url_count, crawl_timing)]
    plt.plot(crawl_timing, crawl_speed, label = "Crawl Speed (Pages / Sec)", color = "blue")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Pages per Second")
    plt.title("Crawl Speed over Time")
    plt.legend()
    plt.savefig("crawl_speed.png")
    plt.show()