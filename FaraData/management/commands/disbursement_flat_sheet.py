import csv
import datetime

#maybe move the files to s3 later?
#from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError

from FaraData.models import Disbursement, MetaData
from fara_feed.models import *

def find_disbursements(url, writer):
	disbursement = Disbursement.objects.filter(link=url)
	md = MetaData.objects.get(link=url)
	dumb_date = md.end_date

	for d in disbursement:
		if d.date == None:
			try:
				date = dumb_date.strftime('%x') + '*'
				print date
			except:
				date = '*'
		else:
			date = d.date
		
		writer.writerow([d.amount, date, d.client.encode('ascii', errors='ignore'), d.registrant.encode('ascii', errors='ignore'), d.purpose.encode('ascii', errors='ignore'), d.subcontractor.encode('ascii', errors='ignore'), d.link, d.id])


def big_bad_disbursements():
	filename = "data/disbursements" + str(datetime.date.today()) + ".csv"
	# filtering archival information for now
	docs = Document.objects.filter(processed=True, doc_type="Supplemental",stamp_date__range=(datetime.date(2010,1,1), datetime.date.today()))
	writer = csv.writer(open(filename, 'wb'))
	writer.writerow(['Amount', 'Date','Client', 'Registrant', 'Purpose', 'To Subcontractor', 'Source', 'Record ID'])

	for d in docs:
		url = d.url
		find_disbursements(url, writer)


class Command(BaseCommand):
    help = "Creates mega disbursement download"
    can_import_settings = True
        
    def handle(self, *args, **options):
    	return big_bad_disbursements()