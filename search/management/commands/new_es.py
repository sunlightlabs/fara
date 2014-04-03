import os
from elasticsearch import Elasticsearch
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings 

from fara_feed.management.commands.create_feed import add_file
from fara_feed.models import Document
from FaraData.models import Registrant

es = Elasticsearch(**settings.ES_CONFIG)

class Command(BaseCommand):
	help = "Puts all the new itemized data into elastic search"
	can_import_settings = True

	def handle(self, *args, **options):
		start_date = datetime.date.today() - datetime.timedelta(days=3)
		for md in MetaData(processed=True, upload_date__range=(start_date, datetime.date.today())):
			for contact in Contacts.objects.filter(meta_data=md):
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
					c_id = "contact" + contact.id
					res = es.index(index="foreign", doc_type='interactions', id=c_id, body=doc)

			for payment in Payment.objects.filter(meta_data=md):
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

			for disbursement in Disbursement.objects.filter(meta_data=md):
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
			
			for contribution in Contributions.objects.filter(meta_data=md):
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

			#for registrants
			#for clients
			#for locations
			

			# recipients

			# gifts
	



		# load arms



if metadata.processed == True:
    spread_sheets.make_file(form)
    