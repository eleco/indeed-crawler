import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from functools import reduce
from collections import defaultdict
import os
import sys
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import date

# sendgrid settings
sendgrid_key = os.environ.get('SENDGRID_KEY')
to_email = os.environ.get('SENDGRID_RECIPIENT')
sg = SendGridAPIClient(sendgrid_key)


results = []
url_suffix='&sort=date&fromage=1&start={}'


#serach criteria for cities 
#cities ={
#    'http://indeed.fr':['Rennes,+France','Lyon,+France', 'Bordeaux,+France', 'Pau,+France', 'Toulouse,+France', 'Marseille,+France'],
#    'http://indeed.es':['Barcelona','Valencia','Madrid'],
#    'https://de.indeed.com':['München','Berlin'],
#    'http://indeed.co.uk':['London'],
#    'https://www.indeed.nl':['Amsterdam'],
#    'http://indeed.com.sg':['Singapore'],
#    'https://www.indeed.pt':['Lisboa']}

cities ={
    'http://indeed.fr':['Remote','Bordeaux','Marseille','Toulouse'],
    'http://indeed.es':['Remote'],
    'https://de.indeed.com':['Remote'],
    'http://indeed.co.uk':['Remote','Cambridge'],
    'https://www.indeed.nl':['Remote'],
    'http://indeed.com.sg':['Remote'],
    'https://www.indeed.pt':['Remote'],
    'https://www.indeed.ch':['Remote','Lausanne','Geneva','Zurich']
    }



# max paging per city
max_pages=2

#skill sought for
skill = 'java'

#blocked companies and titles removed from the results
blocked_companies =['sword', 'gfi', 'zenika', 'groupe sii', 'cgi group', 'gfi informatique','netcentric','utigroup','onepoint']
blocked_titles=['Administrateur','trainee','junior','test','stage','cobol','php','ios','enseignant','marketing','seo']

with requests.Session() as s:

    for host in cities:
    
        for city in cities[host]:
            print("fetching jobs for: " + host +  " in:" + city)
        
            for page in range(max_pages):
                time.sleep(1)
                url= host + '/jobs?q=' + skill + '&l=' + city + url_suffix
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

if len(df)==0:
    sys.exit()

# add href to the job advert
df['joburl'] = '<a href="' + df['href']+ '">' + df['title'] + '</a>'
df = df.drop(columns=['href'])
print(df)

# generate output
pd.set_option('colheader_justify', 'center')   # FOR TABLE <th>

with open('df_style.css','r') as css_f:
    css = css_f.read()

table = df.to_html(escape=False, classes='mystyle')
html_string = '''
<html>
  <head><title>Indeed Crawler</title>
  <style>''' + css + '''</style></head>
  <body>'''  + table + '''  
 </body>
</html>.
'''

# OUTPUT AN HTML FILE AND SEND AS EMAIL
with open('jobs.html', 'w+') as f:
    f.write(html_string)
    f.seek(0)
    sg.send(Mail(from_email='indeed-crawler@noreply',
                subject="jobs crawled at: "+ str(date.today()), 
                to_emails=to_email,
                html_content=f.read()))

