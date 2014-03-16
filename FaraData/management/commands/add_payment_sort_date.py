import re
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

from FaraData.models import Payment, MetaData 
from fara_feed.models import Document

payments = Payment.objects.all()

problems = []
class Command(BaseCommand):
	def handle(self, *args, **options):
		for payment in payments:
			if payment.date is not None:
				payment.sort_date = payment.date
				p = payment.date
			else:
				if MetaData.objects.filter(link=payment.link).exists():
					md = MetaData.objects.get(link=payment.link)
					if md.end_date is not None:
						payment.sort_date = md.end_date
						p = md.end_date
						print p
					else:
						if not Document.objects.filter(url=payment.link).exists():
							problems.append(payment.link)
						else:
							doc = Document.objects.get(url=payment.link)
							payment.sort_date = doc.stamp_date
							p = doc.stamp_date
				else:
					if not Document.objects.filter(url=payment.link).exists():
						problems.append(payment.link)
					else:
						doc = Document.objects.get(url=payment.link)
						payment.sort_date = doc.stamp_date
						p = doc.stamp_date
			if p == None:
			#if payment.sort_date == None:
				url = payment.link
				stamp_date = re.findall(r'\d{8}', url)
				stamp_date = stamp_date[0]
				stamp_date_obj = datetime.datetime.strptime(stamp_date, "%Y%m%d")
				payment.sort_date = stamp_date_obj
				#print url
			#payment.save()
			print payment.sort_date
		print problems
	





