import datetime
import json

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.db.models import Sum

from fara_feed.models import Document
from FaraData.models import Registrant, Payment, Contact, Contribution, Recipient, Client, Disbursement
from fara.local_settings import API_PASSWORD
#from arms_sales.models import Proposed

def paginate(form, page):
	paginator = Paginator(form, 20)
	try:
		form = paginator.page(page)
	except PageNotAnInteger:
		form = paginator.page(1)
	except EmptyPage:
		form = paginator.page(paginator.num_pages)
	return form


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
	query_params['stamp_date__range'] = (datetime.date(2012,1,1), datetime.date.today())

	if request.GET.get('p'):
		page = int(request.GET.get('p'))
	else:
		page = 1
	
	# Would like to make this not case sensitive 
	if request.GET.get('type'):
		form_type = request.GET.get('type')
		form_type = [form_type]
	else:
		form_type = ['Supplemental', 'Amendment', 'Exhibit AB', 'Registration']
	query_params['doc_type__in']=form_type


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

	print query_params
	doc_pool = Document.objects.filter(**query_params).order_by('-stamp_date')
	paginate_docs = paginate(doc_pool, page)
	page_of_docs = paginate_docs[0:]

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

	if Registrant.objects.filter(reg_id=reg_id).exists():
		reg = Registrant.objects.get(reg_id=reg_id)
		results['reg_name'] = reg.reg_name
		client_results = reg.clients.all()
		clients = []
		for client in client_results:
			c = {
				'client_name':client.client_name,
				'location': client.location.location,
				'client_id': client.id,
			}
			
			if Payment.objects.filter(link=url,client=client).exists():
				payment = Payment.objects.filter(link=url,client=client).aggregate(total_pay=Sum('amount'))
				total_pay = float(payment['total_pay'])
				c['payment'] = total_pay

			if Contact.objects.filter(link=url,client=client).exists():
				total_contacts = Contact.objects.filter(link=url,client=client).count()
				c['contact'] = total_contacts

			clients.append(c)
		results['clients'] = clients
	print results
	results = json.dumps({'results': results}, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")

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

		if Contribution.objects.filter(recipient=recip_id).exists():
			contribution = Contribution.objects.filter(recipient=recip_id).aggregate(total_pay=Sum('amount'))
			recipient['total_contribution'] = float(contribution['total_pay'])
		
		if Contact.objects.filter(recipient=recip_id).exists():
			recipient['contacts'] = Contact.objects.filter(recipient=recip_id).count()

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
	client['client_name'] = c.client_name
	client['address'] = c.address1
	client['city'] = c.city
	client['state'] = c.state
	client['zip_code'] = c.zip_code
	client['client_type'] = c.client_type
	client['description'] = c.description

	# don't know how to incorporate this yet
	if Contact.objects.filter(client=client_id).exists():
		client['contacts'] = Contact.objects.filter(client=client_id).count()

	if Payment.objects.filter(client=client_id).exists():
		payment = Payment.objects.filter(client=client_id,subcontractor__isnull=True).aggregate(total_pay=Sum('amount'))
		client['total_payment'] = float(payment['total_pay'])

	if Disbursement.objects.filter(client=client_id).exists():
		disbursement = Disbursement.objects.filter(client=client_id,subcontractor__isnull=True).aggregate(total_pay=Sum('amount'))
		client['total_disbursement'] = float(disbursement['total_pay'])

	results = json.dumps({'results': client }, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")

# def location_profile(request, loc_id):
	# if not request.GET.get('key') == API_PASSWORD:
	# 	raise PermissionDenied
# 	#arms = 


# def reg_profile(request, reg_id):
	# if not request.GET.get('key') == API_PASSWORD:
	# 	raise PermissionDenied





