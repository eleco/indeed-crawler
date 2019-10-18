import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from functools import reduce
from collections import defaultdict

results = []
url_suffix='&sort=date&fromage=1&start={}'


#search criteria
cities ={
    'http://indeed.fr':['Rennes,+France','Lyon,+France'],
    'https://de.indeed.com':['München','Berlin']}

max_pages=1
blocked_companies =['sword', 'gfi', 'zenika', 'groupe sii', 'cgi group', 'gfi informatique']
blocked_titles=['Administrateur','trainee','junior']

with requests.Session() as s:

    for host in cities:
    
        for city in cities[host]:
        
            for page in range(max_pages):
                time.sleep(1)
                url= host + '/jobs?q=java' + '&l=' + city + url_suffix
                res = s.get(url.format(page))
                soup = bs(res.content, 'lxml')
                urls = [item for item in soup.select('.title > a')]
                titles = [item.text.strip() for item in soup.select('[data-tn-element=jobTitle]')]
                companies = [item.text.strip() for item in soup.select('.company')]
                locations = [item.text.strip() for item in soup.select('span.location')]
                hrefs = [ host+url['href'] for url in urls]

                list_of_tuples  = list(zip(titles, companies, locations, hrefs))
                results = results + list_of_tuples


#build dataframe
df = pd.DataFrame(results, columns = ['title','company','location','href'])

# remove blocked companies
df = df[~df['company'].str.lower().isin([x.lower() for x in blocked_companies])]

# remove blocked titles
df = df [~df.title.apply(lambda sentence: any(word.lower() in sentence.lower() for word in blocked_titles))]


# add href to the job advert
df['joburl'] = '<a href="' + df['href']+ '">' + df['title'] + '</a>'
df = df.drop(columns=['href'])
print(df)

# generate output
pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>

html_string = '''
<html>
  <head><title>HTML Pandas Dataframe with CSS</title></head>
  <link rel="stylesheet" type="text/css" href="df_style.css"/>
  <body>
    {table}
  </body>
</html>.
'''

# OUTPUT AN HTML FILE
with open('test.html', 'w') as f:
    f.write(html_string.format(table=df.to_html(escape=False, classes='mystyle')))



