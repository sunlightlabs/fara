import datetime
import csv

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

from FaraData import spread_sheets
from fara_feed.models import Document

class Command(BaseCommand):
	help = "Creates one zipfile of spreadsheets for each form to buckets."
	can_import_settings = True

	def handle(self, *args, **options):
		# contacts
		contacts = Contacts.objects.filter(meta_data__processed=True)
		filename = "InfluenceExplorer/contacts.csv"
		contact_file = default_storage.open(filename, 'wb')
		writer = csv.writer(contact_file)
		writer.writerow(contact_heading)
		contact_sheet(contacts, writer)
		
		# payments
		payments = Payments.objects.filter(meta_data__processed=True)
		filename = "InfluenceExplorer/payments.csv"
		payment_file = default_storage.open(filename, 'wb')
		writer = csv.writer(payment_file)
		writer.writerow(payment_heading)
		payments_sheet(payments, writer)

		# disbursements
		disbursements = Disbursement.objects.filter(meta_data__processed=True)
		filename = "InfluenceExplorer/disbursements.csv"
		disbursement_file = default_storage.open(filename, 'wb')
		writer = csv.writer(disbursement_file)
		writer.writerow(disbursement_heading)
		disbursements_sheet(disbursements, writer)

		# contributions
		contributions = Contributions.objects.filter(meta_data__processed=True)
		filename = "InfluenceExplorer/contributions.csv"
		contribution_file = default_storage.open(filename, 'wb')
		writer = csv.writer(contribution_file)
		writer.writerow(contribution_heading)
		contributions_sheet(contributions, writer)

		# client-registrant
		filename = "InfluenceExplorer/client_registrant.csv"
		cr_file = default_storage.open(filename, 'wb')
		writer = csv.writer(cr_file)
		client_registrant(writer)





