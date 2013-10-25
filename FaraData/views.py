import csv
from datetime import datetime

from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http import HttpResponse


from FaraData.models import *
from fara_feed.models import *

@login_required(login_url='/admin')
def temp_home(request):
	return render(request, 'fara_feed/temp_home.html')

@login_required(login_url='/admin')
def instructions(request):
	return render(request, 'FaraData/instructions.html')

### Creating CSV results 

@login_required(login_url='/admin')
def contact_csv(request, form_id):
	doc = Document.objects.get(id=form_id)
	url = doc.url
	contacts = Contact.objects.filter(link=url)
	response = HttpResponse(content_type='text/csv')
	filename = "contacts" + form_id + ".csv"
	response['Content-Disposition'] = 'attachment; filename='+ filename

	md = MetaData.objects.get(link=url)
	dumb_date = md.end_date

	writer = csv.writer(response)
	writer.writerow(['Date', 'Contact', 'Client', 'Registrant', 'Description', 'Type', 'Employees mentioned', 'Source'])
	for c in contacts:

		lobbyists = ''
		for l in c.lobbyist.all():
			lobbyists = lobbyists + l.lobbyist_name + ", "
		lobbyists = lobbyists.encode('ascii', errors='ignore')
		recipients = []
		contact_name = ''
		for r in c.recipient.all():
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
		
		if c.date == None:
			date = dumb_date.strftime('%x') + "*"
		else:
			date = c.date
		
		c_type = {"M": "meeting", "U":"unknown", "P":"phone", "O": "other", "E": "email"}
		
		writer.writerow([date, contact_name, c.client, c.registrant, c.description, c_type[c.contact_type], lobbyists, c.link, c.id])

	return response


@login_required(login_url='/admin')
def payment_csv(request, form_id):
	doc = Document.objects.get(id=form_id)
	url = doc.url
	payments = Payment.objects.filter(link=url)
	response = HttpResponse(content_type='text/csv')
	filename = "payments" + form_id + ".csv"
	response['Content-Disposition'] = 'attachment; filename='+ filename

	md = MetaData.objects.get(link=url)
	dumb_date = md.end_date

	writer = csv.writer(response)
	writer.writerow(['Client', 'Amount', 'Date', 'Registrant', 'Purpose', 'Source'])

	for p in payments:
		if p.date == None:
			date = dumb_date.strftime('%x') + "*"
		else:
			date = p.date
		writer.writerow([p.client, p.amount, date, p.registrant, p.purpose, p.link])

	return response

@login_required(login_url='/admin')
def clients_csv(request):
	response = HttpResponse(content_type='text/csv')
	filename = "clients" + datetime.now().strftime('%x') + ".csv"
	response['Content-Disposition'] = 'attachment; filename='+ filename
	clients = Client.objects.all()

	writer = csv.writer(response)

	for c in clients:
		writer.writerow([c.id, c.client_name]) 
	return response
