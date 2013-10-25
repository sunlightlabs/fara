from django.conf.urls import patterns, include, url
from django.contrib import admin

from FaraData.Feeds import LatestEntriesFeed, RegionFeed, DataEntryFeed

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #login view
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    #views for viewing #### GET RID OF THESE
    url(r'^regview/', 'FaraData.reg_view.index', name='reg-view'),
    url(r'^entersupplemental/(\d+)', 'FaraData.entry_view.index', name='enter-supplemental'),
    # functions for forms
    url(r'^registrant/create', 'FaraData.entry_view.registrant', name= 'create-registrant'),
    url(r'^registrant/new', 'FaraData.entry_view.new_registrant', name= 'new-registrant'),
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
    url(r'^stamp_date', 'FaraData.entry_view.stamp_date', name='stamp-date'),
    url(r'^location/create', 'FaraData.entry_view.location', name='location'),
    #Functions for fixing forms
    url(r'^amend_client', 'FaraData.entry_view.amend_client', name='amend-client'),
    url(r'^amend_registrant', 'FaraData.entry_view.amend_registrant', name='amend-registrant'),
    url(r'^amend_contact', 'FaraData.entry_view.amend_contact', name='amend-contact'),
    url(r'^amend_gift', 'FaraData.entry_view.amend_gift', name='amend-gift'),
    url(r'^contact_remove_recip', 'FaraData.entry_view.contact_remove_recip', name='contact-remove-recip'),
    url(r'^contact_remove_lobby', 'FaraData.entry_view.contact_remove_lobby', name='contact-remove-lobby'),
    url(r'^amend_payment', 'FaraData.entry_view.amend_payment', name='amend-payment'),
    url(r'^payment_remove_sub', 'FaraData.entry_view.payment_remove_sub', name='payment-remove-sub'),
    url(r'^amend_disbursement', 'FaraData.entry_view.amend_disbursement', name='amend-disbursement'),
    url(r'^disbursement_remove_sub', 'FaraData.entry_view.disbursement_remove_sub', name='disbursement-remove-sub'),
    url(r'^amend_contribution', 'FaraData.entry_view.amend_contribution', name='amend-contribution'),
    url(r'^gift_remove_recip', 'FaraData.entry_view.gift_remove_recip', name='remove-gift'),
    url(r'^delete_contact', 'FaraData.entry_view.delete_contact', name='delete-contact'),
    url(r'^delete_payment', 'FaraData.entry_view.delete_payment', name='delete-payment'),
    url(r'^delete_disbursement', 'FaraData.entry_view.delete_disbursement', name='delete-disbursement'),
    url(r'^delete_contribution', 'FaraData.entry_view.delete_contribution', name='delete-contribution'),
    url(r'^delete_gift', 'FaraData.entry_view.delete_gift', name='delete-gift'),
    #Easy fix forms
    url(r'^fix_contact/(\d+)', 'FaraData.entry_view.fix_contact', name='fix-contact'),
    url(r'^fix_payment/(\d+)', 'FaraData.entry_view.fix_payment', name='fix-payment'),
    url(r'^fix_disbursement/(\d+)', 'FaraData.entry_view.fix_disbursement', name='fix-disbursement'),
    url(r'^fix_contribution/(\d+)', 'FaraData.entry_view.fix_contribution', name='fix-contribution'),
    url(r'^fix_registrant/(\d+)/(\d+)', 'FaraData.entry_view.fix_registrant', name='fix-registrant'),
    url(r'^fix_client/(\d+)/(\d+)', 'FaraData.entry_view.fix_client', name='fix-client'),
    url(r'^fix_gift/(\d+)', 'FaraData.entry_view.fix_gift', name='fix-gift'),
    #Segmented supplemental
    url(r'^supplemental_base/(\d+)', 'FaraData.entry_view.supplemental_base', name='supplemental-base'),
    url(r'^supplemental_first/(\d+)', 'FaraData.entry_view.supplemental_first', name='supplemental-first'),
    url(r'^supplemental_contact/(\d+)', 'FaraData.entry_view.supplemental_contact', name='supplemental-contact'),
    url(r'^supplemental_payment/(\d+)', 'FaraData.entry_view.supplemental_payment', name='supplemental-payment'),
    url(r'^supplemental_disbursement/(\d+)', 'FaraData.entry_view.supplemental_disbursement', name='supplemental-disbursement'),
    url(r'^supplemental_gift/(\d+)', 'FaraData.entry_view.supplemental_gift', name='supplemental-gift'),
    url(r'^supplemental_contribution/(\d+)', 'FaraData.entry_view.supplemental_contribution', name='supplemental-contribution'),
    url(r'^supplemental_last/(\d+)', 'FaraData.entry_view.supplemental_last', name='supplemental-last'),
    #Segmented Registration
    url(r'^registration_base/(\d+)', 'FaraData.entry_view.registration_base', name='registration-base'),
    url(r'^registration_first/(\d+)', 'FaraData.entry_view.registration_first', name='registration-first'),
    url(r'^registration_payment/(\d+)', 'FaraData.entry_view.registration_payment', name='registration-payment'),
    url(r'^registration_disbursement/(\d+)', 'FaraData.entry_view.registration_disbursement', name='registration-disbursement'),
    url(r'^registration_gift/(\d+)', 'FaraData.entry_view.registration_gift', name='registration-gift'),
    url(r'^registration_contribution/(\d+)', 'FaraData.entry_view.registration_contribution', name='registration-contribution'),
    url(r'^registration_last/(\d+)', 'FaraData.entry_view.registration_last', name='registration-last'),
    #Amendment form
    url(r'^enter_amendment/(\d+)', 'FaraData.entry_view.index', name='enter-amendment'),
    #AB/ Client Registration
    url(r'^enter_AB/(\d+)', 'FaraData.entry_view.enter_AB', name='enter-AB'),
    url(r'^client_info', 'FaraData.entry_view.client_info', name='client-info'),
    #json to generate choices for the forms
    url(r'^formchoices/recip', 'FaraData.json_creator_view.recip_choice', name='json-recip-choices'),
    url(r'^formchoices/lobby', 'FaraData.json_creator_view.lobby_choice', name='json-lobby-choices'),
    url(r'^formchoices/client', 'FaraData.json_creator_view.client_choice', name='json-client-choices'),
    url(r'^formchoices/location', 'FaraData.json_creator_view.location_choice', name='json-location-choices'),
    url(r'^formchoices/reg', 'FaraData.json_creator_view.reg_choice', name='json-reg-choices'),
    #API lookup
    url(r'^find_form/', 'FaraData.find_api_view.find_form', name='find-form'),
    url(r'^find_member/', 'FaraData.find_api_view.find_member', name='find-member'),
    url(r'^add_member/', 'FaraData.find_api_view.add_member', name='add-member'),
    url(r'^add_staff/', 'FaraData.find_api_view.add_staff', name='add-staff'),
    url(r'^add_leader_PAC/', 'FaraData.find_api_view.add_leader_PAC', name='add-leader-PAC'),
    #Document managers
    url(r'^full_list', 'fara_feed.document_select_view.full_list', name='full-list'),
    url(r'^entry_list', 'fara_feed.document_select_view.entry_list', name='entry-list'),
    url(r'^supplemental_list', 'fara_feed.document_select_view.fast_supplemental', name='supplemental-list'),
    #Temp landing page
    url(r'^$', 'FaraData.views.temp_home', name='temp-home'),
    #Instructions for data entry 
    url(r'^instructions', 'FaraData.views.instructions', name='instructions'),
    ### End of forms
    # RSS feeds
    url(r'^latest/rss/$', LatestEntriesFeed()),
    url(r'^region/(?P<region>\w+)/rss', RegionFeed()),
    url(r'^entry/rss/$', DataEntryFeed()), 
    # CSV creators
    url(r'^contact_csv/(\d+)', 'FaraData.views.contact_csv', name='contact-csv'),
    url(r'^payment_csv/(\d+)', 'FaraData.views.payment_csv', name='payment-csv'),
    url(r'^clients_csv', 'FaraData.views.clients_csv', name='clients_csv'),
    )
