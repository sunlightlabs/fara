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
					print "working"
				else:
					print "Name error", 1
			else:
				print "Name error", 2


		#go through records  to replace where they are pointing
		for cleared_id in cleared.keys():
			#Registrant.clients m2m
			
			regs = Registrant.objects.filter(clients__id__exact= cleared_id)
			print regs
			for r in regs:
				print "hello"
			regs2 = Registrant.objects.filter(terminated_clients__id__exact= cleared_id)
			for r in regs2:
				print r
				print "good bye"

			#print registrations
			#Registrant.terminated_clients m2m
			#registrationsT = Registrant.terminated_clients.filter(id=cleared_id)
			
			#Gift.client m2m
			
			#Contact.client fk
			
			#Payment.client fk
			
			#Disbursement.client fk
			
			#ClientReg.client_id fk





#get rid of bad clients
