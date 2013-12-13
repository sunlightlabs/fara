import csv
import datetime

#maybe move the files to s3 later?
#from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError


from FaraData.models import Contribution, MetaData
from fara_feed.models import *


def namebuilder(r):
	contact_name = ''
	if r.title != None and r.title != '':	
		contact_name = r.title.encode('ascii', errors='ignore') + ' '
	if r.name != None and r.name != '':
		contact_name = contact_name + r.name.encode('ascii', errors='ignore')
	if r.office_detail != None and r.office_detail != '':
		contact_name = contact_name + ", office: " + r.office_detail.encode('ascii', errors='ignore')
	if r. agency != None and r.agency != '':
		contact_name = contact_name + ", agency: " + r.agency.encode('ascii', errors='ignore')
	contact_name = contact_name.encode('ascii', errors='ignore') + "; "
	if contact_name == "unknown; ":
		contact_name = ''
	return contact_name

def big_bad_contributions():
	filename = "data/contributions" + str(datetime.date.today()) + ".csv"
	# filtering archival information for now
	docs = Document.objects.filter(processed=True, doc_type="Supplemental",stamp_date__range=(datetime.date(2012,1,1), datetime.date.today()))
	writer = csv.writer(open(filename, 'wb'))
	writer.writerow(['Amount', 'Date', 'Recipient', 'Registrant', 'Contributing Lobbyist or PAC', 'Source', 'Record ID'])

	for d in docs:
		url = d.url
		find_contributions(url, writer)

def find_contributions(url, writer):
	md = MetaData.objects.get(link=url)
	end_date = md.end_date
	dumb_date = end_date
	if md.end_date == None:
		if md.notes == "legacy":
			end_date = None


	contribution = Contribution.objects.filter(link=url)

	for c in contribution:	
 		recipient_name = namebuilder(c.recipient)
 		if c.lobbyist:
 			lobby = c.lobbyist
 		else:
 			lobby = ''
 		if c.date == None:
			try:
				date = dumb_date.strftime('%x') + "*"
			except:
				date = "*"
		else:
			date = c.date

		writer.writerow([c.amount, date, recipient_name, c.registrant, lobby, c.link, c.id])


class Command(BaseCommand):
    help = "Creates mega contribution download"
    can_import_settings = True
        
    def handle(self, *args, **options):
    	return big_bad_contributions()