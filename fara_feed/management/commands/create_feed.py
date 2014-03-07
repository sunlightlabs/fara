# this is modified from Arron's reporting feed for the lobbying tracker in "Willard"
import datetime
import re
import sys
import time
import urllib
import urllib2
import string
import lxml.html
import logging

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

from bs4 import BeautifulSoup
from optparse import make_option

from fara_feed.models import Document

logging.basicConfig()
logger = logging.getLogger(__name__)

def pdf2htmlEX(): 
    return true


def add_document(url_info):
    document = Document(url = url_info[0],
        reg_id = url_info[1],
        doc_type = url_info[2],
        stamp_date = url_info[3],
    )
    document.save()
    
def add_file(url):
    if url[:25] != "http://www.fara.gov/docs/":
        message = 'bad link ' + url
        logger.error(message)
    
    else:
        file_name = "pdfs/" + url[25:]
        if not default_storage.exists(file_name):
            try:
                url = str(url)
                u = urllib2.urlopen(url)
                localFile = default_storage.open(file_name, 'w')
                localFile.write(u.read())
                localFile.close() #http://www.fara.gov/
		# shim here !! --timball need to know what the filename is ... and either call my script . 
		# so maybe GET the file from s3 . and the process w/ pdf2htmlEX . i'll make a function pdf2htmlEX($) that takes the url to the the document . 
                doc = Document.objects.get(url=url)
                doc.uploaded = True
                doc.save() 
            except:
                message = 'bad upload ' + url
                logger.error(message)
        else:
            doc = Document.objects.get(url=url)
            if doc.uploaded != True:  
                doc.uploaded = True
                doc.save()


def parse_and_save(page):
    filings = page.find("table", {"class" : "t14Standard"})
    new_fara_docs = []
    

    for l in filings.find_all("tr"):
        row = str(l)
        url = str(re.findall(r'href="(.*?)"', row))
        url = str(url)
        url = re.sub("\['",'', re.sub("'\]", '', url))
    
        if url[:4] == "http":
            stamp_date = l.find_all('td',{"headers" : "STAMPED/RECEIVEDDATE"})
            stamp_date = str(stamp_date)[-16:-6]
            stamp_date_obj = datetime.datetime.strptime(stamp_date, "%m/%d/%Y")

            if Document.objects.filter(url = url).exists():
                add_file(url)
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
                    message = "Can't identify form-- " + url
                    logger.error(message)

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
                add_file(url)
                new_fara_docs.append(url_info)
                
                   
    return new_fara_docs

class Command(BaseCommand):
    help = "Crawls the DOJ's FARA site looking for new documents."
    can_import_settings = True
        
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

        start_date = datetime.date.today() - datetime.timedelta(days=25)
        end_date = datetime.date.today()

        data += [('p_t01', 'ALL'),
                 ('p_t02', 'ALL'),
                 ('p_t06', start_date.strftime('%m/%d/%Y')),
                 ('p_t07', end_date.strftime('%m/%d/%Y')),
                 ('p_request', 'SEARCH'),
        ]
    
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
            next_url = 'https://efile.fara.gov/pls/apex' + url_end
            
            req = urllib2.Request(next_url)
            page = urllib2.urlopen(req).read()
            page = BeautifulSoup(page)
            new_info = parse_and_save(page)
            
            url_end = page.findAll("a", {"class":"t14pagination"})
            
            if len(url_end) > 1:
                url_end = url_end[1]
            else: 
                break
            
            new_info = parse_and_save(url_end)

          



