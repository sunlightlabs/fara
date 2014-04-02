# one_ring_for_files
import os
from elasticsearch import Elasticsearch
from PyPDF2 import PdfFileReader

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from django.conf import settings 

from fara_feed.management.commands.create_feed import add_file
from fara_feed.models import Document
from FaraData.models import Registrant

es = Elasticsearch(**settings.ES_CONFIG)


class Command(BaseCommand):
	help = "Puts all the data into elastic search, checks that there is a PDF, and saves a copy to disk."
	can_import_settings = True

	def handle(self, *args, **options):
		for document in Document.objects.all():
			text = extract_text(document.url)
			load_fara_text(text, document)
			save_on_disk(text, document.url)


def extract_text(link):
	print 'text extraction'
	amazon_file_name = "pdfs/" + link[25:]
	if not default_storage.exists(amazon_file_name):
		try:
			add_file(link)
		except:
			return ''

	pdf = default_storage.open(amazon_file_name, 'rb')

	try:
		pdf_file = PdfFileReader(pdf)
	except:
		print "BAD FILE-- %s " %(link)

	pages = pdf_file.getNumPages()
	count = 0
	text = ''
	while count < pages:
		pg = pdf_file.getPage(count)
		pgtxt = pg.extractText()
		count = count + 1
		text = text + pgtxt

	return text 


def load_fara_text(text, document):
	print 'es'
	reg_id = document.reg_id
	reg = Registrant.objects.get(reg_id=reg_id)
	reg_name = reg.reg_name
	doc = {
			'type': document.doc_type,
			'date': document.stamp_date,
			'registrant': reg_name,
			'reg_id': reg_id,
			'doc_id': document.id, 
			'link': document.url,
			'text': text,
	}
	
	res = es.index(index="foreign", doc_type='fara_files', id=document.id, body=doc)


def save_on_disk(text, link):
	print 'disk'
	file_name = "data/form_text/" + link[25:-4] + ".txt"
	print file_name
	with open(file_name, 'w') as f:
		f.write(text.encode('utf8'))




