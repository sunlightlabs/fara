# pass in instance(s) of documents to make a spreadsheet

import csv
import datetime
import tempfile
import sys
import os
import zipfile
from StringIO import StringIO

from django.core.files.storage import default_storage

from FaraData.models import *
from fara_feed.models import *


# makes a file package per form 
def make_file(form_id):
	form = Document.objects.get(id=form_id)
	contacts = make_contacts([form])
	print "contacts"
	payments = make_payments([form])
	print "payments"
	contributions = make_contributions([form])
	print "contrib"
	disbursements = make_disbursements([form])
	print "dis"
	sheets = {"contacts.csv":contacts, "payments.csv":payments, "contributions.csv":contributions, "disbursements.csv":disbursements}
	if not (contacts == None and payments == None and contributions == None and disbursements == None):
		print "saving a zipped file of sheets"
		name = "form_" + form + ".zip"
		form_file = zipfile.ZipFile(name, 'w')
		for sheet in sheets.keys():
			print sheet
			if sheet is not None:
				form_file.write

		print "saving to amazon" 
		bucket_file = default_storage.open(file_name, 'w')
		bucket_file.write(form_file.read())
		bucket_file.close()
		form_file.close()
	# removing tmp
	

def make_contacts(docs):
	links = []
	for d in docs:
		if d.processed == True:
			links.append(d.url)
	contacts = Contact.objects.filter(link__in=links) 
	if len(contacts) >= 1:
		filename = "tmp/contacts.csv"
		writer = csv.writer(open(filename, 'wb'))
		writer.writerow(['Date', 'Contact Title','Contact Name', 'Contact Office', 'Contact Agency', 'Client', 'Client Location', 'Registrant', 'Description', 'Type', 'Employees mentioned', 'Affiliated Member CRP ID', 'Affiliated Member Bioguide ID', 'Source', 'Contact ID', 'Record ID'])
		contact_file = contact_sheet(contacts, writer)
		print "PLEASE WORK"
		return contact_file
	else: return None

def make_contributions(docs):
	links = []
	for d in docs:
		if d.processed == True:
			links.append(d.url)
	contributions = Contribution.objects.filter(link__in=links) 
		
	if len(contributions) >=1:
		filename = "tmp/contributions.csv"
		writer = csv.writer(open(filename, 'wb'))
		writer.writerow(['Date', 'Amount', 'Recipient', 'Registrant', 'Contributing Lobbyist or PAC', 'CRP ID of Recipient', 'Bioguide ID', 'Source', 'Record ID'])
		contributions_file = contributions_sheet(contributions, writer)
		return contributions_file
	else: return None

def make_payments(docs):
	links = []
	for d in docs:
		if d.processed == True:
			links.append(d.url)
	payments = Payment.objects.filter(link__in=links)

	if len(payments) >=1:
		filename = "tmp/payments.csv"
		writer = csv.writer(open(filename, 'wb'))
		writer.writerow(['Client', 'Amount', 'Date', 'Registrant', 'Purpose', 'From subcontractor', 'Source'])
		payments_file = payments_sheet(payments, writer)
		return payments_file
	else: return None

def make_disbursements(docs):
	links = []
	for d in docs:
		if d.processed == True:
			links.append(d.url)
	disbursements = Disbursement.objects.filter(link__in=links)

	if len(disbursements) >=1:
		filename = "tmp/disbursements.csv"
		writer = csv.writer(open(filename, 'wb'))
		writer.writerow(['Amount', 'Date','Client', 'Registrant', 'Purpose', 'To Subcontractor', 'Source', 'Record ID'])
		disbursements_file = disbursements_sheet(disbursements, writer)
		return disbursements_file
	else: return None

def contact_sheet(contacts, writer):
	for c in contacts:
		
		lobbyists = ''
		for l in c.lobbyist.all():
			lobbyists = lobbyists + l.lobbyist_name + ", "
		lobbyists = lobbyists.encode('ascii', errors='ignore')
		
		if c.date == None:
			if MetaData.objects.get(link=c.link):
				md = MetaData.objects.get(link=c.link)
				end_date = md.end_date
				dumb_date = end_date	
			else:
				end_date == ''
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
				if contact_name == "unknown":
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
			
			writer.writerow([date, contact_title, contact_name, contact_office, contact_agency, c.client, c.client.location, c.registrant, description, c_type[c.contact_type], lobbyists, r.crp_id, r.bioguide_id, c.link, r.id, c.id])


def contributions_sheet(contributions, writer):
	for c in contributions:	
 		recipient_name = namebuilder(c.recipient)
 		if c.lobbyist:
 			lobby = c.lobbyist
 		else:
 			lobby = ''
 		if c.date == None:
			md = MetaData.objects.get(link=url)
			end_date = md.end_date
			dumb_date = end_date
			if md.end_date == None:
				end_date == None
		else:
			date = c.date

		writer.writerow([date, c.amount, recipient_name, c.registrant, lobby, c.recipient.crp_id, c.recipient.bioguide_id, c.link, c.id])

	
def payments_sheet(payments, writer):
	for p in payments:
		date = p.date
		if p.date == None or p.date == '':
			if MetaData.objects.get(link=p.link):
				md = MetaData.objects.get(link=p.link)
				end_date = md.end_date
				date = end_date	
			else:
				date == ''
		
		if p.purpose == None:
			purpose = None
		else:
			purpose = p.purpose.encode('ascii', errors='ignore')
		
		writer.writerow([p.client, p.amount, date, p.registrant, purpose , p.subcontractor, p.link])


def disbursements_sheet(disbursements, writer):
	for d in disbursements:
		date = d.date
		if d.date == None or d.date == '':
			if MetaData.objects.get(link=d.link):
				md = MetaData.objects.get(link=d.link)
				end_date = md.end_date
				date = end_date	
			else:
				date == ''
		
		if d.purpose == None:
			purpose = None
		else:
			purpose = d.purpose.encode('ascii', errors='ignore')

		writer.writerow([d.amount, date, d.client, d.registrant, purpose, d.subcontractor, d.link, d.id])

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