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
			try:
				md = MetaData.objects.get(link=payment.link)
				date = md.end_date
			except:
				if not Document.objects.filter(url=payment.link).exists():
					problems.append(payment.link)
				else:
					doc = Document.objects.get(url=payment.link)
					date = doc.stamp_date

			if payment.date is not None:
				payment.sort_date = payment.date
			else:
				payment.sort_date = date

			if payment.sort_date == None:
				url = payment.link
				stamp_date = re.findall(r'\d{8}', url)
                stamp_date = stamp_date[0]
                stamp_date_obj = datetime.datetime.strptime(stamp_date, "%Y%m%d")
                print stamp_date
			# payment.save()
		print problems
	





