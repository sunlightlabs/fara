# this is modified from Arron's reporting feed for the lobbying tracker in "Willard"
import datetime
import re
import sys
import time
import urllib
import urllib2
import string
import lxml.html
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option

from fara_feed.models import Document

def add_document(url_info):
    document = Document(url = url_info[0],
        reg_id = url_info[1],
        doc_type = url_info[2],
        stamp_date = url_info[3],
    )
    document.save()
    

def parse_and_save(page):
    print "Starting parse and save"
    filings = page.find("table", {"class" : "t14Standard"})
    new_fara_docs = []
    

    for l in filings.find_all("tr"):
        #print "starting l loop"
        row = str(l)
        url = str(re.findall(r'href="(.*?)"', row))
        print url
        url = str(url)
        url = re.sub("\['",'', re.sub("'\]", '', url))
    
        if url[:4] == "http":
            stamp_date = l.find_all('td',{"headers" : "STAMPED/RECEIVEDDATE"})
            stamp_date = str(stamp_date)[-16:-6]
            stamp_date_obj = datetime.datetime.strptime(stamp_date, "%m/%d/%Y")

            if Document.objects.filter(url = url).exists():
                pass
            else:     
                reg_id = re.sub('-','', url[25:29])
                reg_id = re.sub('S','', reg_id)
                reg_id = re.sub('L','', reg_id)
                re.findall(r'href="(.*?)"', url)
                info = re.findall( r'-(.*?)-', url)

                if info[0] == 'Amendment':
                    doc_type = 'Amendment'

                elif info[0] == 'Short':
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

                if stamp_date_obj != None:
                    try:
                        stamp_date = re.findall(r'\d{8}', url)
                        stamp_date = stamp_date[0]
                        stamp_date_obj = datetime.datetime.strptime(stamp_date, "%Y%m%d")
                    except:
                        stamp_date_obj = datetime.date.today()

                url_info= [url, reg_id, doc_type, stamp_date_obj]
                #saves url info
                add_document(url_info)

                new_fara_docs.append(url_info)
                print "saving", url_info
                ##new_info.append(new_fara_docs)
                   
    return new_fara_docs

class Command(BaseCommand):
    can_import_settings = True
    #option_list = BaseCommand.option_list + (
        #make_option()) to add more console command options
        
    def handle(self, *args, **options):
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

        start_date = datetime.date.today() - datetime.timedelta(days=10)
        
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
        page = BeautifulSoup(page)
        parse_and_save(page)
    
        #looking for additional pages of results 
        url_end = page.find("a", {"class":"t14pagination"})
        count = 0 
        
        while url_end != "None" and url_end != None:

            url_end = str(url_end)
            url_end = url_end.replace('&amp;', '&')
            url_end = re.sub('<a class="t14pagination" href="', '/', url_end) 
            url_end = re.sub('">Next &gt;</a>', '', url_end)
            #url_end = re.sub('>&lt;Previous</a>', '', url_end)
            next_url = 'https://efile.fara.gov/pls/apex' + url_end
            
            req = urllib2.Request(next_url)
            page = urllib2.urlopen(req).read()
            page = BeautifulSoup(page)
            new_info = parse_and_save(page)
            
            url_end = page.findAll("a", {"class":"t14pagination"})
            
            #for m in url_end:
            if len(url_end) > 1:
                url_end = url_end[1]
            else: 
                break
            
            
            new_info = parse_and_save(filings)
            print datetime.date.today()
            print new_info
          
        #return new_fara_docs



