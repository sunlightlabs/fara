from django.core.management.base import BaseCommand, CommandError

from FaraData.models import Registrant, Client, Payment, Contact, Disbursement, Gift, Contribution


class Command(BaseCommand):
	def handle(self, pythonpath, verbosity, traceback, settings):
		wrong_contact = 0
		wrong_contribution = 0
		wrong_payment = 0 
		for contact in Contact.objects.all():
			reg_id = str(contact.registrant.reg_id)
			if reg_id not in contact.link:
				print reg_id, contact.link, contact.date
				wrong_contact += 1
		print "ran contacts"
		for contribution in Contribution.objects.all():
			reg_id = str(contribution.registrant.reg_id)
			if reg_id not in contribution.link:
				print reg_id, contribution.link, contribution.date
				wrong_contribution += 1
		print "ran contributions"
		for payment in Payment.objects.all():
			reg_id = str(payment.registrant.reg_id)
			if reg_id not in payment.link:
				print reg_id, payment.link, payment.date
				wrong_payment += 1
				
		print "contact", wrong_contact
		print "contribution", wrong_contribution
		print "payment", wrong_payment