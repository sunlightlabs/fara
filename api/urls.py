from django.conf.urls import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from handlers import *

auth = HttpBasicAuthentication(realm="Narnia")
regdoc_handler = Resource(RegDocHandler, authentication=auth)
metadata_handler = Resource(MetaDataHandler, authentication=auth)
registrant_handler = Resource(RegistrantDataHandler, authentication=auth)
contactdoc_handler = Resource(ContactDocHandler, authentication=auth)
contribdoc_handler = Resource(ContribDocHandler, authentication=auth)
paymentdoc_handler = Resource(PaymentDocHandler, authentication=auth)
disbursedoc_handler = Resource(DisburseDocHandler, authentication=auth)
doc_handler = Resource(Dochandler, authentication=auth) 
loc_handler = Resource(Locationhandler, authentication=auth)

urlpatterns = patterns('',
   url(r'^docs', doc_handler),
   url(r'^location', loc_handler),
   url(r'^regdocs/(\d+)/', regdoc_handler),
   url(r'^metadata/(\d+)/', metadata_handler),
   url(r'^registrant', registrant_handler),
   url(r'^contactbydoc/(?P<link>\w+)/', contactdoc_handler),
   url(r'^contribbydoc/(?P<link>\w+)/', contribdoc_handler),
   url(r'^paymentbydoc/(?P<link>\w+)/', paymentdoc_handler),
   url(r'^disbursementbydoc/(?P<link>\w+)/', disbursedoc_handler),
)