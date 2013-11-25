import urllib
import urllib2
import logging

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

from fara_feed.models import *

logging.basicConfig()
logger = logging.getLogger(__name__)


def add_file(url, record_id):
	if url[:25] != "http://www.fara.gov/docs/" or len(url) < 25:
		message = 'bad link ' + url
		logger.error(message)

	else:
		file_name = url[25:]
		doc = Document.objects.get(id=record_id)
		if not default_storage.exists(file_name):
			try:
				url = str(url)
				u = urllib2.urlopen(url)
				localFile = default_storage.open(file_name, 'w')
				localFile.write(u.read())
				localFile.close()
				if doc.uploaded != True:
					doc.uploaded = True
					doc.save()

			except:
				message = 'bad upload ' + url
				logger.error(message)
				if doc.uploaded != False:
					doc.uploaded = False
					doc.save()
		else:
			if doc.uploaded != True:
				doc.uploaded = True
				doc.save()


class Command(BaseCommand):
	def handle(self, pythonpath, verbosity, traceback, settings):
		for doc in Document.objects.all():
			try:
				if doc.url:
					add_file(doc.url, doc.id)
				else: 
					message = "bad record"
					if doc.uploaded != False:
						doc.uploaded = False
						doc.save()
					logger.error(message)
			except:
				print "wtf"
