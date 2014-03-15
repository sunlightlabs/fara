from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

from FaraData.models import Payment, MetaData

payments = Payment.objects.all()

for payment in payments:
	if payment.date is not None:
		payment.sort_date = payment.date
	else:
		md = MetaData.objects.get(link=payment.link)
		payment.sort_date = md.end_date
	print payment.sort_date
	# payment.save()





