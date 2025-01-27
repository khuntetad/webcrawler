# Problem 1.2: Write a Web Crawler of your own
## By: Devansh Khunteta

## Setup
To create the environment for the web crawler, a few different packages will need to be installed within the Conda environment. The process to do so is as follows:

```
conda create -n webcrawler python=3.9
conda activate webcrawler
```

Due to there being a bug with the latest NLTK, we need to install a downgraded version. The following is the process needed to download the packages:

```
conda install -c conda-forge nltk=3.8.1
conda install -c conda-forge matplotlib whoosh beautifulsoup4 requests
```

Once each of these packages has successfully been downloaded onto the conda environment, the Python file can be executed to generate the CSV containing the webpages crawled mapped to their corresponding timestamps, keywords, and a brief content description. The file can be ran within the conda environment as follows:

```
python3 webcrawler.py
```

## Web Crawler Design
The crawler was designed to efficiently crawl web pages and gather data that will be stored in a structured format through a CSV as well as a indexed format through Whoosh. Whoosh is the backing package that is utilized for more efficient full-text indexing and searching as it is compatible with Python. 

First, there is a seed URL that the crawler is instantiated with. By providing this seed url, it is ensured that the crawling is restricted to the same domain and does not crawl onto other sites. By using the requests package, we fetch the webpages through an HTTP request. Once the URL is visited, the BeautifulSoup package is employed to be able to break down the content on the website to human-readable content. The Python script searches for references to any href link. The NLTK package is also used to tokenize the content and select the alphanumeric tokens, while ensuring that keywords are stored within the CSV. Finally, the crawler keeps track of the number of URLs that are crawled as well as the number of keywords that are extracted. The crawl speed is also measured, and all of these metrics are plotted by using Matplotlib.

## Pros

There were a few different pros that were noted as a result of creating this web crawler.

- Focused Crawling
    - Because we are building off of a specific seed URL, the data collection is much more targeted and focused.
- Scalable Storage
    - Whoosh is a very efficient library and hence the speeds of hte crawler are pretty fast for searching capabilities.
    - Similarly storing information in a CSV is very lightweight and does not waste many resources.
- Tracking Metrics
    - Because we are doing things like tracking metrics and gracefully handling errors, it is simple to tell when something unexpected could be taking place in the web crawler's execution. 

## Cons
- Limited Content Analyses
    - Only simple keyword extraction is employed within the web crawler. As a result, there are very similar keywords for many of the webpages.
    - The content could have been further preprocessed to be able to come up with more informative content descriptions. Currently the content is simply cut into the first 200 characters that are encountered, which often may not be indicative of what is on the webpage. 
- Single Threaded
    - The current parser is single threaded and pops a single webpage at a time. If the process was made multithreaded it could improve the speed for crawling at a much larger scale. 

## Web Crawler Terminal Descriptions and Crawl Statistics
To generate the crawl statistics and CSV with keywords and content descriptions for the thousand webpages simply execute the Python file. Doing so results in the crawled_data.csv with the information for each of the crawled webpages. Moreover, the command results in the graphs for the crawl speed and keyword extraction speed in the keywords_over_time.png, crawl_speed.png, crawl_over_time.png. Each of these files can be found within the submission ZIP. 

## Experience and Lessons Learned
Building the web crawler was an interesting experience that allowed me to combine the concepts that we learned in class along with Python packages. Throughout the process, I learned much more about scraping HTML from webpages through libraries such as BeautifulSoup and integrating tools such as NLTK for things such as keyword extraction. Moreover, I learned valuable skills for analyzing metrics and evaluating efficiencies through the generated Matplotlib plots.

A significant lesson that was affirmed through this project was the importance of having a modular design within my code with helpful error handling. There were points within the homework where it would seem as if all of the components were working and a small change would cause everything to break. After this happened, I decided to seperate functionalities such as crawling, data extracting and keyword processing to debug more effectively. A specific example of this was recognizing that when I added keyword extraction, there was an issue within the NLTK package version that I was using. Before I added modularity and error handling within my code, I had no idea as to how a seemingly small change caused everything to break. However, implementing this logic made it much more clear what specifically was going wrong within my code. 

With the current performance, as extrapolated from the Matplotlib graphs, we can also calculate how long it would take for the crawler to go through 10 million pages by utilizing the formula: $$Time (seconds) = PageCount/CrawlSpeed$$. With the calculated crawl speed of 3.5 seconds per page, 10 million pages would take 2857142 seconds and a billion pages would take 285714285 seconds to complete. Though the codebase was much more easy to maintain through modular design and error handling, there is definitely room for improvement. As mentioned in the cons section of the README, the project could be made more efficient by adding multithreading. 
