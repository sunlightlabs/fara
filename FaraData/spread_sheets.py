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

from FaraData.unicode_csv import UnicodeWriter
from fara_feed.models import Document
from FaraData.models import Contact, Payment, Registrant, Contribution, Disbursement, MetaData
from django.conf import settings

#from django.db import connection

logging.basicConfig()
logger = logging.getLogger(__name__)

# HEADINGS
contact_heading = ['Date', 'Contact Title','Contact Name', 'Contact Office', 'Contact Agency', 'Client', 'Client Location', 'Registrant', 'Description', 'Type', 'Employees Mentioned', 'Affiliated Member Bioguide ID', 'Source', 'Document ID', 'Registrant ID', 'Client ID', 'Location ID', 'Recipient ID', 'Record ID']
contribution_heading = ['Date', 'Amount', 'Recipient', 'Registrant', 'Contributing Individual or PAC', 'CRP ID of Recipient', 'Bioguide ID', 'Source', 'Document ID', 'Registrant ID', 'Recipient ID', 'Record ID']
payment_heading = ['Date', 'Amount', 'Client', 'Registrant', 'Purpose', 'From subcontractor', 'Source', 'Document ID', 'Registrant ID', 'Client ID','Location ID', 'Subcontractor ID', 'Record ID']
disbursement_heading = ['Date', 'Amount', 'Client', 'Registrant', 'Purpose', 'To Subcontractor', 'Source', 'Document ID', 'Registrant ID', 'Client ID','Location ID', 'Subcontractor ID', 'Record ID']
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
		writer = UnicodeWriter(contact_file)
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
		writer = UnicodeWriter(open(filename, 'wb'))
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
		writer = UnicodeWriter(open(filename, 'wb'))
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
		writer = UnicodeWriter(open(filename, 'wb'))
		writer.writerow(disbursement_heading)
		disbursements_sheet(disbursements, writer)
		return filename
	else: return None

def contact_sheet(contacts, writer):
	print 'starting contacts'
	c_type = {"M": "meeting", "U":"unknown", "P":"phone", "O": "other", "E": "email"}
	for c in contacts:
		print "starting loop"
		lobbyists = ''
		for l in c.lobbyist.all():
			lobbyists = lobbyists + l.lobbyist_name + ", "
		lobbyists = lobbyists

		if c.date == None:
			date = str(c.meta_data.end_date) + '*'
		else:
			date = c.date

		for r in c.recipient.all():

			if r.name != None:
				contact_name = r.name
				if contact_name == "unknown":
					contact_name = ''

			writer.writerow([date, r.title, contact_name, r.office_detail, r.agency, c.client, c.client.location, c.registrant, c.description, c_type[c.contact_type], lobbyists, r.bioguide_id, c.link, c.meta_data.form, c.registrant.reg_id, c.client.id, c.client.location.id, r.id, c.id])


def contributions_sheet(contributions, writer):
	for c in contributions:	
 		recipient_name = namebuilder(c.recipient)
 		if c.lobbyist:
 			lobby = c.lobbyist
 		else:
 			lobby = ''
 		if c.date == None:
			date = str(c.meta_data.end_date) + '*'
		else:
			date = c.date

		writer.writerow([date, c.amount, recipient_name, c.registrant, lobby, c.recipient.crp_id, c.recipient.bioguide_id, c.link, c.meta_data.form, c.registrant.reg_id, c.recipient.id, c.id])

	
def payments_sheet(payments, writer):
	for p in payments:
		if p.date == None:
			date = str(p.meta_data.end_date) + '*'
		else:
			date = p.date

		if p.subcontractor:
			subid = p.subcontractor.reg_id
		else:
			subid = ''

		writer.writerow([date, p.amount, p.client, p.registrant, p.purpose , p.subcontractor, p.link, p.meta_data.form, p.registrant.reg_id, p.client.id, p.client.location.id, subid, p.id])


def disbursements_sheet(disbursements, writer):
	for d in disbursements:
		if d.date == None:
			date = str(d.meta_data.end_date) + '*'
		else:
			date = d.date
		
		if d.subcontractor != None:
			subid = d.subcontractor.reg_id
		else:
			subid = ''

		writer.writerow([date, d.amount, d.client, d.registrant, d.purpose, d.subcontractor, d.link, d.meta_data.form, d.registrant.reg_id, d.client.id, d.client.location.id, subid, d.id])

def namebuilder(r):
	contact_name = ''
	if r.title != None and r.title != '':	
		contact_name = r.title
	if r.name != None and r.name != '':
		contact_name = contact_name + r.name
	if r.office_detail != None and r.office_detail != '':
		contact_name = contact_name + ", office: " + r.office_detail
	if r. agency != None and r.agency != '':
		contact_name = contact_name + ", agency: " + r.agency
	contact_name = contact_name + "; "
	if contact_name == "unknown; ":
		contact_name = ''
	return contact_name

def client_registrant(writer):
	writer.writerow(client_reg_heading)
	for reg in Registrant.objects.all():
		for c in reg.clients.all():
			client_name = c.client_name
			reg_name = reg.reg_name
			try:	
				client_reg = ClientReg.objects.get(client_id=client,registrant_id=registrant)
				description = client_reg.description
			except:
				description = ''
			writer.writerow([client_name, reg_name, "Active", c.location.location, description, reg.reg_id, c.id])
		for client in reg.terminated_clients.all():
			client_name = client.client_name
			reg_name = reg.reg_name
			client_loc = client.location.location
			try:	
				client_reg = ClientReg.objects.get(client_id=client,registrant_id=registrant)
				description = client_reg.description
			except:
				description = ''

			writer.writerow([client_name, reg_name, "Terminated", client_loc, description, reg.reg_id, client.id, client.location.id])
