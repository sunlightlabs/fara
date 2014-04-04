import re
import datetime

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
					url = md.link
					reg_id = re.sub('-','', url[25:29])
					reg_id = re.sub('S','', reg_id)
					reg_id = re.sub('L','', reg_id)

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
						print info[0]

					stamp_date = re.findall(r'\d{8}', url)
					stamp_date = stamp_date[0]
					stamp_date_obj = datetime.datetime.strptime(stamp_date, "%Y%m%d")


					document = Document(
						url = url,
					    reg_id = reg_id,
					    doc_type = doc_type,
					    stamp_date = stamp_date_obj,
					    processed = md.processed,
					)
					#document.save()
					print md.notes