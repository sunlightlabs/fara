import csv

from django.core.management.base import BaseCommand, CommandError

from FaraData.models import *


class Command(BaseCommand):
	def handle(self, pythonpath, verbosity, traceback, settings):
		print "good morning"
		cleared = {}
		#import csv
		clientcsv = open('util/management/commands/clean_clients10_24.csv', 'rb')

		#check that clients are correctly identified
		for i in clientcsv:
			original_id = i[0]
			new_id = i[1]
			name = i[2]
			try:
				client = Client.objects.get(id=original_id)
				if client.client_name == name:
					cleared[original_id] = new_id
				else:
					print "Name error", i
			except:
				print "Lookup error", i

		#go through records  to replace where they are pointing
		for cleared_id in cleared.keys():
			print id
			#Registrant.clients m2m
			registrations = Registrant.clients.filter(id=cleared_id)
			#print registrations
			#Registrant.terminated_clients m2m
			#registrationsT = Registrant.terminated_clients.filter(id=cleared_id)
			
			#Gift.client m2m
			
			#Contact.client fk
			
			#Payment.client fk
			
			#Disbursement.client fk
			
			#ClientReg.client_id fk





#get rid of bad clients
