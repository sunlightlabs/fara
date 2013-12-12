import dateutil
import dateutil.parser
from datetime import datetime, date

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from FaraData.models import *
from fara_feed.models import *

default_date = "08/01/2013"
default_date = datetime.strptime(default_date, "%m/%d/%Y")

class Command(BaseCommand):
	def handle(self, pythonpath, verbosity, traceback, settings):
		for m in MetaData.objects.all():
			if m.upload_date == None:
				m.upload_date = default_date
				print m.upload_date

			if m.form == '':
				try:
					doc = Document.objects.get(url=m.link)
					m.form = doc.id
				except:
					m.form_id = add_doc(m.link)

			m.save()
					
def add_doc(url): 
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
	        print(message)


	    stamp_date = re.findall(r'\d{8}', url)
	    stamp_date = stamp_date[0]
	    stamp_date_obj = datetime.strptime(stamp_date, "%Y%m%d")

	    url_info= [url, reg_id, doc_type, stamp_date_obj]
	    #saves url info
	    doc_id = add_document(url_info)
	    add_file(url)

	    return doc_id

def add_document(url_info):
    document = Document(url = url_info[0],
        reg_id = url_info[1],
        doc_type = url_info[2],
        stamp_date = url_info[3],
    )
    document.save()
    return document.id
    
def add_file(url):
    if url[:25] != "http://www.fara.gov/docs/":
        message = 'bad link ' + url
        print(message)
    
    else:
        file_name = "pdfs/" + url[25:]
        if not default_storage.exists(file_name):
            try:
                url = str(url)
                u = urllib2.urlopen(url)
                localFile = default_storage.open(file_name, 'w')
                localFile.write(u.read())
                localFile.close()
                doc = Document.objects.get(url=url)
                doc.uploaded = True
                doc.save()
            except:
                message = 'bad upload ' + url
                print(message)
        else:
            doc = Document.objects.get(url=url)
            if doc.uploaded != True:  
                doc.uploaded = True
                doc.save()
