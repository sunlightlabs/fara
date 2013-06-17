from django.core.management.base import BaseCommand, CommandError

from fara_feed.models import Document

class Command(BaseCommand):
	can_import_settings = True
	
	def handle(self, *args, **options):
		from fara_feed.models import Document
		urls = []	
		for l in Document.objects.all():
			if l.url in urls:
				Document.objects.delete(l)
				print "deleted -", l
			if 'L' in str(l.reg_id):
				print "problem is- ", l, l.id
				urls.append(l.url)
