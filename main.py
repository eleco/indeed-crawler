import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from collections import defaultdict

max_pages=1
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

            list_of_tuples  = list(zip(titles, companies, locations, dates, hrefs))
            results = results + list_of_tuples


df = pd.DataFrame(results, columns = ['title','company','location','date','href'])


# drop adverts which are not of today
d = defaultdict(lambda: -1)
d.update({'Aujourd\'hui': 0, 'Publiée à l\'instant': 0})
df['normalized_date'] = df.iloc[:,3].map(d)
df = df[df.normalized_date != -1]

# add href to the job advert
df['joburl'] = '<a href="' + df['href']+ '">' + df['title'] + '</a>'
df = df.drop(columns=['href', 'date' , 'normalized_date'])

# generate output
print(df)
df.to_html("test.html",escape=False)


