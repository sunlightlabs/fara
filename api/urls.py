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
   url(r'^docs', 'api.views.incoming_fara', name= 'incoming-fara'),
   url(r'^agentfeed',  proposed_handler),
   url(r'^metadata/(\d+)/', metadata_handler),
   url(r'^registrant', registrant_handler),
   url(r'^proposed-arms', 'api.views.incoming_arms', name='incoming-arms'),
   url(r'^recipient-profile/(\d+)/', 'api.views.recipient_profile', name='recipient-profile'),
   url(r'^client-profile/(\d+)/', 'api.views.client_profile', name= 'client-profile'),
   url(r'^place-profile/(\d+)/', 'api.views.location_profile', name= 'location-profile'),
   url(r'^reg-profile/(\d+)/', 'api.views.reg_profile', name= 'reg-profile'),
   url(r'^doc-profile/(\d+)/','api.views.doc_profile', name= 'doc-profile'),
   url(r'^contact-table', 'api.views.contact_table', name= 'contact-table'),
   url(r'^payment-table', 'api.views.payment_table', name= 'payment-table'),
   url(r'^disbursement-table', 'api.views.disbursement_table', name= 'disbursement-table'),
   url(r'^contribution-table', 'api.views.contribution_table', name= 'contribution-table'),
   url(r'^reg-2013', 'api.views.reg_2013', name= 'reg-2013'),
   url(r'^locations', 'api.views.location_list', name='location-list'),
)