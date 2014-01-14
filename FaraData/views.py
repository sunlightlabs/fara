import csv
from datetime import datetime

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
		contact_name = contact_name + r.name.encode('ascii', errors='ignore')
	if r.office_detail != None and r.office_detail != '':
		contact_name = contact_name + ", office: " + r.office_detail.encode('ascii', errors='ignore')
	if r. agency != None and r.agency != '':
		contact_name = contact_name + ", agency: " + r.agency.encode('ascii', errors='ignore')
	contact_name = contact_name.encode('ascii', errors='ignore') + "; "
	return contact_name

@login_required(login_url='/admin')
def temp_home(request):
	return render(request, 'fara_feed/temp_home.html')

@login_required(login_url='/admin')
def instructions(request):
	return render(request, 'FaraData/instructions.html')

### Creating CSV results by form

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
	writer.writerow(['Date', 'Contact Title', 'Contact Name', 'Contact Agency', 'Contact Office', 'CRP ID', 'Bioguide ID', 'Client', 'Client Location', 'Registrant', 'Description', 'Type', 'Employees mentioned', 'Source', 'Record ID'])
	for c in contacts:

		lobbyists = ''
		for l in c.lobbyist.all():
			lobbyists = lobbyists + l.lobbyist_name + ", "
		lobbyists = lobbyists.encode('ascii', errors='ignore')
		
		if c.date == None:
			date = dumb_date.strftime('%x') + "*"
		else:
			date = c.date

		c_type = {"M": "meeting", "U":"unknown", "P":"phone", "O": "other", "E": "email"}

		for r in c.recipient.all():
			if str(r.name).lower() != "unknown":
				name = str(r.name).encode('ascii', errors='ignore')
			else:
				name = ''
			writer.writerow([date, r.title, name, r.agency, r.office_detail, r.crp_id, r.bioguide_id, c.client, c.client.location, c.registrant, c.description, c_type[c.contact_type], lobbyists, c.link, c.id])

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
	writer.writerow(['Client', 'Amount', 'Date', 'Registrant', 'Purpose', 'From Subcontractor' 'Source'])

	for p in payments:
		if p.date == None:
			date = dumb_date.strftime('%x') + "*"
		else:
			date = p.date
		
		writer.writerow([p.client, p.amount, date, p.registrant, p.purpose, p.subcontractor, p.link])

	return response

@login_required(login_url='/admin')
def disbursement_csv(request, form_id):
	doc = Document.objects.get(id=form_id)
	url = doc.url
	disbursement = Disbursement.objects.filter(link=url)
	response = HttpResponse(content_type='text/csv')
	filename = "disbursements" + form_id + ".csv"
	response['Content-Disposition'] = 'attachment; filename='+ filename

	md = MetaData.objects.get(link=url)
	dumb_date = md.end_date

	writer = csv.writer(response)
	writer.writerow(['Amount', 'Date','Client', 'Registrant', 'Purpose', 'Source', 'Record ID'])

	for d in disbursement:
		if d.date == None:
			date = dumb_date.strftime('%x') + "*"
		else:
			date = d.date
		
		writer.writerow([d.amount, date, d.client, d.registrant, d.purpose, d.link, d.id])

	return response

#
@login_required(login_url='/admin')
def contribution_csv(request, form_id):
	doc = Document.objects.get(id=form_id)
	url = doc.url
	contribution = Contribution.objects.filter(link=url)
	response = HttpResponse(content_type='text/csv')
	filename = "contributions" + form_id + ".csv"
	response['Content-Disposition'] = 'attachment; filename='+ filename

	md = MetaData.objects.get(link=url)
	dumb_date = md.end_date

	writer = csv.writer(response)
	writer.writerow(['Amount', 'Date', 'Recipient', 'Registrant', 'Contributing Lobbyist or PAC', 'Source', 'Record ID'])

	for c in contribution:	
 		recipient_name = namebuilder(c.recipient)
 		if c.lobbyist:
 			lobby = c.lobbyist
 		else:
 			lobby = ''
 		if c.date == None:
			date = dumb_date.strftime('%x') + "*"
		else:
			date = c.date
		writer.writerow([c.amount, date, recipient_name, c.registrant, lobby, c.link, c.id])

	return response


#I wrote this as a resource for clean-up 
@login_required(login_url='/admin')
def clients_csv(request):
	response = HttpResponse(content_type='text/csv')
	filename = "clients" + datetime.now().strftime('%x') + ".csv"
	response['Content-Disposition'] = 'attachment; filename='+ filename
	clients = Client.objects.all()

	writer = csv.writer(response)

	for c in clients:
		writer.writerow([c.id, c.client_name, c.location]) 
	
	return response




