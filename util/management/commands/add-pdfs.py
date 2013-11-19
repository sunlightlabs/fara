import urllib
import urllib2
import logging

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

from fara_feed.models import *

logging.basicConfig()
logger = logging.getLogger(__name__)


def add_file(url):
	if url[:25] != "http://www.fara.gov/docs/":
		message = 'bad link ' + url
		logger.error(message)

	else:
		file_name = url[25:]
		if not default_storage.exists(file_name):
			try:
			    url = str(url)
			    u = urllib2.urlopen(url)
			    localFile = default_storage.open(file_name, 'w')
			    localFile.write(u.read())
			    localFile.close()
			    print "saved", file_name
			except:
				message = 'bad upload ' + url
				logger.error(message)
		else:
			print "found it", file_name

class Command(BaseCommand):
	for doc in Document.objects.all():
		add_file(doc.url)