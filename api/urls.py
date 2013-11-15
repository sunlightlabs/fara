from django.conf.urls.defaults import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from mysite.myapp.api.handlers import BlogpostHandler

auth = HttpBasicAuthentication(realm="Narnia")
document_handler = Resource(DocumentHandler)

urlpatterns = patterns('',
   url(r'^docs/(\d+)/', document_handler),
   #url(r'^blogposts/', blogpost_handler),
)