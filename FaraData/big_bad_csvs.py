import csv
import datetime

from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from FaraData.models import *
from fara_feed.models import *

def namebuilder(r):
	contact_name = ''
	if r.title != None and r.title != '':	
		contact_name = r.title.encode('ascii', errors='ignore') + ' '
	if r.name != None and r.name != '':
		contact_name = contact_name + r.name.encode('ascii', errors='ignore') + ', '
	if r.office_detail != None and r.office_detail != '':
		contact_name = contact_name + "office: " + r.office_detail.encode('ascii', errors='ignore') + ', '
	if r. agency != None and r.agency != '':
		contact_name = contact_name + "agency: " + r.agency.encode('ascii', errors='ignore')
	contact_name = contact_name.encode('ascii', errors='ignore') + "; "
	return contact_name

@login_required(login_url='/admin')
def big_bad_contacts(request):
	filename = "contacts" + str(datetime.date.today()) + ".csv"
	docs = Document.objects.filter(processed=True, doc_type="Supplemental",stamp_date__range=(datetime.date(2011,1,1), datetime.date.today()))
	response = HttpResponse(content_type='text/csv')
	writer = csv.writer(response)
	response['Content-Disposition'] = 'attachment; filename='+ filename
	writer.writerow(['Date', 'Contact', 'Client', 'Registrant', 'Description', 'Type', 'Employees mentioned', 'Source', 'Record ID'])

	for d in docs:
		url = d.url
		md = MetaData.objects.get(link=url)
		end_date = md.end_date
		if md.end_date == None:
			if md.notes == "legacy":
				end_date = None
			else:
				print md.link

		info = {
			"url": url,
			"contacts": Contact.objects.filter(link=url),
			"md": md,
			"dumb_date": end_date,
			"writer": writer,
		}

		

	return response

def find_contacts(info):
	contacts = info['contacts']
	url = info['url']
	md = info['md']
	dumb_date = info['dumb_date']
	writer = info['writer']
	
	for c in contacts:
		lobbyists = ''
		for l in c.lobbyist.all():
			lobbyists = lobbyists + l.lobbyist_name + ", "
		lobbyists = lobbyists.encode('ascii', errors='ignore')
		#recipients = []
		contact_name = ''
		for r in c.recipient.all():
			contact_name = namebuilder(r)
		
		if c.date == None:
			try:
				date = dumb_date.strftime('%x') + "*"
			except:
				# this is bad, it means a missing date
				date = "*"
		else:
			date = c.date
		
		c_type = {"M": "meeting", "U":"unknown", "P":"phone", "O": "other", "E": "email"}
		
		writer.writerow([date, contact_name, c.client, c.registrant, c.description, c_type[c.contact_type], lobbyists, c.link, c.id])

big_bad_
