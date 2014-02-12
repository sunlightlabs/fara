
import urllib2
import logging

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

from arms_sales.models import Proposed

logging.basicConfig()
logger = logging.getLogger(__name__)

class Command(BaseCommand):
	def handle(self, *args, **options):
		for proposal in Proposed.objects.all():
			try:
				file_name = "arms_pdf/" + str(proposal.id) + ".pdf"
				pdf_link = proposal.pdf_url
				pdf_link = str(pdf_link)
				u = urllib2.urlopen(pdf_link)
				localFile = default_storage.open(file_name, 'w')
				localFile.write(u.read())
				localFile.close() 

			except:
				print 'not working'
				title = proposal.title
				message = 'bad upload ' + title
				logger.error(message)