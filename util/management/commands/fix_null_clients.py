# all null clients in the archival data were assigned to the same client
import csv

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

from FaraData.models import Contact, Client, Contact, Payment, Disbursement, Registrant

class Command(BaseCommand):
	def handle(self, *args, **options):
		#import csv put the fixes into a list
		clientcsv = csv.reader(open('util/null_clients.csv', "rU"))
		clients_regs = []
		clientcsv.next()
		for i in clientcsv:
			reg_id = i[0]
			bad_client = i[1]
			real_client_name = i[2]
			clients_regs.append({'reg':reg_id, 'client':real_client_name, 'bad':bad_client}) 
		print clients_regs
	
		#check that clients are correctly identified
		
		for entry in clients_regs:
			reg = Registrant.objects.get(reg_id=entry['reg'])
			reg_id = reg.reg_id
			real_client = Client.objects.get(id=entry['client'])
			bad = Client.objects.get(id=entry['bad'])

			if Contact.objects.filter(registrant=reg,client=bad).exists():
				for contact in Contact.objects.filter(registrant=reg,client=bad):
					contact.client = real_client
					# contact.save()
					print real_client.client_name, "contact"
			if Payment.objects.filter(registrant=reg,client=bad).exists():
				for payment in Payment.objects.filter(registrant=reg,client=bad):
					payment.client = real_client
					#payment.save()
					print real_client.client_name, "payment"
			if Disbursement.objects.filter(registrant=reg,client=bad).exists():
				for disbursement in Disbursement.objects.filter(registrant=reg,client=bad):
					disbursement.client = real_client
					#disbursement.save()
					print real_client.client_name, "disbursement"
			if Registrant.objects.filter(reg_id=reg_id,clients=bad).exists():
				reg.clients.add(real_client)
				reg.clients.remove(bad)
				#reg.save
				print real_client.client_name, "client"

			if Registrant.objects.filter(reg_id=reg_id,terminated_clients=bad).exists():
				reg.terminated_clients.add(real_client)
				reg.terminated_clients.remove(bad)
				#reg.save()
				print real_client.client_name, "terminated_clients"



