from django.conf.urls import patterns, include, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #views for viewing
    url(r'^regview/', 'FaraData.reg_view.index', name='reg-view'),
    #data entry form
    #url(r'^entryform/', 'FaraData.entry_view.index', name='entryform'),
    url(r'^entersupplemental/(\d+)', 'FaraData.entry_view.index', name='enter-supplemental'),
    url(r'^registrant/create', 'FaraData.entry_view.registrant', name= 'create-registrant'),
    url(r'^lobbyist/create', 'FaraData.entry_view.lobbyist', name='create-lobbyist'),
    url(r'^client/create', 'FaraData.entry_view.client', name='create-client'),
    url(r'^recipient/create', 'FaraData.entry_view.recipient', name='create-recipient'),
    url(r'^contact/create', 'FaraData.entry_view.contact', name='create-contact'),
    url(r'^payment/create', 'FaraData.entry_view.payment', name='create-payment'),
    url(r'^contribution/create', 'FaraData.entry_view.contribution', name='create-contribution'),
    url(r'^disbursement/create', 'FaraData.entry_view.disbursement', name='create-disbursement'),
    url(r'^registrant/add_client', 'FaraData.entry_view.reg_client', name='add-client'),
    url(r'^registrant/add_terminated', 'FaraData.entry_view.terminated', name='add-terminated'),
    url(r'^registrant/add_lobbyist', 'FaraData.entry_view.reg_lobbyist', name='add-lobbyist'),
    url(r'^registrant/add_recipient', 'FaraData.entry_view.recipient', name='add-recipient'),
    url(r'^gift/create', 'FaraData.entry_view.gift', name='create-gift'),
    url(r'^metadata/create', 'FaraData.entry_view.metadata', name='metadata'),
    #json to generate choices for the form
    url(r'^formchoices/recip', 'FaraData.json_creator_view.recip_choice', name='json-recip-choices'),
    url(r'^formchoices/lobby', 'FaraData.json_creator_view.lobby_choice', name='json-lobby-choices'),
    url(r'^formchoices/client', 'FaraData.json_creator_view.client_choice', name='json-client-choices'),
    #Document managers
    url(r'^full_list/', 'fara_feed.document_select_view.full_list', name='full-list'),
    )
