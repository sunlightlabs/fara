import csv
import datetime

#maybe move the files to s3 later?
#from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError


from FaraData.models import Contact, MetaData
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


def big_bad_contacts():
	filename = "data/contacts-condensed" + str(datetime.date.today()) + ".csv"
	# filter out old files
	docs = Document.objects.filter(processed=True, doc_type="Supplemental",stamp_date__range=(datetime.date(2012,1,1), datetime.date.today()))
	# combined contact sheet
	writer = csv.writer(open(filename, 'wb'))
	writer.writerow(['Date', 'Contact', 'Client', 'Registrant', 'Description', 'Type', 'Employees mentioned', 'Source', 'Record ID'])
	# one line per contact sheet
	filename = "data/contacts-by-contact" + str(datetime.date.today()) + ".csv"
	writer2 = csv.writer(open(filename, 'wb'))
	writer2.writerow(['Date', 'Contact Title','Contact Name', 'Contact Office', 'Contact Agency', 'Client', 'Registrant', 'Description', 'Type', 'Employees mentioned', 'Source', 'Affiliated Member CRP ID', 'Contact ID', 'Record ID'])

	for d in docs:
		url = d.url
		md = MetaData.objects.get(link=url)
		end_date = md.end_date
		if md.end_date == None:
			if md.notes == "legacy":
				end_date = None

		info = {
			"url": url,
			"contacts": Contact.objects.filter(link=url),
			"md": md,
			"dumb_date": end_date,
			"writer": writer,
			"writer2": writer2,
		}

		find_contacts(info)
		

def find_contacts(info):
	contacts = info['contacts']
	url = info['url']
	md = info['md']
	dumb_date = info['dumb_date']
	writer = info['writer']
	writer2 = info['writer2']
	
	for c in contacts:
		lobbyists = ''
		for l in c.lobbyist.all():
			lobbyists = lobbyists + l.lobbyist_name + ", "
		lobbyists = lobbyists.encode('ascii', errors='ignore')
		#recipients = []
		contact_name = ''
		for r in c.recipient.all():
			contact_name = contact_name + namebuilder(r)
		
		if c.date == None:
			try:
				date = dumb_date.strftime('%x') + "*"
			except:
				# this is bad, it means a missing date
				date = "*"
		else:
			date = c.date
		
		if c.description == None:
			description = None
		else:
			description = c.description.encode('ascii', errors='ignore')

		c_type = {"M": "meeting", "U":"unknown", "P":"phone", "O": "other", "E": "email"}
		
		writer.writerow([date, contact_name, c.client, c.registrant, description, c_type[c.contact_type], lobbyists, c.link, c.id])

		for r in c.recipient.all():
			if r.title != None and r.title != '':	
				contact_title = r.title.encode('ascii', errors='ignore')	
			else:
				contact_title = ''
			
			if r.name != None and r.name != '':
				contact_name = r.name.encode('ascii', errors='ignore')
				if contact_name == "unknown; ":
					contact_name = ''
			else:
				contact_name = ''
			
			if r.office_detail != None and r.office_detail != '':
				contact_office = r.office_detail.encode('ascii', errors='ignore')
			else:
				contact_office = ''
			if r. agency != None and r.agency != '':
				contact_agency = r.agency.encode('ascii', errors='ignore')
			else:
				contact_agency = ''
			
			
			writer2.writerow([date, contact_title, contact_name, contact_office, contact_agency, c.client, c.registrant, description, c_type[c.contact_type], lobbyists, c.link, r.crp_id, r.id, c.id])


class Command(BaseCommand):
    help = "Creates mega contact download"
    can_import_settings = True
        
    def handle(self, *args, **options):
    	return big_bad_contacts()
