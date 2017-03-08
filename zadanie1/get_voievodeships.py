import requests
import re

r = re.compile(r'WOJ\. (\S*)<')

voievodeship = {}

for i in range(1, 69):
    page = requests.get('http://prezydent2000.pkw.gov.pl/wb/okreg/o{:02}.html'.format(i))
    page.encoding = 'ISO-8859-2'
    voievodeship[i] = r.search(page.text).group(1).lower()

print(voievodeship)
