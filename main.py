import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time

max_pages=2
host="www.indeed.fr"
max_pages=2
cities=['Rennes,+France','Lyon,+France']
results = []
url_prefix = 'https://' + host + '/jobs?q=java'
url_suffix='&sort=date&start={}'
with requests.Session() as s:

    for city in cities:
    
        for page in range(max_pages):
            time.sleep(1)
            url=url_prefix + '&l=' + city + url_suffix
            res = s.get(url.format(page))
            soup = bs(res.content, 'lxml')
            urls = [item for item in soup.select('.title > a')]
            titles = [item.text.strip() for item in soup.select('[data-tn-element=jobTitle]')]
            companies = [item.text.strip() for item in soup.select('.company')]
            location = [item.text.strip() for item in soup.select('span.location')]
            date = [item.text.strip() for item in soup.select('span.date')]
  
            us = [ host+u['href'] for u in urls]
  
            data = list(zip(titles, companies, location, date, us))
            results.append(data)



newList = [item for sublist in results for item in sublist]
df = pd.DataFrame(newList)
print(df)