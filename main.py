import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time

max_pages=2
host="http://indeed.fr"
max_pages=2
cities=['Rennes,+France','Lyon,+France']
results = []
url_prefix = host + '/jobs?q=java'
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
            locations = [item.text.strip() for item in soup.select('span.location')]
            dates = [item.text.strip() for item in soup.select('span.date')]
            hrefs = [ host+url['href'] for url in urls]
            results.append(list(zip(titles, companies, locations, dates, hrefs)))



df = pd.DataFrame([item for sublist in results for item in sublist])
df['joburl'] = '<a href="' + df.iloc[:,4]+ '">' + df.iloc[:,0] + '</a>'
df.drop(df.columns[[0,4]],axis=1,inplace=True)
print(df)
df.to_html("test.html",escape=False)


