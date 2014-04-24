
import os
from elasticsearch import Elasticsearch
from PyPDF2 import PdfFileReader

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from django.conf import settings 

from FaraData.models import Contact, Payment, Disbursement, Contribution, Client, Location, Registrant, Recipient, Lobbyist, Gift
from fara_feed.models import Document
from arms_sales.models import Proposed
from fara_feed.management.commands.create_feed import add_file


es = Elasticsearch(**settings.ES_CONFIG)

class Command(BaseCommand):
	help = "Puts all the data into elastic search."
	can_import_settings = True

	def handle(self, *args, **options):
		load_clients()
		load_locations()
		load_registrants()
		load_recipients()
		# load_lobby()
		load_arms()
		load_contacts()
		load_payments()
		load_disbursements()
		load_contributions()
		load_gifts()
		load_fara_text()

def load_clients():
	for client in Client.objects.all():
		doc = {
				'name': client.client_name, 
				'location': client.location.location, 
				'country_grouping': client.location.country_grouping,
				'client_description': client.description,
		}
		
		res = es.index(index="foreign", doc_type='client', id=client.id, body=doc)

	res = es.search(index="foreign", doc_type='client', body={"query": {"match_all": {}}})
	print("Got %d Hits:" % res['hits']['total'])
	for hit in res['hits']['hits']:
		print hit

	print '\nloaded clients\n'

def load_locations():
	for location in Location.objects.all():
		doc = {
				'location': location.location,
				'country_grouping': location.country_grouping,
				'region': location.region,
		}

		res = es.index(index="foreign", doc_type='location', id=location.id, body=doc)

	res = es.search(index="foreign", doc_type='location', body={"query": {"match_all": {}}})
	print("Got %d Hits:" % res['hits']['total'])
	for hit in res['hits']['hits']:
		print hit

	print '\nloaded clients\n'

def load_registrants():
	for reg in Registrant.objects.all():
		doc = {
				'name': reg.reg_name,
				'reg_id': reg.reg_id
		}

		res = es.index(index="foreign", doc_type='registrant', id=reg.reg_id, body=doc)

	res = es.search(index="foreign", doc_type='registrant', body={"query": {"match_all": {}}})
	print("Got %d Hits:" % res['hits']['total'])
	for hit in res['hits']['hits']:
		print hit

	print '\nloaded registrants\n'

def load_recipients():
	for recip in Recipient.objects.all():
		doc = {
				'type': 'recipient',
				'bioguide_id': recip.bioguide_id,
				'agency': recip.agency,
				'office': recip.office_detail,
				'name': recip.name,
				'title': recip.title, 
		}

		res = es.index(index="foreign", doc_type='people_org', id=recip.id, body=doc)

	res = es.search(index="foreign", doc_type='people_org', body={"query": {"match_all": {}}})
	print("Got %d Hits:" % res['hits']['total'])
	for hit in res['hits']['hits']:
		print hit

	print '\nloaded recipients\n'

# THIS MIGHT BE COVERED BY INTERACTIONS
# lobbyists and PACs
def load_lobby():
	for lobby in Lobbyist.objects.all():
		# there will only be one
		name = str(lobby.lobbyist_name) + str(lobby.PAC_name)
		regs = Registrant.objects.filter(lobbyists=lobby)
		reg_ids = []
		for reg in regs:
			reg_ids.append(reg.reg_id)
		
		doc = {
				'name': name,
				'reg_ids': reg_ids,
		}

		res = es.index(index="foreign", doc_type='lobby', id=lobby.id, body=doc)

	res = es.search(index="foreign", doc_type='lobby', body={"query": {"match_all": {}}})
	print("Got %d Hits:" % res['hits']['total'])
	for hit in res['hits']['hits']:
		print hit

	print '\nloaded lobbyists\n'

def load_arms():
	for record in Proposed.objects.all():
		doc = {
				'title': record.title,
				'text': record.text,
				'location': record.location,
				'location_id': record.location_id,
				'date': record.date,
		}

		res = es.index(index="foreign", doc_type='arms', id=record.id, body=doc)

	res = es.search(index="foreign", doc_type='arms', body={"query": {"match_all": {}}})
	print("Got %d Hits:" % res['hits']['total'])
	for hit in res['hits']['hits']:
		print hit

	print '\nloaded arms\n'

def load_contacts():
	for contact in Contact.objects.all():
		document = Document.objects.get(url=contact.link)
		doc = {
				'type': 'contact',
				'client': contact.client.client_name,
				'client_id': contact.client.id,
				'registrant': contact.registrant.reg_name,
				'reg_id': contact.registrant.reg_id,
				'description': contact.description,
				'date': contact.date,
				'link': contact.link,
				'doc_id': document.id,
		}

		for l in contact.lobbyist.all():
			if l.lobbyist_name:
				doc['employee'] = l.lobbyist_name
		c_id = "contact" + str(contact.id)
		res = es.index(index="foreign", doc_type='interactions', id=c_id, body=doc)

	res = es.search(index="foreign", doc_type='interactions', body={"query": {"match_all": {}}})
	print("Got %d Hits:" % res['hits']['total'])
	for hit in res['hits']['hits']:
		print hit

	print '\nloaded contacts\n'

