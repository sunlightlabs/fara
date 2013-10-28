import csv

from django.core.management.base import BaseCommand, CommandError

from FaraData.models import *


class Command(BaseCommand):
	def handle(self, pythonpath, verbosity, traceback, settings):
		cleared = {}
		#import csv

		clientcsv = csv.reader(open('util/management/commands/clean_client_10_28.csv', "rU"))
		#check that clients are correctly identified
		for i in clientcsv:
			
			original_id = i[0]
			new_id = i[1]
			name = i[2]
			try:
				client = Client.objects.get(id=original_id)
			
			except:
				client = None
			
			if client != None:
				if client.client_name == name:
					cleared[original_id] = new_id
				else:
					print "Name error", 1
			else:
				print "Name error", 2


		#go through records  to replace where they are pointing
		for cleared_id in cleared.keys():
			#Registrant.clients m2m
			old_client = Client.objects.get(id=cleared_id)
			new_id = cleared[cleared_id]
			new_client = Client.objects.get(id=new_id)
			regs = Registrant.objects.filter(clients__id__exact= cleared_id)
			
			for r in regs:
				print new_client, old_client
				r.clients.add(new_client)
				print "adding new_client: ", new_client
				r.clients.remove(old_client)
				print "removing: ", old_client, r.reg_id

			#Registrant.terminated_clients m2m
			regs2 = Registrant.objects.filter(terminated_clients__id__exact= cleared_id)
			for r in regs2:
				print r.reg_name
				r.terminated_clients.add(new_client)
				print "terminated adding new_client", new_client
				r.terminated_clients.remove(old_client)
				print "terminated removing: ", old_client, r.reg_id

			#Gift.client m2m
			gifts = Gift.objects.filter(client__id= cleared_id)
			for g in gifts:
				g.client.add(new_client)
				print "gift adding new_client", new_client
				g.client.remove(old_client)
				print "gift removing: ", old_client, g.id

			#Contact.client fk
			contacts = Contact.objects.filter(client__id= cleared_id)
			for c in contacts:
				c.client = new_client
				c.save()
				print "contact -saving ", new_client, "replacing ", old_client, c.id
			#Payment.client fk
			payments = Payment.objects.filter(client__id= cleared_id)
			for p in payments:
				p.client = new_client
				p.save()
				print "payemnt -saving ", new_client, "replacing ", old_client, p.id
			#Disbursement.client fk
			dis = Disbursement.objects.filter(client__id= cleared_id)
			for d in dis:
				d.client = new_client
				d.save()
				print "dis -saving ", new_client, "replacing ", old_client, d.id
			#ClientReg.client_id fk
			client_reg = ClientReg.objects.filter(client_id__id= cleared_id)
			for cr in client_reg:
				cr.client = new_client
				cr.save()
				print "client reg, replacing ", old_client, " with ", new_client, cr.id



#get rid of bad clients
