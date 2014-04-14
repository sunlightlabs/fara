#ryan's script
import csv

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from FaraData.models import Registrant, Client, Contribution, Recipient, Contact



class Command(BaseCommand):
	help = "Creates a spreadsheet for looking at contact and donation overlap."
	can_import_settings = True
	def handle(self, *args, **options):
		regs = Registrant.objects.all()

		for reg in regs:
			contrib_dict = {}
			if Contribution.objects.filter(registrant=reg).exists:
				if Contribution.objects.filter(registrant=reg).exists():
					reg_name = reg.reg_name
					reg_id = reg.reg_id
					clients = ''
					client_ids = ''
					for client in reg.clients.all():
						clients = clients + str(client.client_name) + "; "
						client_ids = client_ids + str(client.id) + "; "

					contribs = Contribution.objects.prefetch_related('recipient').filter(registrant=reg)
					
					for c in contribs:
						if not contrib_dict.has_key(c.recipient.id):
							payments = Contribution.objects.filter(registrant=reg,recipient=c.recipient).aggregate(amount=Sum('amount'))
							contrib_dict[c.recipient.id] = {'conribs':float(payments['amount']), 'recip_name': c.recipient.name, 'bioguide_id': c.recipient.bioguide_id, 'reg_id':reg_id, 'reg_name':reg_name, 'clients':clients, 'client_id':client_ids}
							# print contrib_dict[c.recipient.id]
					for key in contrib_dict.keys():
						if Contact.objects.filter(registrant=reg,recipient__id=key).exists():	
							contrib_dict[key]['contacts'] = Contact.objects.filter(registrant=reg,recipient__id=key).count()
							if Contact.objects.filter(registrant=reg,recipient__bioguide_id=contrib_dict[key]['bioguide_id']).exists():
								contrib_dict[key]['contacts_by_bioguide'] = Contact.objects.filter(registrant=reg,recipient__id=key).count()
							else:
								contrib_dict[key]['contacts_by_bioguide'] = 0
						else:
							contrib_dict[key]['contacts'] = 0
					print contrib_dict
					# write
		#print contrib_dict
				
