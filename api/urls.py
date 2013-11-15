from django.conf.urls import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from handlers import DocumentHandler

auth = HttpBasicAuthentication(realm="Narnia")
document_handler = Resource(DocumentHandler)

urlpatterns = patterns('',
   url(r'^docs/(\d+)/', document_handler),
   #url(r'^blogposts/', blogpost_handler),
)