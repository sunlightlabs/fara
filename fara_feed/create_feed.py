# this is modified from Arron's reporting feed for the lobbying tracker in "Willard"
import datetime
import re
import sys
import time
import urllib
import urllib2

import lxml.html
from bs4 import BeautifulSoup

def fara_handle():
    url = 'https://efile.fara.gov/pls/apex/f?p=125:10:::NO::P10_DOCTYPE:ALL'

    page = urllib2.urlopen(url).read()
    doc = lxml.html.fromstring(page)
    form = doc.cssselect('form')[0]

    data = []
    for input in form.cssselect('input'):
        if input.attrib.get('name'):
            if input.attrib['name'] in ('p_t01', 'p_t02', 'p_t06', 'p_t07', 'p_request'):
                continue
            data.append((input.attrib['name'], input.attrib['value']))

    start_date = datetime.date(2013, 05, 29) - datetime.timedelta(9)
    print start_date
    end_date = datetime.date.today()

    data += [('p_t01', 'ALL'),
             ('p_t02', 'ALL'),
             ('p_t06', start_date.strftime('%m/%d/%Y')),
             ('p_t07', end_date.strftime('%m/%d/%Y')),
             ('p_request', 'SEARCH'),
             ]
    
    #url = 'http://209.11.109.152/pls/htmldb/wwv_flow.accept'
    url = 'https://efile.fara.gov/pls/apex/wwv_flow.accept'

    req = urllib2.Request(url, data=urllib.urlencode(data))
    page = urllib2.urlopen(req).read()
    
    #new
    
    page = BeautifulSoup(page)
    filings = page.find("table", {"class" : "t14Standard"})
    #print filings
    
    fara_urls = []
    
    for l in filings.find_all("a"):
        link = str(l)
        url = str(re.findall(r'href="(.*?)"', link))
        url = re.sub("\['",'', re.sub("'\]", '', url))
        if url[:4] == "http":
            reg_id = re.sub('-','', link[34:38])
            re.findall(r'href="(.*?)"', url)
            info = re.findall( r'-(.*?)-', url)
            
            if info[0] == 'Amendment':
                doc_type = 'Amendment'
                raw_date = None
            
            else:
                raw_date = info[1]
                
                if info[0] == 'Short':
                    doc_type = 'Short Form'
            
                elif info[0] == 'Exhibit':
                    if "AB" in url:
                        doc_type = 'Exhibit AB'  
                    if "C" in url:
                        doc_type = 'Exhibit C'    
                    if "D" in url:
                        doc_type = 'Exhibit D'
                
                elif info[0] == 'Conflict':
                    doc_type = 'Conflict Provision'
                
                elif info[0] == 'Registration':
                    doc_type = 'Registration'
            
                elif info[0] == 'Supplemental':
                    doc_type = 'Supplemental' 
                
                else:
                    print "Can't identify form-- ", url
                
            if raw_date != None:
                raw_date = raw_date[3:5] + raw_date[-2:] + raw_date[:4]
                print raw_date
                stamp_date = datetime.datetime.strptime(raw_date, "%M%d%Y")
            else:
                stamp_date = raw_date
            
            url_info= [{'url':url}, {'reg_id':reg_id}, {'doc_type':doc_type}, {'stamp_date': stamp_date}]
            print url_info
            fara_urls.append(url_info)
      
       
    return fara_urls
    
    
        
fara_handle()


