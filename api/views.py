import datetime
import json
import os

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.db.models import Sum

from fara_feed.models import Document
from FaraData.models import Registrant, Payment, Contact, Contribution, Recipient, Client, Disbursement, ClientReg, Location, MetaData, Lobbyist
from arms_sales.models import Proposed
from search.search_foreign import *

from fara.local_settings import API_PASSWORD

def paginate(form, page):
	paginator = Paginator(form, 20)
	try:
		form = paginator.page(page)
	except PageNotAnInteger:
		form = paginator.page(1)
	except EmptyPage:
		form = paginator.page(paginator.num_pages)
	return form

def test(request):
	results = json.dumps({"working":True}, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")

def incoming_fara(request):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied

	if request.GET.get('doc_id'):
		doc_id = int(request.GET.get('doc_id'))
		doc =  Document.objects.get(id=doc_id)
		reg_id = doc.reg_id
		info = {
			"doc_id": doc.id,
			"doc_type": doc.doc_type,
			"stamp_date": doc.stamp_date.strftime("%m/%d/%Y"),
			"processed": doc.processed,
			"reg_id": reg_id,
			}
		
		if Registrant.objects.filter(reg_id=reg_id).exists():
			reg = Registrant.objects.get(reg_id=reg_id)
			info['reg_name']= reg.reg_name
		
		results = json.dumps({'results':info}, separators=(',',':'))
		return HttpResponse(results, mimetype="application/json")

	query_params = {}
	if not request.GET.get('all_records'):
		query_params['stamp_date__range'] = (datetime.date(2012,1,1), datetime.date.today())
	
	### Would like to make this not case sensitive 
	if request.GET.get('doc_type'):
		form_type = request.GET.get('doc_type')
		# all takes away doc type restrictions
		if form_type != 'all':
			query_params['doc_type'] = [form_type]
	else:
		query_params['doc_type__in'] = ['Supplemental', 'Amendment', 'Exhibit AB', 'Registration']

	if request.GET.get('processed'):
		processed = request.GET.get('processed')
		if processed == 'true':
			processed = True
		if processed == 'false':
			processed = False
		query_params['processed'] = processed

	if request.GET.get('reg_id'):
		reg_id = request.GET.get('reg_id')
		query_params['reg_id'] = reg_id

	if request.GET.get('p'):
		p = int(request.GET.get('p'))
	else:
		p = 1
	
	page = {}	
	page['page'] = p

	doc_pool = Document.objects.filter(**query_params).order_by('-stamp_date')
	paginate_docs = paginate(doc_pool, p)
	page_of_docs = paginate_docs[0:]
	page['num_pages'] = int(doc_pool.count())/20

	results = []
	for doc in page_of_docs:
		reg_id = doc.reg_id
		info = {
			"doc_id": doc.id,
			"doc_type": doc.doc_type,
			"stamp_date": doc.stamp_date.strftime("%m/%d/%Y"),
			"processed": doc.processed,
			"reg_id": reg_id,
			}
		if Registrant.objects.filter(reg_id=reg_id).exists():
			reg = Registrant.objects.get(reg_id=reg_id)
			info['reg_name']= reg.reg_name
		results.append(info)

	results = json.dumps({'results': results, 'page':page}, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")

def incoming_arms(request):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied

	if request.GET.get('p'):
		p = request.GET.get('p')
	else:
		p = 1
	page = {}
	page['page'] = p 

	if request.GET.get('location_id'):
		arms_pool = Proposed.objects.filter(location_id=request.GET.get('location_id'))
	elif request.GET.get('doc_id'):
		arms = Proposed.objects.get(id=request.GET.get('doc_id'))
	
		if arms.date:
			try:
				date = arms.date.strftime("%m/%d/%Y")
			except:
				date = None
		else:
			print arms, "Has no date"
			date =  None
		
		return HttpResponse(json.dumps({'pdf_url':arms.pdf_url, 'date':date, 'title':arms.title, 'id':arms.id, 'location':arms.location, 'location_id':arms.location_id, 'dsca_url':arms.dsca_url}), mimetype="application/json")
	else:
		arms_pool = Proposed.objects.all().order_by('-date')
	
	paginate_arms = paginate(arms_pool, p)
	page_of_arms = paginate_arms[0:]
	page['num_pages'] = int(arms_pool.count())/20

	proposed_sales = []
	count = 1
	for arms_press in page_of_arms:
		record = {}
		if count %2 == 0:
			record['row'] = "even"
		else:
			record['row'] = "odd"
		count += 1
		record['id'] = arms_press.id
		record['title'] = arms_press.title
		
		if arms_press.date:
			try:
				record['date'] = arms_press.date.strftime("%m/%d/%Y")
			except:
				record['date'] = None
		else:
			print record, "Has no date"
			record['date'] =  None

		# this is not scraped yet
		if arms_press.amount:
			record['amount'] = arms_press.amount
		proposed_sales.append(record)

	results = {'proposed_sales': proposed_sales, 'page': page}
	results = json.dumps({'results': results}, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")

def doc_profile(request, doc_id):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied
	
	doc_id= int(doc_id)
	doc = Document.objects.get(id=doc_id)
	url = doc.url
	reg_id = doc.reg_id

	results ={
		"reg_id": reg_id,
		"url": url,
		"stamp_date": doc.stamp_date.strftime("%m/%d/%Y"),
		"doc_type": doc.doc_type,
		"processed": doc.processed,
		"doc_id": doc.id,
	}

	if MetaData.objects.filter(link=url):
		md = MetaData.objects.get(link=url)
		if md.is_amendment == True:
			results['amended'] = True

	if Registrant.objects.filter(reg_id=reg_id).exists():
		reg = Registrant.objects.get(reg_id=reg_id)
		results['reg_name'] = reg.reg_name

		client_results = reg.clients.all()
		clients = client_form_summary(client_results, url)
		results['clients'] = clients

		terminated_results = reg.terminated_clients.all()
		terminated_clients = client_form_summary(terminated_results, url)
		results['terminated_clients'] = terminated_clients

		if doc.processed == True:
			if Contribution.objects.filter(link=url).exists():
				contribution = Contribution.objects.filter(link=url,meta_data__processed=True).aggregate(total_pay=Sum('amount'))
				total_contributions = float(contribution['total_pay'])
				results['total_contribution'] = total_contributions
			
			if Payment.objects.filter(link=url).exists():
				payment = Payment.objects.filter(link=url,meta_data__processed=True).aggregate(total_pay=Sum('amount'))
				total_pay = float(payment['total_pay'])
				results['total_payment'] = total_pay

			if Contact.objects.filter(link=url).exists():
				total_contacts = Contact.objects.filter(link=url,meta_data__processed=True).count()
				results['total_contact'] = total_contacts
			
			if Disbursement.objects.filter(link=url).exists():
				disbursements = Disbursement.objects.filter(link=url,meta_data__processed=True).aggregate(total_pay=Sum('amount'))
				total_disbursements = float(disbursements['total_pay'])
				results['total_disbursement'] = total_disbursements

	results = json.dumps({'results': results}, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")

# used to make the summary section of the form profile page
def client_form_summary(client_objects, url):
	clients = []
	for client in client_objects:
		c = {
			'client_name':client.client_name,
			'location': client.location.location,
			'client_id': client.id,
			'location_id': client.location.id,
		}		
		if Payment.objects.filter(link=url,client=client,meta_data__processed=True).exists():
			payment = Payment.objects.filter(link=url,client=client).aggregate(total_pay=Sum('amount'))
			total_pay = float(payment['total_pay'])
			c['payment'] = total_pay

		if Contact.objects.filter(link=url,client=client,meta_data__processed=True).exists():
			total_contacts = Contact.objects.filter(link=url,client=client).count()
			c['contact'] = total_contacts
		
		if Disbursement.objects.filter(link=url,client=client,meta_data__processed=True).exists():
			disbursements = Disbursement.objects.filter(link=url,client=client).aggregate(total_pay=Sum('amount'))
			total_disbursements = float(disbursements['total_pay'])
			c['disbursement'] = total_disbursements
		clients.append(c)
	return clients

def recipient_profile(request, recip_id):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied
	
	recipient = Recipient.objects.get(id=recip_id)
	results = []
	# If a member of congress, we want to get all the connected contacts

	if recipient.agency == "Congress":
		recipients = Recipient.objects.filter(bioguide_id=recipient.bioguide_id)
	else:
		recipients = [recipient]
			
	for recip in recipients:
		recipient = {}
		recipient['agency'] = recip.agency
		recipient['office_detail'] = recip.office_detail
		recipient['name'] = recip.name
		recipient['title'] = recip.title
		recipient['state_local'] = recip.state_local
		recipient['bioguide_id'] = recip.bioguide_id
		recip_id = recip.id 
		recipient['recipient_id'] = recip_id

		if Contribution.objects.filter(recipient=recip_id).exists():
			contribution = Contribution.objects.filter(recipient=recip_id,meta_data__processed=True).aggregate(total_pay=Sum('amount'))
			recipient['total_contribution'] = float(contribution['total_pay'])
		
		if Contact.objects.filter(recipient=recip_id).exists():
			recipient['contacts'] = Contact.objects.filter(recipient=recip_id, meta_data__processed=True).count()

		results.append(recipient)
	
	results = json.dumps({'results': results }, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")

# agency profile

def client_profile(request, client_id):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied

	c = Client.objects.get(id=client_id)
	results = []
	client = {}
	client['location'] = c.location.location 
	client['location_id'] = c.location.id
	client['client_name'] = c.client_name
	client['address'] = c.address1
	client['city'] = c.city
	client['state'] = c.state
	client['zip_code'] = c.zip_code
	client['client_type'] = c.client_type
	client['description'] = c.description

	if Contact.objects.filter(client=client_id,meta_data__processed=True).exists():
		client['contacts'] = Contact.objects.filter(client=client_id, meta_data__processed=True).count()

	# is null makes sure there is not double counting money flowing through multiple contractors
	if Payment.objects.filter(client=client_id).exists():
		client['total_payment'] = True

	# running total beginning in 2013
	if Payment.objects.filter(client=client_id,subcontractor__isnull=True,sort_date__range=( datetime.date(2013,1,1), datetime.date.today()),meta_data__processed=True).exists():
		payments = Payment.objects.filter(client=client_id,subcontractor__isnull=True,sort_date__range=(datetime.date(2013,1,1), datetime.date.today()),meta_data__processed=True).aggregate(total_pay=Sum('amount'))
		total_pay = float(payments['total_pay'])
		client['running_total_13'] = total_pay

	if Payment.objects.filter(client=client_id,subcontractor__isnull=True,meta_data__end_date__range=( datetime.date(2013,1,1), datetime.date(2014,1,1)),meta_data__processed=True).exists():
		payment13 = Payment.objects.filter(client=client_id,subcontractor__isnull=True,meta_data__end_date__range=( datetime.date(2013,1,1), datetime.date(2014,1,1)),meta_data__processed=True).aggregate(total_pay=Sum('amount'))
		total_pay = float(payment13['total_pay'])
		client['total_13'] = total_pay

	if Disbursement.objects.filter(client=client_id).exists():
		#disbursement = Disbursement.objects.filter(client=client_id,subcontractor__isnull=True).aggregate(total_pay=Sum('amount'))
		client['total_disbursement'] = True

	if Registrant.objects.filter(clients=c).exists():
		active_regs = Registrant.objects.filter(clients=c)
		acitve_regstrants = []
		for reg in active_regs:
			active_reg= {}
			active_reg['name'] = reg.reg_name
			active_reg['reg_id'] = reg.reg_id
			acitve_regstrants.append(active_reg)
		client['active_reg'] = acitve_regstrants
		client['active'] = True

	if Registrant.objects.filter(terminated_clients=c).exists():
		terminated_regs = Registrant.objects.filter(terminated_clients=c)
		terminated_registrants = []
		for reg in terminated_regs:
			terminated_reg = {}
			terminated_reg['name'] = reg.reg_name
			terminated_reg['reg_id'] = reg.reg_id
			terminated_registrants.append(terminated_reg)	
		client['terminated_reg'] = terminated_registrants

	results = json.dumps({'results': client }, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")

def location_profile(request, loc_id):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied 	
	
	results = {}
	location = Location.objects.get(id=loc_id)
	results['location_name'] = location.location
	results['location_id'] = location.id
	
	# Find client and reg information
	clients = Client.objects.filter(location=loc_id)
	client_list = []
	for c in clients:
		client = {}
		client['client_name'] = c.client_name
		client['client_type'] = c.client_type
		client['description'] = c.description
		client['id'] = c.id

		# is null makes sure there is not double counting money flowing through multiple contractors
		# changing to 2013 running total
		if Payment.objects.filter(client=c.id,subcontractor__isnull=True,sort_date__range=( datetime.date(2013,1,1), datetime.date.today()),meta_data__processed=True).exists():
			payment = Payment.objects.filter(client=c.id,subcontractor__isnull=True,sort_date__range=( datetime.date(2013,1,1), datetime.date.today()),meta_data__processed=True).aggregate(total_pay=Sum('amount'))
			client['running_total_13'] = float(payment['total_pay'])
		
		if Payment.objects.filter(client=c.id).exists():
			client['total_pay'] = True
		
		if Contact.objects.filter(client=c.id).exists():
			client['contacts'] = Contact.objects.filter(client=c.id).count()
		
		# registrant and status
		if Registrant.objects.filter(clients=c).exists():
			active_regs = Registrant.objects.filter(clients=c)
			acitve_regstrants = []
			for reg in active_regs:
				active_reg= {}
				active_reg['name'] = reg.reg_name
				active_reg['reg_id'] = reg.reg_id
				acitve_regstrants.append(active_reg)
			client['active_reg'] = acitve_regstrants
			client['active'] = True

		if Registrant.objects.filter(terminated_clients=c).exists():
			terminated_regs = Registrant.objects.filter(terminated_clients=c)
			terminated_registrants = []
			for reg in terminated_regs:
				terminated_reg = {}
				terminated_reg['name'] = reg.reg_name
				terminated_reg['reg_id'] = reg.reg_id
				terminated_registrants.append(terminated_reg)	
			client['terminated_reg'] = terminated_registrants
		
		client_list.append(client)

	if Contact.objects.filter(client__in=clients, meta_data__processed=True).exists():
		results['location_contacts'] = True
	if Payment.objects.filter(client__in=clients, meta_data__processed=True).exists():
		results['location_payments'] = True
	if Disbursement.objects.filter(client__in=clients, meta_data__processed=True).exists():
		results['location_disbursements'] = True

	results['clients'] = client_list
	results = json.dumps({'results': results }, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")

##### Why is there repeted Qubec?

def reg_profile(request, reg_id):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied

	results = {}
	clients = []
	terminated_clients = []
	registrant = {}
	reg = Registrant.objects.get(reg_id=reg_id)
	reg_id = reg.reg_id
	registrant['reg_id'] = reg_id
	registrant['name'] = reg.reg_name
	# could add address information 
	if Document.objects.filter(processed=True,reg_id=reg_id,doc_type__in=['Supplemental','Amendment'],stamp_date__range=(datetime.date(2013,1,1), datetime.date.today())).exists():
		docs_2013 = []
		s13 = 0
		registrant['docs_13'] = []
		# doc is really a doc url
		for doc in Document.objects.filter(processed=True, reg_id=reg_id,doc_type__in=['Supplemental','Amendment'],stamp_date__range=(datetime.date(2013,1,1), datetime.date.today())):
			doc = doc.url
			md = MetaData.objects.get(link=doc)
			end_date = md.end_date
			# meta data for supplementals and amendments with supplemental-like records should all have end dates
			if end_date != None:
				# narrows to 2013 Supplementals and Amendments that apply to 2013
				if datetime.date(2013,1,1) <= md.end_date <= datetime.date(2014,1,1):
					docs_2013.append(doc)
					if "Supplemental" in doc:
						s13 = s13 + 1
						registrant['docs_13'].append(doc) 
					if "Registration" in doc:
						s13 = s13 + 1
						registrant['docs_13'].append(doc) 
		
		if s13 == 2:
			complete_records13 = True
			registrant['complete_records13'] = True
		else:
			complete_records13 = False
			registrant['complete_records13'] = False

		if Payment.objects.filter(link__in=docs_2013) and complete_records13 == True:
			payments2013 = Payment.objects.filter(link__in=docs_2013).aggregate(total_pay=Sum('amount'))
			payments2013 = float(payments2013['total_pay'])
			registrant['payments2013'] = payments2013

		if Contact.objects.filter(registrant=reg_id,recipient__agency__in=["Congress", "House", "Senate", "White House"], meta_data__end_date__range=(datetime.date(2013,1,1), datetime.date.today()) ).exists():
			registrant['federal_lobbying'] = True
			
		if Contact.objects.filter(registrant=reg_id,recipient__agency="U.S. Department of State", meta_data__end_date__range=(datetime.date(2013,1,1), datetime.date.today()) ).exists():
			registrant['state_dept_lobbying'] = True
			
		if Contact.objects.filter(registrant=reg_id,recipient__agency="Media", meta_data__end_date__range=(datetime.date(2013,1,1), datetime.date.today()) ).exists():
			registrant['pr'] = True
		else:
			registrant['pr'] = False
			

	if Payment.objects.filter(registrant=reg).exists():
	 	registrant['total_payments'] = True

	if Disbursement.objects.filter(registrant=reg).exists():
	 	registrant['total_disbursements'] = True

	if Contact.objects.filter(registrant=reg).exists():
		contacts = Contact.objects.filter(registrant=reg).count()
		registrant['total_contacts'] = contacts
	
	if Contribution.objects.filter(registrant=reg).exists():
		registrant['total_contributions'] = True

	# contacts
	results['registrant'] =  registrant
	# active client info
	client_results = reg.clients.all()
	for client in client_results:
		c = {
			'client_name':client.client_name,
			'location': client.location.location,
			'client_id': client.id,
			'location': client.location.location,
			'location_id': client.location.id, 
			'active': True,
		}

		if Payment.objects.filter(client=client,registrant=reg, meta_data__processed=True).exists():
			c['payment'] = True
		if Disbursement.objects.filter(client=client,registrant=reg, meta_data__processed=True).exists():
			c['disbursement'] = True
		if Contact.objects.filter(client=client,registrant=reg, meta_data__processed=True).exists():
			total_contacts = Contact.objects.filter(client=client,registrant=reg, meta_data__processed=True).count()
			c['contact'] = total_contacts
		if ClientReg.objects.filter(client_id=client,reg_id=reg_id).exists():
			cr = ClientReg.objects.get(client_id=client,reg_id=reg_id)
			c['primary_contractor'] = cr.reg_id.reg_name
			c['primary_contractor_id'] = cr.reg_id.reg_id
			c['description'] = cr.description

		clients.append(c)
	results['clients'] = clients

	# terminated client info
	terminated_results = reg.terminated_clients.all()
	for client in terminated_results:
		client_id = int(client.id)
		c = {
			'client_name':client.client_name,
			'location': client.location.location,
			'client_id': client_id,
			'location': client.location.location,
			'location_id': client.location.id, 
			'active': False,
		}

		if Payment.objects.filter(client=client,registrant=reg, meta_data__processed=True).exists():
			c['payment'] = True
		if Disbursement.objects.filter(client=client,registrant=reg, meta_data__processed=True).exists():
			c['disbursement'] = True
		if Contact.objects.filter(client=client,registrant=reg, meta_data__processed=True).exists():
			total_contacts = Contact.objects.filter(client=client, registrant=reg, meta_data__processed=True).count()
			c['contact'] = total_contacts
		if ClientReg.objects.filter(client_id=client,reg_id=reg_id).exists():
			cr = ClientReg.objects.get(client_id=client,reg_id=reg_id)
			c['primary_contractor'] = cr.reg_id.reg_name
			c['primary_contractor_id'] = cr.reg_id.reg_id
			c['description'] = cr.description

		clients.append(c)
	results['terminated_clients'] = terminated_clients
	results = json.dumps({'results': results }, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")

## tables
def contact_table(request):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied
	results = []
	query_params = {"meta_data__processed": True}

	### add date paras
	title = []
	# this can't be later in the query or it turns in to a trademark symbol
	if request.GET.get('reg_id'):
		reg_id = request.GET.get('reg_id')
		registrant = Registrant.objects.get(reg_id=reg_id)
		query_params['registrant'] = registrant
		title.append({'id':reg_id, 'text':registrant.reg_name, "type":'reg' })
	
	if request.GET.get('doc_id'):
		doc_id = request.GET.get('doc_id')
		doc = Document.objects.get(id=doc_id)
		url = doc.url
		query_params['link'] = url
		text = "Document " + str(doc_id)
		title.append({'id':doc_id, 'text':text, "type": 'form'})

	if request.GET.get('client_id'):
		client_id = int(request.GET.get('client_id'))
		client = Client.objects.get(id=client_id)
		query_params['client'] = client
		title.append({'id':client_id, 'text':str(client.client_name), "type": 'client'})

	if request.GET.get('recipient_id'):
		recip_id = int(request.GET.get('recipient_id'))
		recip = Recipient.objects.get(id=recip_id)
		query_params['recipient'] = recip
		title.append({'id':recip_id, 'text':str(recip.name), "type": 'recipient'})

	if request.GET.get('contact_id'):	
		contact_id = int(request.GET.get('contact_id'))
		query_params['id'] = contact_id
		t = "Contact record " + str(contact_id)
		title.append({'id':None, 'text': t, "type": 'contact'})

	if request.GET.get('location_id'):
		loc_id = int(request.GET.get('location_id'))
		clients = Client.objects.filter(location__id=loc_id)
		query_params['client__in'] = clients
		location = Location.objects.get(id=loc_id)
		location = location.location
		title.append({'id':loc_id, 'text':location, "type": 'location'})

	if request.GET.get('sort'):
		sort = request.GET.get('sort')
	else:
		sort = '-date'	

	contact_pool = Contact.objects.filter(**query_params).order_by(sort)
	
	if request.GET.get('p'):
		p = int(request.GET.get('p'))
	else:
		p = 1
	page = {}	
	page['page'] = p
	page['num_pages'] = int(contact_pool.count())/20

	paginate_contacts = paginate(contact_pool, p)
	page_of_contacts = paginate_contacts[0:]

	count = 1
	for contact in page_of_contacts:
		record = {}
		url = contact.link
		doc = Document.objects.get(url=url)

		contacts = []
		for r in contact.recipient.all():
			person = {}
			name = namebuilder(r) 
			recipient_id = r.id
			if name == '':
				recipient_id = None
			contacts.append({"name":name, "recipient_id":recipient_id})
		record['contact'] =  contacts

		if count %2 == 0:
			record['row'] = "even"
		else:
			record['row'] = "odd"
		count += 1
		
		date = contact.date
		if date == None:
			md = MetaData.objects.get(link=url)
			date = md.end_date
			try:
				date = date.strftime("%m/%d/%Y")
				date = "*" + date 
			except:
				date = ''
		else:
			date = date.strftime("%m/%d/%Y")
		record['date'] = date
		
		employee = ''
		for l in contact.lobbyist.all():
			employee = employee + l.lobbyist_name + ", "
		record['employee'] = employee
		record['client_id'] = contact.client.id
		record['client'] = contact.client.client_name
		record['doc_id'] = doc.id
		record['description'] = contact.description
		record['registrant'] = contact.registrant.reg_name
		record['reg_id'] = contact.registrant.reg_id

		results.append(record)

	buttons = {}
	try:
		if Payment.objects.filter(**query_params).exists():
			buttons['payment'] = True
	except:
		pass
	try:
		if Disbursement.objects.filter(**query_params).exists():
			buttons['disbursement'] = True
	except:
		pass
	try:
		if Contribution.objects.filter(**query_params).exists():
			buttons['contribution'] = True
	except:
		pass

	results = json.dumps({'results':results, 'title':title, 'buttons': buttons, 'page':page}, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")

def namebuilder(r):
	if r.name == "unknown":
		return ''
	contact_name = ''
	if r.name != None and r.name != '':
		contact_name = contact_name + r.name
	if r.office_detail != None and r.office_detail != '':
		contact_name = contact_name + ", office: " + r.office_detail
	if r.agency != None and r.agency != '':
		contact_name = contact_name + ", agency: " + r.agency

	return contact_name

def payment_table(request):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied
	
	results = []
	query_params = {"meta_data__processed": True}
	title = []

	if request.GET.get('reg_id'):
		reg_id = request.GET.get('reg_id')
		registrant = Registrant.objects.get(reg_id=reg_id)
		query_params['registrant'] = registrant
		title.append({'id':reg_id, 'text':registrant.reg_name, "type":'reg' })

	if request.GET.get('doc_id'):
		doc_id = request.GET.get('doc_id')
		doc = Document.objects.get(id=doc_id)
		url = doc.url
		query_params['link']= url 
		text = "Document " + str(doc_id)
		title.append({'id':doc_id, 'text':text, "type": 'form'})

	if request.GET.get('client_id'):
		client_id = int(request.GET.get('client_id'))
		client = Client.objects.get(id=client_id)
		query_params['client'] = client
		title.append({'id':client_id, 'text':str(client.client_name), "type": 'client'})
	
	if request.GET.get('payment_id'):
		payment_id = int(request.GET.get('payment_id'))
		query_params['id'] = int(payment_id)
		t = "Payment record " + str(payment_id)
		title.append({'id':None, 'text': t, "type": 'payment'})
	
	if request.GET.get('location_id'):
		loc_id = int(request.GET.get('location_id'))
		clients = Client.objects.filter(location__id=loc_id)
		query_params['client__in'] = clients
		location = Location.objects.get(id=loc_id)
		location = location.location
		title.append({'id':loc_id, 'text':location, "type": 'location'})

	if request.GET.get('sort'):
		sort = request.GET.get('sort')
	else:
		sort = '-date'	

	payment_pool = Payment.objects.filter(**query_params).order_by(sort)
	
	if request.GET.get('p'):
		p = int(request.GET.get('p'))
	else:
		p = 1
	page = {}	
	page['page'] = p
	page['num_pages'] = int(payment_pool.count())/20
	paginate_payments = paginate(payment_pool, p)
	page_of_payments = paginate_payments[0:]

	count = 1
	for payment in page_of_payments:
		record = {}
		url = payment.link
		doc = Document.objects.get(url=url)
		record['doc_id'] = doc.id
		record['purpose'] = payment.purpose
		record['client'] = payment.client.client_name
		record['client_id'] = payment.client.id
		record['registrant'] = payment.registrant.reg_name
		record['reg_id'] = payment.registrant.reg_id
		record['amount'] = float(payment.amount)
		if payment.subcontractor != None:
			record['subcontractor'] = payment.subcontractor.reg_name
			record['subcontractor_id'] = payment.subcontractor.reg_id
		date = payment.date
		if date == None:
			md = MetaData.objects.get(link=url)
			date = md.end_date
			try:
				date = date.strftime("%m/%d/%Y")
				date = "*" + date 
			except:
				date = ''
		else:
			date = date.strftime("%m/%d/%Y")
		record['date'] = date	
		results.append(record)

		if count %2 == 0:
			record['row'] = "even"
		else:
			record['row'] = "odd"
		count = count + 1

	buttons = {}
	try:
		if Contact.objects.filter(**query_params).exists():
			buttons['contact'] = True
	except:
		pass
	try:
		if Disbursement.objects.filter(**query_params).exists():
			buttons['disbursement'] = True
	except:
		pass
	try:
		if Contribution.objects.filter(**query_params).exists():
			buttons['contribution'] = True
	except:
		pass

	results = json.dumps({'results':results, 'title':title, 'buttons':buttons, 'page':page}, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")

def disbursement_table(request):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied
	
	results = []
	query_params = {"meta_data__processed": True}
	title = []

	if request.GET.get('reg_id'):
		reg_id = request.GET.get('reg_id')
		registrant = Registrant.objects.get(reg_id=reg_id)
		query_params['registrant'] = registrant
		title.append({'id':reg_id, 'text':registrant.reg_name, "type":'reg' })

	if request.GET.get('doc_id'):
		doc_id = request.GET.get('doc_id')
		doc = Document.objects.get(id=doc_id)
		url = doc.url
		query_params['link']= url 
		text = "Document " + str(doc_id)
		title.append({'id':doc_id, 'text':text, "type": 'form'})

	if request.GET.get('client_id'):
		client_id = int(request.GET.get('client_id'))
		client = Client.objects.get(id=client_id)
		query_params['client'] = client
		title.append({'id':client_id, 'text':str(client.client_name), "type": 'client'})
	
	if request.GET.get('disbursement_id'):
		disbursement_id = int(request.GET.get('disbursement_id'))
		query_params['id'] = int(disbursement_id)
		t = "Disbursement record " + str(disbursement_id)
		title.append({'id':None, 'text': t, "type": 'disbursement'})
	
	if request.GET.get('location_id'):
		loc_id = int(request.GET.get('location_id'))
		clients = Client.objects.filter(location__id=loc_id)
		query_params['client__in'] = clients
		location = Location.objects.get(id=loc_id)
		location = location.location
		title.append({'id':loc_id, 'text':location, "type": 'location'})
	
	if request.GET.get('sort'):
		sort = request.GET.get('sort')
	else:
		sort = '-date'	

	disbursement_pool = Disbursement.objects.filter(**query_params).order_by(sort)
	
	if request.GET.get('p'):
		p = int(request.GET.get('p'))
	else:
		p = 1
	page = {}	
	page['page'] = p
	page['num_pages'] = int(disbursement_pool.count())/20
	paginate_disbursements = paginate(disbursement_pool, p)
	page_of_disbursements = paginate_disbursements[0:]

	count = 1
	for disbursement in page_of_disbursements:
		record = {}
		url = disbursement.link
		doc = Document.objects.get(url=url)
		record['doc_id'] = doc.id
		record['purpose'] = disbursement.purpose
		record['client'] = disbursement.client.client_name
		record['client_id'] = disbursement.client.id
		record['registrant'] = disbursement.registrant.reg_name
		record['reg_id'] = disbursement.registrant.reg_id
		record['amount'] = float(disbursement.amount)
		if disbursement.subcontractor != None:
			record['subcontractor'] = disbursement.subcontractor.reg_name
			record['subcontractor_id'] = disbursement.subcontractor.reg_id
		date = disbursement.date
		if date == None:
			md = MetaData.objects.get(link=url)
			date = md.end_date
			try:
				date = date.strftime("%m/%d/%Y")
				date = "*" + date 
			except:
				date = ''
		else:
			date = date.strftime("%m/%d/%Y")
		record['date'] = date	
		results.append(record)

		if count %2 == 0:
			record['row'] = "even"
		else:
			record['row'] = "odd"
		count = count + 1

	buttons = {}
	try:
		if Payment.objects.filter(**query_params).exists():
			buttons['payment'] = True
	except:
		pass
	try:
		if Contact.objects.filter(**query_params).exists():
			buttons['contact'] = True
	except:
		pass
	try:
		if Contribution.objects.filter(**query_params).exists():
			buttons['contribution'] = True
	except:
		pass

	results = json.dumps({'results':results, 'title':title, 'buttons':buttons, 'page':page}, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")

def contribution_table(request):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied

	results = []
	query_params = {"meta_data__processed": True}
	title = []

	if request.GET.get('reg_id'):
		reg_id = request.GET.get('reg_id')
		registrant = Registrant.objects.get(reg_id=reg_id)
		query_params['registrant'] = registrant
		title.append({'id':reg_id, 'text':registrant.reg_name, "type":'reg' })

	if request.GET.get('doc_id'):
		doc_id = request.GET.get('doc_id')
		doc = Document.objects.get(id=doc_id)
		url = doc.url
		query_params['link']= url 
		text = "Document " + str(doc_id)
		title.append({'id':doc_id, 'text':text, "type": 'form'})

	if request.GET.get('recipient_id'):
		recipient_id = int(request.GET.get('recipient_id'))
		recip = Recipient.objects.get(id=recipient_id)
		query_params['recipient'] = recip
		title.append({'id':recipient_id, 'text':recip.name, "type": 'recipient'})

	if request.GET.get('contribution_id'):
		contribution_id = int(request.GET.get('contribution_id'))
		query_params['id'] = contribution_id
		text = "Contribution record " + str(contribution_id)
		title.append({'id':None, 'text': text, "type": 'recipient'})
	
	if request.GET.get('employee_id'):
		lobbyist_id = int(request.GET.get('employee_id'))
		lobbyist = Lobbyist.objects.get(id=lobbyist_id)
		lobbyist_name = lobbyist.lobbyist_name
   		pac_name = lobbyist.PAC_name
   		# one of these will be an empty string
   		text = str(lobbyist_name) + str(pac_name)
		query_params['lobbyist'] = lobbyist
		title.append({'id':None, 'text': text, "type": 'recipient'})
	
	if request.GET.get('sort'):
		sort = request.GET.get('sort')
	else:
		sort = '-date'	

	contribution_pool = Contribution.objects.filter(**query_params).order_by(sort)
	
	if request.GET.get('p'):
		p = int(request.GET.get('p'))
	else:
		p = 1
	page = {}	
	page['page'] = p
	page['num_pages'] = int(contribution_pool.count())/20
	paginate_contributions = paginate(contribution_pool, p)
	page_of_contributions = paginate_contributions[0:]

	count = 1
	for contribution in page_of_contributions:
		record = {}
		url = contribution.link
		doc = Document.objects.get(url=url)
		record['doc_id'] = doc.id
		amount = contribution.amount
		record['amount'] = float(amount)
		record['recipient'] = contribution.recipient.name
		record['recipient_id'] = contribution.recipient.id
		record['registrant'] = contribution.registrant.reg_name
		record['reg_id'] = contribution.registrant.reg_id
		
		if record.has_key('contributor'):
			record['contributor'] = str(contribution.lobbyist)
			record['contributor_id'] = contribution.lobbyist.id
		
		date = contribution.date
		if date == None:
			md = MetaData.objects.get(link=url)
			date = md.end_date
			try:
				date = date.strftime("%m/%d/%Y")
				date = "*" + date 
			except:
				date = ''
		else:
			date = date.strftime("%m/%d/%Y")

		if count %2 == 0:
			record['row'] = "even"
		else:
			record['row'] = "odd"
		count = count + 1

		record['date'] = date	
		results.append(record)


	buttons = {}
	try:
		if Payment.objects.filter(**query_params).exists():
			buttons['payment'] = True
	except:
		pass
	try:
		if Contact.objects.filter(**query_params).exists():
			buttons['contact'] = True
	except:
		pass
	try:
		if Disbursement.objects.filter(**query_params).exists():
			buttons['disbursement'] = True
	except:
		pass

	results = json.dumps({'results':results, 'title':title, 'buttons':buttons, 'page':page}, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")
	
# 2013 totals pages
def reg_2013(request):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied
	
	# this grabs the totals that are created in api management command totaler.py
	this_filepath = os.path.abspath(__file__)
	this_parent_dir = os.path.dirname(this_filepath) 
	file_name = os.path.join(this_parent_dir, "computations/reg13.json")
	data = open(file_name, 'r')
	results = data.read()
	data.close()
	return HttpResponse(results, mimetype="application/json")


## we could make this a static file in the future and update weekly or whatever
# Map endpoint
def map(request):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied

	# this grabs the totals that are created in api management command totaler.py
	this_filepath = os.path.abspath(__file__)
	this_parent_dir = os.path.dirname(this_filepath) 
	file_name = os.path.join(this_parent_dir, "computations/map.json")
	data = open(file_name, 'r')
	results = data.read()
	data.close()
	return HttpResponse(results, mimetype="application/json")

# client totals
def client13(request):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied

	# this grabs the totals that are created in api management command totaler.py
	this_filepath = os.path.abspath(__file__)
	this_parent_dir = os.path.dirname(this_filepath) 
	file_name = os.path.join(this_parent_dir, "computations/client13.json")
	data = open(file_name, 'r')
	results = data.read()
	data.close()
	return HttpResponse(results, mimetype="application/json")

def location13(request):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied

	# this grabs the totals that are created in api management command totaler.py
	this_filepath = os.path.abspath(__file__)
	this_parent_dir = os.path.dirname(this_filepath) 
	file_name = os.path.join(this_parent_dir, "computations/location13.json")
	data = open(file_name, 'r')
	results = data.read()
	data.close()
	return HttpResponse(results, mimetype="application/json")

# I am using this for clients now
def location_list(request):
	locations = Location.objects.all()
	results = []
	for l in locations:
		clients = Client.objects.filter(location=l)
		for client in clients:
			record = {}
			record['client_id'] = client.id
			record['client_name'] = client.client_name
			record['location_id'] = l.id
			record['location_name'] = l.location
			print record
			results.append(record)

	results = json.dumps({'results':results}, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")


def search(request):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied

	if request.GET.get('q'):
		q = request.GET.get('q')
	else:
		results = json.dumps({'message':'No search terms'}, separators=(',',':'))
		return HttpResponse(results, mimetype="application/json")
	
	# I could make them all 1
	if request.GET.get('clientpage'):
		clientpage = request.GET.get('clientpage')
	else:
		clientpage = 1
	if request.GET.get('regpage'):
		regpage = request.GET.get('regpage')
	else:
		regpage = 1
	if request.GET.get('peoplepage'):
		peoplepage = request.GET.get('peoplepage')
	else:
		peoplepage = 1
	if request.GET.get('armspage'):
		armspage = request.GET.get('armspage')
	else:
		armspage = 1
	if request.GET.get('interactionspage'):
		interactionspage = request.GET.get('interactionspage')
	else:
		interactionspage = 1
	if request.GET.get('locationpage'):
		locationpage = request.GET.get('locationpage')
	else:
		locationpage = 1
	if request.GET.get('docpage'):
		docpage = request.GET.get('docpage')
	else:
		docpage = 1

	clients = search_client(q, int(clientpage))
	regs = search_registrant(q, int(regpage))
	people_org = search_recipients(q, int(peoplepage))
	arms = search_arms(q, int(armspage))
	interactions = search_interactions(q, int(interactionspage))
	locations = search_locations(q, int(locationpage))
	docs =  search_text(q, int(docpage))

	results = {}
	results['clients'] = clients
	results['registrants'] = regs
	results['people_org'] =  people_org
	results['arms'] = arms
	results['interactions'] = interactions
	results['locations'] = locations
	results['docs'] = docs

	results = json.dumps(results, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")

def search_more(request):
	if not request.GET.get('key') == API_PASSWORD:
		raise PermissionDenied

	results = {}

	if request.GET.get('q'):
		q = request.GET.get('q')
	else:
		results = json.dumps({'message':'No search terms'}, separators=(',',':'))
		return HttpResponse(results, mimetype="application/json")

	if request.GET.get('clientpage'):
		clientpage = request.GET.get('clientpage')
		clients = search_client(q, int(clientpage))
		results['clients'] = clients

	if request.GET.get('regpage'):
		regpage = request.GET.get('regpage')
		regs = search_registrant(q, int(regpage))
		results['registrants'] = regs

	if request.GET.get('peoplepage'):
		peoplepage = request.GET.get('peoplepage')
		people_org = search_recipients(q, int(peoplepage))
		results['people_org'] =  people_org
	
	if request.GET.get('armspage'):
		armspage = request.GET.get('armspage')
		arms = search_arms(q, int(armspage))
		results['arms'] = arms
	
	if request.GET.get('interactionspage'):
		interactionspage = request.GET.get('interactionspage')
		interactions = search_interactions(q, int(interactionspage))
		results['interactions'] = interactions
	
	if request.GET.get('locationpage'):
		locationpage = request.GET.get('locationpage')
		locations = search_locations(q, int(locationpage))
		results['locations'] = locations

	if request.GET.get('docpage'):
		docpage = request.GET.get('docpage')
		docs =  search_text(q, int(docpage))
		results['docs'] = docs

	results = json.dumps(results, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")
