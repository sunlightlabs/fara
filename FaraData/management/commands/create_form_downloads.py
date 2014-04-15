import datetime

from optparse import make_option

from FaraData.unicode_csv import UnicodeWriter
from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from FaraData.spread_sheets import *
from FaraData.models import Contact, Payment, Disbursement, Contribution
from fara_feed.models import Document

class Command(BaseCommand):
	help = "Creates one zipfile of spreadsheets for each form to buckets."
	can_import_settings = True

	option_list = BaseCommand.option_list + (
			make_option('--contacts',
				action='store_true',
				help='create full download of contacts',
			),
			make_option('--client_reg',
				action='store_true',
				help='create full download of clients and registrants',
			),
			make_option('--disbursements',
				action = 'store_true',
				help= 'create full download of disbursements'
			),
			make_option('--contributions',
				action = 'store_true',
				help= 'create full download of contributions'
			),
			make_option('--payments',
				action = 'store_true',
				help = 'create full download of payments'
			),
		)

	def handle(self, *args, **options):
		print "starting", datetime.datetime.now().time()
		if options.get('contacts'):
			create_contact()
		if options.get('client_reg'):
			client_reg()
		if options.get('disbursements'):
			disbursements()
		if options.get('contributions'):
			contributions()
		if options.get('payments'):
			payments()

		print "ending", datetime.datetime.now().time()


def create_contact():
	pool = Contact.objects.filter(meta_data__processed=True)
	paginated_contacts = Paginator(pool, 500)
	page_range = paginated_contacts.page_range

	filename = "InfluenceExplorer/contacts.csv"
	# this was paginated to avoid horrendous garbage cleanup when I passes it all at once
	with default_storage.open(filename, 'wb') as contact_file:
		writer = UnicodeWriter(contact_file)
		writer.writerow(contact_heading)
		page = 1
		for n in range(1, page_range[1]):
			contacts = paginated_contacts.page(n)
			contact_sheet(contacts, writer)

	print "done with contacts"

def client_reg():
	filename = "InfluenceExplorer/client_registrant.csv"
	cr_file = default_storage.open(filename, 'wb')
	writer = UnicodeWriter(cr_file)
	client_registrant(writer)
	cr_file.close()
	print "done with client registrant"

def disbursements():
	disbursements = Disbursement.objects.filter(meta_data__processed=True)
	filename = "InfluenceExplorer/disbursements.csv"
	disbursement_file = default_storage.open(filename, 'wb')
	writer = UnicodeWriter(disbursement_file)
	writer.writerow(disbursement_heading)
	disbursements_sheet(disbursements, writer)
	disbursement_file.close()
	print "done with disbursements"

def contributions():
	contributions = Contribution.objects.filter(meta_data__processed=True)
	filename = "InfluenceExplorer/contributions.csv"
	contribution_file = default_storage.open(filename, 'wb')
	writer = UnicodeWriter(contribution_file)
	writer.writerow(contribution_heading)
	contributions_sheet(contributions, writer)
	contribution_file.close()
	print "done with contributions"

def payments():
	payments = Payment.objects.filter(meta_data__processed=True)
	filename = "InfluenceExplorer/payments.csv"
	payment_file = default_storage.open(filename, 'wb')
	writer = UnicodeWriter(payment_file)
	writer.writerow(payment_heading)
	payments_sheet(payments, writer)
	payment_file.close()
	print "done with payments"