def load_contributions():
	for contribution in Contribution.objects.all():
		document = Document.objects.get(url=contribution.link)

		doc = {
				'type': 'contribution',
				'registrant': contribution.registrant.reg_name,
				'reg_id': contribution.registrant.reg_id,
				'recipient': contribution.recipient.name,
				'recipient_id': contribution.recipient.id,
				'date': contribution.date,
				'state_local': contribution.recipient.state_local,
				'amount': contribution.amount,
				'link': contribution.link,
				'doc_id': document.id,
		}

		if contribution.lobbyist:
			if contribution.lobbyist.lobbyist_name:
				doc['contributor'] = contribution.lobbyist.lobbyist_name
			if contribution.lobbyist.PAC_name:
				doc['contributor'] =  contribution.lobbyist.PAC_name
				doc['pac'] = True

		con_id = 'contribution' + str(contribution.id)
		res = es.index(index="foreign", doc_type='interactions', id=con_id, body=doc)

	res = es.search(index="foreign", doc_type='interactions', body={"query": {"match_all": {}}})
	print("Got %d Hits:" % res['hits']['total'])
	for hit in res['hits']['hits']:
		print hit

	print '\nloaded contributions\n'

def load_payments():
	for payment in Payment.objects.all():
		document = Document.objects.get(url=payment.link)
		doc = {
				'type': 'payment',
				'client': payment.client.client_name,
				'client_id': payment.client.id,
				'registrant': payment.registrant.reg_name,
				'reg_id': payment.registrant.reg_id,
				'purpose': payment.purpose,
				'date': payment.date,
				'amount': payment.amount,
				'link': payment.link,
				'doc_id': document.id,
		}
		if payment.subcontractor:
			doc['subcontractor'] = payment.subcontractor.reg_name,
			doc['subcontractor_id'] = payment.subcontractor.reg_id,

		pay_id = "payment" + str(payment.id)
		res = es.index(index="foreign", doc_type='interactions', id=pay_id, body=doc)

	res = es.search(index="foreign", doc_type='interactions', body={"query": {"match_all": {}}})
	print("Got %d Hits:" % res['hits']['total'])
	for hit in res['hits']['hits']:
		print hit

	print '\nloaded payments\n'

def load_disbursements():
	for disbursement in Disbursement.objects.all():
		document = Document.objects.get(url=disbursement.link)
		doc = {
				'type': 'disbursement',
				'client': disbursement.client.client_name,
				'client_id': disbursement.client.id,
				'registrant': disbursement.registrant.reg_name,
				'reg_id': disbursement.registrant.reg_id,
				'purpose': disbursement.purpose,
				'date': disbursement.date,
				'amount': disbursement.amount,
				'link': disbursement.link,
				'doc_id': document.id,
		}
		if disbursement.subcontractor:
			doc['subcontractor'] = disbursement.subcontractor.reg_name,
			doc['subcontractor_id'] = disbursement.subcontractor.reg_id,
		dis_id = 'disbursement' + str(disbursement.id)
		res = es.index(index="foreign", doc_type='interactions', id=dis_id, body=doc)

	res = es.search(index="foreign", doc_type='interactions', body={"query": {"match_all": {}}})
	print("Got %d Hits:" % res['hits']['total'])
	for hit in res['hits']['hits']:
		print hit

	print '\nloaded disbursements\n'

def load_gifts():
	for gift in Gift.objects.all():
		print gift
		document = Document.objects.get(url=gift.link)
		clients = []
		for client in gift.client.all():
			clients.append({'client_id': client.id, 'client_name': client.client_name})
		doc = {
				'type': 'gift',
				'registrant': gift.registrant.reg_name,
				'reg_id': gift.registrant.reg_id,
				'clients': [clients],
				'description': gift.description,
				'link': gift.link,
				'doc_id': document.id,
		}
		if gift.recipient:
			doc['recipient'] = gift.recipient.name
			doc['recipient_id'] = gift.recipient.id
		gift_id = 'gift' + str(gift.id)
		res = es.index(index="foreign", doc_type='interactions', id=gift_id, body=doc)

	res = es.search(index="foreign", doc_type='interactions', body={"query": {"match_all": {}}})
	print("Got %d Hits:" % res['hits']['total'])
	for hit in res['hits']['hits']:
		print hit

	print '\nloaded gifts\n'

def load_fara_text():
	for document in Document.objects.all():
		text = extract_text(document.url)
		reg_id = document.reg_id
		reg = Registrant.objects.get(reg_id=reg_id)
		reg_name = reg.reg_name
		doc = {
				'type': document.doc_type,
				'date': document.stamp_date,
				'registrant': reg_name,
				'reg_id': reg_id,
				'doc_id': document.id, 
				'link': document.url,
				'text': text,
		}

		res = es.index(index="foreign", doc_type='fara_files', id=document.id, body=doc)

	res = es.search(index="foreign", doc_type='fara_files', body={"query": {"match_all": {}}})
	print("Got %d Hits:" % res['hits']['total'])
	for hit in res['hits']['hits']:
		print hit

	print '\nloaded full text\n'


def extract_text(link):
	amazon_file_name = "pdfs/" + link[25:]
	if not default_storage.exists(amazon_file_name):
		try:
			add_file(link)
		except:
			return ''

	pdf = default_storage.open(amazon_file_name, 'rb')

	try:
		pdf_file = PdfFileReader(pdf)
	except:
		print "BAD FILE-- %s " %(link)

	pages = pdf_file.getNumPages()
	count = 0
	text = ''
	while count < pages:
		pg = pdf_file.getPage(count)
		pgtxt = pg.extractText()
		count = count + 1
		text = text + pgtxt

	return text 



