from django.conf.urls import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from handlers import DocumentHandler, RegDocHandler

#auth = HttpBasicAuthentication(realm="Narnia")
document_handler = Resource(DocumentHandler)
regdoc_handler = Resource(RegDocHandler)

urlpatterns = patterns('',
   url(r'^doc/(\d+)/', document_handler),
   url(r'^docs', document_handler),
   url(r'^regdocs/(\d+)/', regdoc_handler),
   #url(r'^blogposts/', blogpost_handler),
)