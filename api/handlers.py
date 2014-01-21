
import datetime

from piston.handler import BaseHandler

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from fara_feed.models import *
from FaraData.models import *



def format_link_bit(link):
	if link[:25] != "http://www.fara.gov/docs/":
		link = "http://www.fara.gov/docs/" + link
	if link[-4:] != ".pdf":
		link = link + ".pdf"
	link = link.replace("_", "-")
	return link

def paginate(form, page):
	print 3
	paginator = Paginator(form, 20)
	try:
		form = paginator.page(page)
	except PageNotAnInteger:
		form = paginator.page(1)
	except EmptyPage:
		form = paginator.page(paginator.num_pages)
	print form
	return form

class PagedDochandler(BaseHandler):
	allowed_methods = ('GET',)
	model = Document
	fields = ('url', 'reg_id', 'doc_type', 'processed', 'stamp_date', 'id')
	print 1   

	def read(self, request, page=None):
		print 2
		base = Document.objects.filter(doc_type__in=['Supplemental', 'Amendment', 'Exhibit AB', 'Registration'],stamp_date__range=(datetime.date(2012,1,1), datetime.date.today())).order_by('-stamp_date')
		form = paginate(base, page)
		page = form[0]
		results = form[0:]

		return results, page


class DocumentHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = Document
    fields = ('url', 'reg_id', 'doc_type', 'processed', 'stamp_date')   

    def read(self, request, doc_id=None):
            base = Document.objects
            # document type would make for good kwarg
            if doc_id:
                    return base.get(id=doc_id)
            else:
                    return base.all().order_by('-stamp_date')

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

	def read(self, request, reg_id=None):
		base = Registrant.objects
		if reg_id:
			return base.filter(reg_id=reg_id)
		else:
			return base.all()

class ContactDocHandler(BaseHandler):
	allowed_methods = ('GET',)
	model = Contact

	def read(self, request, link=None):
		base = Contact.objects
		link = format_link_bit(link)
		return base.filter(link=link)

class ContribDocHandler(BaseHandler):
	allowed_methods = ('GET',)
	model = Contribution
	
	def read(self, request, link=None):
		base = Contribution.objects
		link = format_link_bit(link)
		return base.filter(link=link)

class PaymentDocHandler(BaseHandler):
	allowed_methods = ('GET',)
	model = Payment
	
	def read(self, request, link=None):
		base = Payment.objects
		link = format_link_bit(link)
		return base.filter(link=link)

class DisburseDocHandler(BaseHandler):
	allowed_methods = ('GET',)
	model = Disbursement
	
	def read(self, request, link=None):
		base = Disbursement.objects
		link = format_link_bit(link)
		return base.filter(link=link)



#class ContactHandler(BaseHandler):
	#Contact by Registrant



#Contact by Client
#Contact by Recipient
#Contact by Agency
