import csv
import datetime

from django.core.management.base import BaseCommand, CommandError

from FaraData.models import Payment, MetaData, Contact
from fara_feed.models import *


class Command(BaseCommand):
    help = "Creates custom download"
    can_import_settings = True
        
    def handle(self, *args, **options):
    	custom = get_request()
    	contacts(custom)
    	return payments(custom)


def get_request():
	custom = []
	reg_file = csv.reader(open("FaraData/management/commands/reg_list.csv","rU"), dialect=csv.excel_tab)
	for reg in reg_file:
		custom.append(reg[0])
	return custom

def payments(custom):
	filename = "data/custom-payments" + str(datetime.date.today()) + ".csv"
	# filtering archival information for now
	docs = Document.objects.filter(reg_id__in=custom, processed=True, doc_type__in=["Supplemental", "Amendment", "Registration"],stamp_date__range=(datetime.date(2012,1,1), datetime.date.today()))
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

	for p in payments:
		if p.date == None:
			try:
				date = dumb_date.strftime('%x') + "*"
			except:
				date = "*"
		else:
			date = p.date
		
		if p.purpose == None:
			purpose = None
		else:
			purpose = p.purpose.encode('ascii', errors='ignore')
		
		writer.writerow([p.client, p.amount, date, p.registrant, purpose , p.subcontractor, p.link])


 #########
 
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


def contacts(custom):
	docs = Document.objects.filter(processed=True, doc_type__in=["Supplemental", "Amendment", "Registration"], stamp_date__range=(datetime.date(2013,1,1), datetime.date.today()))
	# combined contact sheet
	filename = "data/custom-contacts" + str(datetime.date.today()) + ".csv"
	writer2 = csv.writer(open(filename, 'wb'))
	writer2.writerow(['Date', 'Contact Title','Contact Name', 'Contact Office', 'Contact Agency', 'Client', 'Client Location', 'Registrant', 'Description', 'Type', 'Employees mentioned', 'Affiliated Member CRP ID', 'Affiliated Member Bioguide ID', 'Source', 'Contact ID', 'Record ID'])

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
			"writer2": writer2,
		}

		find_contacts(info)
		

def find_contacts(info):
	contacts = info['contacts']
	url = info['url']
	md = info['md']
	dumb_date = info['dumb_date']
	writer2 = info['writer2']
	
	for c in contacts:
		lobbyists = ''
		for l in c.lobbyist.all():
			lobbyists = lobbyists + l.lobbyist_name + ", "
		lobbyists = lobbyists.encode('ascii', errors='ignore')
		contact_name = ''
		for r in c.recipient.all():
			contact_name = contact_name + namebuilder(r)
		
		if c.date == None:
			try:
				date = dumb_date.strftime('%x') + "*"
			except:
				# missing date
				date = "*"
		else:
			date = c.date
		
		if c.description == None:
			description = None
		else:
			description = c.description.encode('ascii', errors='ignore')

		c_type = {"M": "meeting", "U":"unknown", "P":"phone", "O": "other", "E": "email"}
		
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
			
			
			writer2.writerow([date, contact_title, contact_name, contact_office, contact_agency, c.client, c.client.location, c.registrant, description, c_type[c.contact_type], lobbyists, r.crp_id, r.bioguide_id, c.link, r.id, c.id])




