from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

from FaraData.models import Payment, MetaData 
from fara_feed.models import Document

payments = Payment.objects.all()

for payment in payments:
	md = MetaData.objects.get(link=payment.link)
	if payment.date is not None:
		payment.sort_date = payment.date
	elif md.end_date is not None:
		payment.sort_date = md.end_date
	else:
		doc = Document.objects.get(url=payment.link)
		payment.sort_date = doc.stamp_date
	print payment.sort_date
	# payment.save()





