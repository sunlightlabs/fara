import datetime
import csv

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

from FaraData import spread_sheets
from FaraData.models import Contact, Payment, Disbursement, Contribution
from fara_feed.models import Document

# HEADINGS
contact_heading = ['Date', 'Contact Title','Contact Name', 'Contact Office', 'Contact Agency', 'Client', 'Client Location', 'Registrant', 'Description', 'Type', 'Employees Mentioned', 'Affiliated Member Bioguide ID', 'Source', 'Document ID', 'Registrant ID', 'Client ID', 'Location ID', 'Recipient ID', 'Record ID']
contribution_heading = ['Date', 'Amount', 'Recipient', 'Registrant', 'Contributing Individual or PAC', 'CRP ID of Recipient', 'Bioguide ID', 'Source', 'Document ID', 'Registrant ID', 'Recipient ID', 'Record ID']
payment_heading = ['Date', 'Amount', 'Client', 'Registrant', 'Purpose', 'From subcontractor', 'Source', 'Document ID', 'Registrant ID', 'Client ID','Location ID', 'Subcontractor ID', 'Record ID']
disbursement_heading = ['Date', 'Amount', 'Client', 'Registrant', 'Purpose', 'To Subcontractor', 'Source', 'Document ID' 'Registrant ID', 'Client ID','Location ID', 'Subcontractor ID', 'Record ID']
client_reg_heading = ['Client', 'Registrant name', 'Terminated', 'Location of Client', 'Description of service (when available)', 'Registrant ID', 'Client ID', 'Location ID']



class Command(BaseCommand):
	help = "Creates one zipfile of spreadsheets for each form to buckets."
	can_import_settings = True

	def handle(self, *args, **options):
		# contacts
		contacts = Contact.objects.filter(meta_data__processed=True)
		filename = "InfluenceExplorer/contacts.csv"
		contact_file = default_storage.open(filename, 'wb')
		writer = csv.writer(contact_file)
		writer.writerow(contact_heading)
		contact_sheet(contacts, writer)
		
		# payments
		payments = Payment.objects.filter(meta_data__processed=True)
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
		contributions = Contribution.objects.filter(meta_data__processed=True)
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





