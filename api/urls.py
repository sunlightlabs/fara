from django.conf.urls import *


urlpatterns = patterns('',
   url(r'^docs', 'api.views.incoming_fara', name= 'incoming-fara'),
   url(r'^proposed-arms', 'api.views.incoming_arms', name='incoming-arms' ),
   url(r'^arms-profile', 'api.views.incoming_arms', name='arms-profile' ),
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
   url(r'^search', 'api.views.search', name='search'),
   url(r'^map', 'api.views.map', name='map'),
   url(r'^lobbying-2013', 'api.views.client13', name='client13'),
   url(r'^location-2013', 'api.views.location13', name='location13'),
   # to check status
   url(r'^test', 'api.views.test', name='test'),
)