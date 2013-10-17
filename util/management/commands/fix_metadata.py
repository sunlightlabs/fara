# It passed the test, the extra meta data records were not being used!

from django.core.management.base import BaseCommand, CommandError

from FaraData.models import *
from fara_feed.models import *

# I did not change some old urls when first uploading so I am making sure the bad MetaData is not attached to any information
class Command(BaseCommand):
	def handle(self, pythonpath, verbosity, traceback, settings):
		def find_bad_links(category):

			obj = category.objects.all()
			for o in obj:
				link = o.link
				if link[24:36] == "/to_reimport":
					print "to reimport", o.id
				elif link[:24] == "download_cache/processed":
					print "processed", o.id
				elif link[:8] == 'download':
					print "download", o.id
			print "done", category
				
		find_bad_links(Contribution)
		find_bad_links(Contact)
		find_bad_links(Payment)
		find_bad_links(Disbursement)
			
		# objects = MetaData.objects.all()
		# for o in objects:
		# 	link = str(o.link)
		# 	if link[24:36] == "/to_reimport":
		# 		link= link[36:-4] 
		# 		link = "http://www.fara.gov/docs" + link + ".pdf"
		# 		print link
		# 		o.link = link
		# 		if MetaData.objects.filter(link=link).exists():
		# 			print "DUPE---", o.link
		# 		else:
		# 			o.save()
		# 			print "fixing"

		# 	elif link[:24] == "download_cache/processed":
		# 		link = link[25:-4]
		# 		link = "http://www.fara.gov/docs/" + link + ".pdf"
		# 		print link
		# 		if MetaData.objects.filter(link=link).exists():
		# 			print "DUPE---", o.link
		# 		else:
		# 			o.save()
		# 			print "fixing"

		# 	elif link[:8] == 'download':
		# 		link = link[15:-4]
		# 		link = "http://www.fara.gov/docs/" + link + ".pdf"
		# 		print link
		# 		if MetaData.objects.filter(link=link).exists():
		# 			print "DUPE---", o.link
		# 		else:
		# 			o.save()
		# 			print "fixing"

	

