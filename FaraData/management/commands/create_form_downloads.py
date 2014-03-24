import datetime
import csv

from FaraData.unicode_csv import UnicodeWriter
from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

from FaraData.spread_sheets import *
from FaraData.models import Contact, Payment, Disbursement, Contribution
from fara_feed.models import Document

class Command(BaseCommand):
	help = "Creates one zipfile of spreadsheets for each form to buckets."
	can_import_settings = True

	def handle(self, *args, **options):
		print "starting", datetime.datetime.now().time()
		# client-registrant
		filename = "InfluenceExplorer/client_registrant.csv"
		cr_file = default_storage.open(filename, 'wb')
		writer = csv.writer(cr_file)
		client_registrant(writer)
		cr_file.close()
		print "done with client registrant"

		# disbursements
		disbursements = Disbursement.objects.filter(meta_data__processed=True)
		filename = "InfluenceExplorer/disbursements.csv"
		disbursement_file = default_storage.open(filename, 'wb')
		writer = csv.writer(disbursement_heading)
		writer.writerow(disbursement_file)
		disbursements_sheet(disbursements, writer)
		disbursement_file.close()
		print "done with disbursements"

		# contributions
		contributions = Contribution.objects.filter(meta_data__processed=True)
		filename = "InfluenceExplorer/contributions.csv"
		contribution_file = default_storage.open(filename, 'wb')
		writer = csv.writer(contribution_file)
		writer.writerow(contribution_heading)
		contributions_sheet(contributions, writer)
		contribution_file.close()
		print "done with contributions"

		# payments
		payments = Payment.objects.filter(meta_data__processed=True)
		filename = "InfluenceExplorer/payments.csv"
		payment_file = default_storage.open(filename, 'wb')
		writer = csv.writer(payment_file)
		writer.writerow(payment_heading)
		payments_sheet(payments, writer)
		payment_file.close()
		print "done with payments"
		
		#contacts
		contacts = Contact.objects.filter(meta_data__processed=True)
		print "got contacts"
		filename = "InfluenceExplorer/contacts.csv"
		contact_file = default_storage.open(filename, 'wb')
		writer = csv.writer(contact_file)
		writer.writerow(contact_heading)
		print 'starting contacts'
		contact_sheet(contacts, writer)
		contact_file.close()
		print "done with contacts"

		print "ending", datetime.datetime.now().time()
		

		
		

		
		

		
		







