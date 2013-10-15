from FaraData.models import *
from fara_feed.models import *

class Command(BaseCommand):
	def handle(self):
		obj = Contactsl.objects.all()
		for o in obj:
			if link[24:36] == "/to_reimport":
				print "to reimport"
			elif link[:24] == "download_cache/processed":
				print "processed"
			elif link[:8] == 'download':
				print "download"

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

	

