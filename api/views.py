import datetime
import json

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import PermissionDenied

from fara_feed.models import Document
from FaraData.models import Registrant
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

	if request.GET.get('p'):
		page = int(request.GET.get('p'))
	else:
		page = 1
		
	doc_pool = Document.objects.filter(doc_type__in=['Supplemental', 'Amendment', 'Exhibit AB', 'Registration'],stamp_date__range=(datetime.date(2012,1,1), datetime.date.today())).order_by('-stamp_date')
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
			}
			clients.append(c)
		results['clients'] = clients

	results = json.dumps({'results': results}, separators=(',',':'))
	return HttpResponse(results, mimetype="application/json")






# json_choices = json.dumps(choice_list, separators=(',',':'))
# client_choices = makeJson(client_choices, 'client_name')
# return HttpResponse(client_choices, mimetype="application/json")
