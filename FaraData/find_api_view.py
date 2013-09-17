import requests

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from FaraData.models import Recipient

@login_required(login_url='/admin')
def find_form(request):
 	return render(request, 'FaraData/api_lookup.html') 

@login_required(login_url='/admin')
def find_staff(request):
	return render(request, 'FaraData/api_staff_lookup.html')
         
@login_required(login_url='/admin')        
def find_member(request):
	q = request.GET['member'],
	query_params = { 'query': q,
					'apikey': 'aaf0ab990fc4443ab8d9a7d899686694',
	               }

	# it defaults to currently in office, so need this one too
	old_query_params = { 'query': q,
					'apikey': 'aaf0ab990fc4443ab8d9a7d899686694',
					'in_office': 'false',
	               }

	endpoint = 'http://congress.api.sunlightfoundation.com/legislators'
	response = requests.get(endpoint, params=query_params)
	response_old = requests.get(endpoint, params=old_query_params)
	response_url = response.url

	results = []

	def read_response(data, time):
		for d in data["results"]:
			crp_id = d['crp_id']
			if len(crp_id) > 1:
				chamber = str(d['chamber']).capitalize()
				if chamber == 'Senate':
					title = "Sen. "
				elif chamber == 'House':
					title = "Rep. "
				else:
					title = ''
				
				first_name =  d['first_name']
				last_name = d['last_name']
				full_name = "%s %s" %(first_name, last_name)
				party = d['party']
				crp_id = d['crp_id']
				state = d['state']
				
				if time == 'old':
					text = "%s %s %s (%s-%s) (not in office) CRP ID = %s" %(title, first_name, last_name, party, state, crp_id) 
				else:
					text = "%s %s %s (%s-%s) CRP ID = %s" %(title, first_name, last_name, party, state, crp_id) 
				
				result = [crp_id, "Congress", chamber,  full_name, title, text]
				results.append(result)


	data = response.json()
	old_data = response_old.json()
	read_response(data, "new")
	read_response(old_data, "old")
	return render(request, 'FaraData/api_lookup.html', {'results': results}) 

@login_required(login_url='/admin')
def add_member(request):
	member = Recipient(crp_id = request.GET['crp_id'],
					    agency = request.GET['agency'],
					    office_detail = request.GET['office_detail'],
					    name = request.GET['name'],
					    title = request.GET['title'],
	)
	if Recipient.objects.filter(crp_id = member.crp_id, agency="Congress").exists():
		message = member.name
		return render(request, 'FaraData/api_lookup.html', {'insystem': message})
	else:
		member.save()
		return render(request, 'FaraData/api_lookup.html', {'member': member.name})

@login_required(login_url='/admin')
def add_staff(request):
	agency = request.GET['agency']
	member_name = request.GET['office_detail']
	if agency == "House":
		member_name = "Rep. " + member_name
	elif agency == "Senate":
		member_name = "Sen. " + member_name

	staff = Recipient(crp_id = request.GET['crp_id'],
					    agency = request.GET['agency'],
					    office_detail = member_name,
					    name = request.GET['name'],
					    title = request.GET['title'],
	)
	if Recipient.objects.filter(crp_id=staff.crp_id, name=staff.name).exists():
		message = staff.name + " of " + staff.office_detail + " CRP id : " + staff.crp_id 
		return render(request, 'FaraData/api_lookup.html', {'insystem': message})
	else:
		staff.save()
		message = staff.name + " of " + staff.office_detail + "'s office"
		return render(request, 'FaraData/api_lookup.html', {'member': message})


