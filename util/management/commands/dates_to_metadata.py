from django.core.management.base import BaseCommand, CommandError

from fara_feed.models import Document
from FaraData.models import MetaData

class Command(BaseCommand):
	help = "Makes sure we have dates in metadata, I am using stampdate"
	can_import_settings = True

	def handle(self, *args, **options):
		for md in MetaData.objects.all():
			if md.end_date == None or md.end_date == '':
				try:
					Document.objects.get(url=md.link)
					doc = Document.objects.get(url=md.link)
					date = doc.stampdate
				except:
					print "missing document"
