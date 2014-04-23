import json
import datetime


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from FaraData.models import Contact, Registrant, MetaData, Payment, Contribution, Location
from fara_feed.models import Document

class Command(BaseCommand):
	help = "Creates data for the 2013 totals page."
	can_import_settings = True

	def handle(self, *args, **options):
		total_registrants()
		location_api()


def total_registrants():
	registrants = Registrant.objects.all()
	results = []
	lobbying_regs =[]
	docs_for_clients = []
	for r in registrants:
		reg_id = r.reg_id
		registrant ={}
		if Document.objects.filter(processed=True,reg_id=reg_id,doc_type__in=['Supplemental','Amendment'],stamp_date__range=(datetime.date(2013,1,1), datetime.date.today())).exists():
			doc_list = []
			registrant["reg_name"] = r.reg_name
			registrant['reg_id'] = r.reg_id
			# looking for all processed documents
			for doc in Document.objects.filter(processed=True,reg_id=reg_id,doc_type__in=['Supplemental','Amendment'],stamp_date__range=(datetime.date(2013,1,1), datetime.date.today())):
				doc_list.append(doc.url)
			
			docs_2013 = []
			s13 = 0
			# doc is really a doc url
			for doc in doc_list:
				md = MetaData.objects.get(link=doc)
				end_date = md.end_date
				# meta data for supplementals and amendments with supplemental-like records should all have end dates
				if end_date != None:
					# narrows to 2013 Supplementals and Amendments that apply to 2013
					if datetime.date(2013,1,1) <= md.end_date <= datetime.date(2013,12,31):
						docs_2013.append(doc)
						docs_for_clients.append(doc)
						print "adding"
						if "Supplemental" in doc:
							s13 = s13 + 1
						if "Registration" in doc:
							s13 = s13 + 1

			if s13 == 2:
				complete_records13 = True
				registrant['complete_records13'] = True
			else:
				registrant['complete_records13'] = False

			if Payment.objects.filter(link__in=docs_2013):
				payments2013 = Payment.objects.filter(link__in=docs_2013).aggregate(total_pay=Sum('amount'))
				payments2013 = float(payments2013['total_pay'])
				registrant['payments2013'] = payments2013

			if Contact.objects.filter(registrant=reg_id,recipient__agency__in=["Congress", "House", "Senate", "White House"], meta_data__end_date__range=(datetime.date(2013,1,1), datetime.date.today()) ).exists():
				registrant['federal_lobbying'] = True
				if r.reg_id not in lobbying_regs:
					lobbying_regs.append(r.reg_id)
			else:
				registrant['federal_lobbying'] = False
				
			if Contact.objects.filter(registrant=reg_id,recipient__agency="U.S. Department of State", meta_data__end_date__range=(datetime.date(2013,1,1), datetime.date.today()) ).exists():
				registrant['state_dept_lobbying'] = True
				if r.reg_id not in lobbying_regs:
					lobbying_regs.append(r.reg_id)
			else:
				registrant['state_dept_lobbying'] = False
				
			if Contact.objects.filter(registrant=reg_id,recipient__agency="Media", meta_data__end_date__range=(datetime.date(2013,1,1), datetime.date.today()) ).exists():
				registrant['pr'] = True
			else:
				registrant['pr'] = False

			if Contribution.objects.filter(registrant=reg_id, meta_data__end_date__range=(datetime.date(2013,1,1), datetime.date.today())).exists():
				registrant['contribution'] = True
			else:
				registrant['contribution'] = False
				
			if s13 != 0:
				results.append(registrant)
	
	# save to file
	with open("api/computations/reg13.json", 'w') as f:
		results = json.dumps({'results':results}, separators=(',',':'))
		f.write(results)

	# pass lobbying regs to client totaler
	print docs_for_clients
	client_totals(lobbying_regs, docs_for_clients)

def location_api():
	locations = Location.objects.all()
	results = {}
	results["000"] = []
	for l in locations:
		if l.country_code:
			if results.has_key(l.country_code):
				results[l.country_code].append({'name':l.location, 'id': l.id, 'region':l.region})
			else:
				results[l.country_code] = [{'name':l.location, 'id': l.id, 'region':l.region}]
		else:
			results["000"].append({'name':l.location, 'id': l.id, 'region':l.region})

	with open("api/computations/map.json", 'w') as f:
		results = json.dumps({'results':results}, separators=(',',':'))
		f.write(results)

# this isn't efficient but it has a lot of data checking
# I can't total as I go from the reg_totals because I want the records of all registrants who lobby not just the payments on the record where the lobbying occurs
def client_totals(lobbying_regs, docs):
	print lobbying_regs
	print
	print docs
	print
	for doc_url in docs:
		print doc_url
		doc = Document.objects.get(url=doc_url)
		client_totals = {}
		# eliminate docs that were not submitted by lobbyists
		if Registrant.objects.get(reg_id=doc.reg_id) in lobbying_regs:
			print "found reg"
			# I can't just sum because I need to break it up by client registrant pairs
			if Payment.objects.filter(link = doc.url).exists():
				print "found payments"
				for payment in Payment.objects.filter(link = doc.url):
					print "made it to payment loop"
					if client_totals.has_key(payment.client.id):
						if client_totals[payment.client.id]['registrants'].has_key(reg_id):
							print "building on existing record"
							total = client_totals[payment.client.id]['registrants'][reg_id][reg_total]
							total_pay  = total + payment.amount
							client_totals[payment.client.id]['registrants'][reg_id][reg_total] = total_pay
							# I want to catch this even if it is missing on the first record 
							if payment.subcontractor != None and client_totals[payment.client.id]['registrants']['subcontractor'] != payment.subcontractor.reg_name:
							 	print subcontractor.reg_name
							 	client_totals[payment.client.id]['registrants']['subcontractor'] = payment.subcontractor.reg_name
						else:
							print "new reg existing record"
							client_totals[payment.client.id]['registrants'][reg_id] = {'reg_id':reg_id, 'reg_name':reg_name, 'reg_total':payment.amount, 'subcontractor':payment.subcontractor.reg_name}
					else:
						client_totals[payment.client.id] = {
															'client_name':client.name, 
															'client_location':client.location.location, 
															'locaiton_id': client.location.location_id,
															'registrants':{ 
																			reg_id: {
																						'reg_id':reg_id, 
																						'reg_name':reg_name, 
																						'reg_total':payment.amount, 
																						'subcontractor':payment.subcontractor.reg_name
																					},
																			},
															}

		# just for debug
		else:
			print "not a lobbyist"




