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
			# payment.save()
		print problems
	





