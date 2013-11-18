from django.conf.urls import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from handlers import DocumentHandler, RegDocHandler, MetaDataHandler, RegistrantDataHandler

auth = HttpBasicAuthentication(realm="Narnia")
document_handler = Resource(DocumentHandler, authentication=auth)
regdoc_handler = Resource(RegDocHandler, authentication=auth)
metadata_handler = Resource(MetaDataHandler, authentication=auth)
registrant_handler = Resource(RegistrantDataHandler, authentication=auth)

urlpatterns = patterns('',
   url(r'^doc/(\d+)/', document_handler),
   url(r'^docs', document_handler),
   url(r'^regdocs/(\d+)/', regdoc_handler),
   url(r'^metadata/(\d+)/', metadata_handler),
   url(r'^registrant/(\d+)/', registrant_handler),
   url(r'^registrants', registrant_handler),
   #url(r'^blogposts/', blogpost_handler),
)