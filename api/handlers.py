from piston.handler import BaseHandler
from fara_feed.models import *
# from FaraData.models import *

class DocumentHandler(BaseHandler):
	allowed_methods = ('GET',)
	model = Document   

	def read(self, request, doc_id=None):
		base = Document.objects
		
		if doc_id:
			return base.get(id=doc_id)
		else:
			return base.all().order_by('-stamp_date')
