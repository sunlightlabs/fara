
import datetime

from piston.handler import BaseHandler

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from fara_feed.models import Document
from FaraData.models import *
from arms_sales.models import Proposed



def format_link_bit(link):
	if link[:25] != "http://www.fara.gov/docs/":
		link = "http://www.fara.gov/docs/" + link
	if link[-4:] != ".pdf":
		link = link + ".pdf"
	link = link.replace("_", "-")
	return link

def paginate(form, page):
	paginator = Paginator(form, 20)
	try:
		form = paginator.page(page)
	except PageNotAnInteger:
		form = paginator.page(1)
	except EmptyPage:
		form = paginator.page(paginator.num_pages)
	return form

class DocHandler(BaseHandler):
	allowed_methods = ('GET',)
	model = Document
	fields = ('id', 'url', 'reg_id', 'doc_type', 'processed', 'stamp_date')

	def read(self, request):
		if request.method == 'GET':
			if request.GET.get('doc_id'):
				doc_id = int(request.GET.get('doc_id'))
				return Document.objects.get(id=doc_id)
			if request.GET.get('p'):
				page = int(request.GET.get('p'))
			else:
				page = 1
		
		base = Document.objects.filter(doc_type__in=['Supplemental', 'Amendment', 'Exhibit AB', 'Registration'],stamp_date__range=(datetime.date(2012,1,1), datetime.date.today())).order_by('-stamp_date')
		form = paginate(base, page)
		page = form[0]
		results = form[0:]

		return results, page

# I should make this an option for the previous 
class RegDocHandler(BaseHandler):
	allowed_methods = ('GET',)
	model = Document
	fields = ('url', 'reg_id', 'doc_type', 'processed', 'stamp_date')

	def read(self, request, reg_id=None):
		base = Document.objects

		if reg_id:
			return base.filter(reg_id=reg_id)



class MetaDataHandler(BaseHandler):
	allowed_methods = ('GET',)
	model = MetaData
	# notes are not viewable from the API
	fields = ( 'processed', 'form', 'link', 'upload_date', 'end_date','reviewed', 'is_amendment')

	def read(self, request, form_id=None):
		base = MetaData.objects
		if form_id:
			return base.filter(form=form_id)

class RegistrantDataHandler(BaseHandler):
	allowed_methods = ('GET',)
	model = Registrant
	fields = ('reg_id', 'reg_name', 'address', 'city', 'state', 'zip_code', 'country', 'terminated_clients', 'clients')

	def read(self, request):
		if request.method == 'GET':
			if request.GET.get('reg_id'):
				reg_id = int(request.GET.get('reg_id'))
				return Registrant.objects.get(reg_id=reg_id)
			if request.GET.get('p'):
				page = int(request.GET.get('p'))
			else:
				page = 1
		base = Registrant.objects.all().order_by('reg_name')
		form = paginate(base, page)
		page = form[0]
		results = form[0:]

		return (results, page)

class LocationHandler(BaseHandler):
	allowed_methods = ('GET',)
	model = Location
	fields = ('location', 'region', 'id')

	def read(self, request):
		if request.GET.get('id'):
			id = int(request.GET.get('id'))
			return Location.objects.get(id=id)
		else:
			base = Location.objects.all()
			return base

class ProposedHandler(BaseHandler):
	allowed_methods = ('GET',)
	model = Proposed
	fields = ('date', 'title', 'id', 'text', 'location', 'pdf_url')

	def read(self, request):
		if request.method == 'GET':
			if request.GET.get('doc_id'):
				doc_id = int(request.GET.get('doc_id'))
				return Proposed.objects.get(id=doc_id)
			if request.GET.get('p'):
				page = int(request.GET.get('p'))
			else:
				page = 1
			base = Proposed.objects.all()
			form = paginate(base, page)
			page = form[0]
			results = form[0:]
			return {"results":results, 'page':page}

