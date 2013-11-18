from piston.handler import BaseHandler
from fara_feed.models import *
from FaraData.models import *

class DocumentHandler(BaseHandler):
	allowed_methods = ('GET',)
	model = Document   

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

	def read(self, request, reg_id=None):
		base = Document.objects

		if reg_id:
			return base.filter(reg_id=reg_id)
		else:
			return base.all().order_by('-stamp_date')


#class ContactHandler(BaseHandler):
	#Contact by Registrant



#Contact by Client
#Contact by Recipient
#Contact by Agency
