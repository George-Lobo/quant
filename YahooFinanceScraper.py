# scraper for Yahoo Finance; access currently denied due to number of requests; maybe adjust frequency in the future?

# the robots.txt file does not disallow scraping of the pages needed; also, this scraper does not go against
# Yahoo's Terms of Service (https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html)

import requests
import pandas as pd
from bs4 import BeautifulSoup

test_offset = 0
yahoo_finance_url = f'https://finance.yahoo.com/most-active?count=100&offset={test_offset}'

result = requests.get(yahoo_finance_url)
doc = BeautifulSoup(result.text, 'lxml')

table1 = doc.find('table')

print(table1)