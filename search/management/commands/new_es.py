# Loads the interactions from recent documents
			# for registrants, clients, locations and recipients, I am going to add them as they are created, 
			# Perhaps, I should burn them down and re-do them monthly

			# gifts - I am not displaying these yet so I am not loading 

			# load arms with the arms scraper
			# documents and registrants get loaded with FARA scraper


import os
from elasticsearch import Elasticsearch
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings 

from fara_feed.management.commands.create_feed import add_file
from fara_feed.models import Document
from FaraData.models import Registrant, MetaData, Contact, Payment, Disbursement, Contribution, Client, Recipient

es = Elasticsearch(**settings.ES_CONFIG)

class Command(BaseCommand):
	help = "Puts all the new itemized data into elastic search"
	can_import_settings = True

	def handle(self, *args, **options):
		print "starting", datetime.datetime.now().time()
		#load all clients I don't have a good way to filter
		for client in Client.objects.all():
			doc = {
					'name': client.client_name, 
					'location': client.location.location, 
					'country_grouping': client.location.country_grouping,
					'client_description': client.description,
			}
			
			res = es.index(index="foreign", doc_type='client', id=client.id, body=doc)

		#load all recipients I don't have a good way to filter
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

		# add interactions
		start_date = datetime.date.today() - datetime.timedelta(days=3)
		print start_date
		md = MetaData.objects.filter(processed=True, upload_date__range=(start_date, datetime.date.today()))
		print md
		
		for contact in Contact.objects.filter(meta_data__in=md):
			c_id = 'contact' + str(contact.id)
			if es.exists(index='foreign', doc_type='interactions', id=c_id) == False:
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
				print c_id

		for payment in Payment.objects.filter(meta_data__in=md):
			p_id = 'payment' + str(payment.id)
			if es.exists(index='foreign', doc_type='interactions', id=p_id) == False:
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
				print pay_id

		for disbursement in Disbursement.objects.filter(meta_data__in=md):
			d_id = 'disbursement' + str(disbursement.id)
			if es.exists(index='foreign', doc_type='interactions', id=d_id) == False:
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
				print dis_id

		for contribution in Contribution.objects.filter(meta_data__in=md):
			c_id = 'contribution' + str(contribution.id)
			if es.exists(index='foreign', doc_type='interactions', id=c_id) == False:
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
				print con_id

		print "ending", datetime.datetime.now().time()



