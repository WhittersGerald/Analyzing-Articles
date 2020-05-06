import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
from newspaper import Article
from newspaper import Config
import json


#month in YYYY-MM format
def scrape(query, month=""):

    last_day = 31
    time = ""

    if(month[-2:] == '02'):
        last_day = 28
    elif(month[-2:] in ['04', '06', '09', '11']):
        last_day = 30

    
    if(month != ""):
        time = "after:" + month + "-01" + " AND before:" + month + "-" + str(last_day) #last_day > 10 so no date formatting issues
    news = "https://news.google.com"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    page = requests.get("https://news.google.com/search?q=" + query + " " + time, headers=headers)
    soup = BeautifulSoup(page.content, features="lxml")
    found = soup.findAll("a")
    links = [x.get('href') for x in found]
    temp = []
    redirects = []
    articles = []
    count = 0
    for l in links:
        if(type(l) == str):
            if 'article' in l:
                if l not in redirects:
                    redirects.append(l)
                    count += 1

    redirects = [x[1:] for x in redirects]



    for a in redirects:
        try:
            r = requests.get(news + a, timeout=10)
            articles.append(r.url)
        except Exception as e:
            print(e)
        



    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    config = Config()
    config.browser_user_agent = user_agent

    a = None
    data = []
    for url in articles: 
        try:
            a = Article(url, config=config)
            a.download()
            a.parse()
            a.nlp()
            
            d ={"url": url,
                "title": a.title,
                "authors": a.authors,
                "date": a.publish_date.date(),
                "keywords": a.keywords,
                "summary": a.summary,
                #"text": a.text
                }
            data.append(d)

            #file.write(url + ";" + a.title + ";" + a.authors + ";" + a.publish_date.date() + ";" + a.summary.encode('unicode-escape') + ";" + a.text.encode('unicode-escape'))

            #print(a.title, a.authors, a.publish_date.date(), a.keywords)
            #print(a.summary)
            #print('*'*100)
        except Exception as e:
            print("Error with", url)
            print(a.title)
            print(e)
            print('*'*100)

    return data



if __name__ == '__main__':
    #Change city and m for different results
    city = "New York City, New York"
    m = "2019-08"
    data = []
    start = time.time()
    data.extend(scrape(city, m))
    file = open(city + ".json", "w+")
    json.dump(data, file, default=str)
    file.close()
    end = time.time()

    print("Total time:", (end-start)/60, "minutes")
