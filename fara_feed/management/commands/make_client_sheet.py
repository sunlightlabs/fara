import csv
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

from FaraData.models import Client, Location, Registrant, ClientReg

# client name # reg name # location # 

class Command(BaseCommand):
	can_import_settings = True

	def handle(self, *args, **options):
		filename = "data/clients" + str(datetime.date.today()) + ".csv"
		writer = csv.writer(open(filename, 'wb'))
		writer.writerow(["Client name", "Registrant name", "Location of Client", "Description of service (when available)"])

		regs = Registrant.objects.all()
		print regs
		print 1
		for reg in regs:
			print reg
			print reg.clients.all()
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

				writer.writerow([client_name, reg_name, client_loc, discription, reg.reg_id, client.id])
