from django.conf.urls import *
from piston.resource import Resource
from piston.authentication import HttpBasicAuthentication
from handlers import *

auth = HttpBasicAuthentication(realm="Narnia")
metadata_handler = Resource(MetaDataHandler, authentication=auth)
registrant_handler = Resource(RegistrantDataHandler, authentication=auth)
doc_handler = Resource(DocHandler, authentication=auth) 
loc_handler = Resource(LocationHandler, authentication=auth)
proposed_handler = Resource(ProposedHandler, authentication=auth)

urlpatterns = patterns('',
   url(r'^docs', doc_handler),
   url(r'^agentfeed',  'api.views.incoming_fara', name= 'incoming-fara'),
   url(r'^doc_profile/(\d+)/','api.views.doc_profile', name= 'doc-profile'),
   url(r'^location', loc_handler),
   url(r'^metadata/(\d+)/', metadata_handler),
   url(r'^registrant', registrant_handler),
   url(r'^proposed_arms', proposed_handler),

)