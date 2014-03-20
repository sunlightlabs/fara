# pass in instance(s) of documents to make a spreadsheet

import csv
import datetime
import sys
import os
import zipfile
import logging
import time

from tempfile import TemporaryFile

from django.core.files.storage import default_storage

from fara_feed.models import Document
from FaraData.models import Contact, Payment, Registrant, Contribution, Disbursement, MetaData
from django.conf import settings

#from django.db import connection

logging.basicConfig()
logger = logging.getLogger(__name__)

# HEADINGS
contact_heading = ['Date', 'Contact Title','Contact Name', 'Contact Office', 'Contact Agency', 'Client', 'Client Location', 'Registrant', 'Description', 'Type', 'Employees Mentioned', 'Affiliated Member Bioguide ID', 'Source','Registrant ID', 'Client ID', 'Location ID', 'Recipient ID', 'Record ID']
contribution_heading = ['Date', 'Amount', 'Recipient', 'Registrant', 'Contributing Individual or PAC', 'CRP ID of Recipient', 'Bioguide ID', 'Source', 'Registrant ID', 'Recipient ID', 'Record ID']
payment_heading = ['Date', 'Amount', 'Client', 'Registrant', 'Purpose', 'From subcontractor', 'Source', 'Registrant ID', 'Client ID','Location ID', 'Subcontractor ID', 'Record ID']
disbursement_heading = ['Date', 'Amount', 'Client', 'Registrant', 'Purpose', 'To Subcontractor', 'Source','Registrant ID', 'Client ID','Location ID', 'Subcontractor ID', 'Record ID']
client_reg_heading = ['Client', 'Registrant name', 'Terminated', 'Location of Client', 'Description of service (when available)', 'Registrant ID', 'Client ID', 'Location ID']

# makes a file package per form 
def make_file(form_id):
	if not os.path.exists("forms"):
		os.mkdir("forms")
		
	form = Document.objects.get(id=form_id)
	contacts = make_contacts([form])
	payments = make_payments([form])
	contributions = make_contributions([form])
	disbursements = make_disbursements([form])
	
	read_text = open(settings.BASE_DIR + '/forms/README.txt', 'r').read()
	date_message = "\nThis record was created on %s" % (datetime.date.today().strftime('%m/%d/%Y'))
	full_read_text = read_text + date_message
	readme = open("README.txt", 'wb')
	readme.write(full_read_text)


	readme = str(readme) + str(date_message)
	
	name = "forms/form_%s.zip" % form_id 
	if disbursements or contacts or contributions or payments:
		with zipfile.ZipFile(name, 'w') as form_file:
			form_file.write("README.txt")
			if disbursements != None: form_file.write(disbursements)	
			if contacts != None: form_file.write(contacts)
			if contributions != None: form_file.write(contributions)
			if payments != None: form_file.write(payments)


		#print "PRTEND saving to amazon" 
		bucket_file = default_storage.open('/spreadsheets/' + name, 'w')
		bucket_file.write(open(name).read())
		bucket_file.close()
		os.remove(name)

	if disbursements: os.remove(disbursements)	
	if contacts: os.remove(contacts)
	if contributions: os.remove(contributions)
	if payments: os.remove(payments)


def make_contacts(docs):
	links = []
	for d in docs:
		if d.processed == True:
			links.append(d.url)
	contacts = Contact.objects.filter(link__in=links) 

	if len(contacts) >= 1:
		filename = "contacts.csv"
		contact_file = open(filename, 'wb')
		writer = csv.writer(contact_file)
		writer.writerow(contact_heading)
		contact_sheet(contacts, writer)
		return filename
	else: return None

def make_contributions(docs):
	links = []
	for d in docs:
		if d.processed == True:
			links.append(d.url)
	contributions = Contribution.objects.filter(link__in=links) 
		
	if len(contributions) >=1:
		filename = "contributions.csv"
		writer = csv.writer(open(filename, 'wb'))
		writer.writerow(contribution_heading)
		contributions_sheet(contributions, writer)
		return filename
	else: return None

def make_payments(docs):
	links = []
	for d in docs:
		if d.processed == True:
			links.append(d.url)
	payments = Payment.objects.filter(link__in=links)

	if len(payments) >=1:
		filename = "payments.csv"
		writer = csv.writer(open(filename, 'wb'))
		writer.writerow(payment_heading)
		payments_sheet(payments, writer)
		return filename
	else: return None

def make_disbursements(docs):
	links = []
	for d in docs:
		if d.processed == True:
			links.append(d.url)
	disbursements = Disbursement.objects.filter(link__in=links)

	if len(disbursements) >=1:
		filename = "disbursements.csv"
		writer = csv.writer(open(filename, 'wb'))
		writer.writerow(disbursement_heading)
		disbursements_sheet(disbursements, writer)
		return filename
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
				date = end_date	
			else:
				date == ''
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

			writer.writerow([date, contact_title, contact_name, contact_office, contact_agency, c.client, c.client.location, c.registrant, description, c_type[c.contact_type], lobbyists, r.bioguide_id, c.link, c.registrant.reg_id, c.client.id, c.client.location.id, r.id, c.id])


def contributions_sheet(contributions, writer):
	for c in contributions:	
 		recipient_name = namebuilder(c.recipient)
 		if c.lobbyist:
 			lobby = c.lobbyist
 		else:
 			lobby = ''
 		if c.date == None:
			md = MetaData.objects.get(link=c.link)
			end_date = md.end_date
			date = end_date

		else:
			date = c.date

		writer.writerow([date, c.amount, recipient_name, c.registrant, lobby, c.recipient.crp_id, c.recipient.bioguide_id, c.link, c.registrant.reg_id, c.recipient.id, c.id])

	
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

		writer.writerow([date, p.amount, p.client, p.registrant, purpose , p.subcontractor, p.link, p.registrant.reg_id, p.client.id, p.client.location.id, p.subcontractor.reg_id, p.id])


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

		writer.writerow([date, d.amount, d.client, d.registrant, purpose, d.subcontractor, d.link, d.registrant.reg_id, d.client.id, d.location.id, d.subcontractor.id, d.id])

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

def client_registrant(writer):
	for reg in Registrant.objects.all():
		for client in reg.clients.all():
			print client
			client_name = client.client_name
			reg_name = reg.reg_name
			client_loc = client.location.location
			try:	
				client_reg = ClientReg.objects.get(client_id=client,registrant_id=registrant)
				discription = client_reg.description
			except:
				discription = ''

			writer.writerow([client_name, reg_name, "Active". client_loc, discription, reg.reg_id, client.id])
		for client in reg.terminated_clients.all():
			print client
			client_name = client.client_name
			reg_name = reg.reg_name
			client_loc = client.location.location
			try:	
				client_reg = ClientReg.objects.get(client_id=client,registrant_id=registrant)
				discription = client_reg.description
			except:
				discription = ''

			writer.writerow([client_name, reg_name, "Terminated", client_loc, discription, reg.reg_id, client.id, client.location.id])
