import csv
import datetime

#maybe move the files to s3 later?
#from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from FaraData.models import Payment, MetaData
from fara_feed.models import *


def big_bad_payments():
	filename = "data/payments" + str(datetime.date.today()) + ".csv"
	# filtering archival information for now
	docs = Document.objects.filter(processed=True, doc_type="Supplemental",stamp_date__range=(datetime.date(2010,1,1), datetime.date.today()))
	writer = csv.writer(open(filename, 'wb'))
	writer.writerow(['Client', 'Amount', 'Date', 'Registrant', 'Purpose', 'From subcontractor', 'Source'])
	
	for d in docs:
		url = d.url
		find_payments(url, writer)
	

def find_payments(url, writer):
	payments = Payment.objects.filter(link=url)
	md = MetaData.objects.get(link=url)
	end_date = md.end_date
	dumb_date = end_date
	if md.end_date == None:
		if md.notes == "legacy":
			end_date = None
		else:
			print url

	for p in payments:
		if p.date == None:
			try:
				date = dumb_date.strftime('%x') + "*"
			except:
				date = "*"
		else:
			date = p.date
		
		writer.writerow([p.client, p.amount, date, p.registrant, p.purpose, p.subcontractor, p.link])

class Command(BaseCommand):
    help = "Creates mega payment download"
    can_import_settings = True
        
    def handle(self, *args, **options):
    	return big_bad_payments()