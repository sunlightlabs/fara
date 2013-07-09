import json
import csv
import requests

from sys import path

from FaraData.models import *

json_data = open('fara.json')
data = json.load(json_data)
print "Working ..."

# list of models:
# fara.registrant
# fara.client
# fara.registration
# fara.clientregistration
# fara.contribution
# fara.contact
# fara.fee
# fara.expense

def find(crp_id):

	query_params = {'apikey': 'aaf0ab990fc4443ab8d9a7d899686694',
	 				"crp_id": crp_id,
					"all_legislators": "true",
	}

	endpoint = 'http://congress.api.sunlightfoundation.com/legislators'
	response = requests.get(endpoint, params=query_params)
	response_url = response.url

	data = response.json()

	chamber = data['results'][0]['chamber']
	m_first_name =  data['results'][0]['first_name']
	m_last_name = data['results'][0]['last_name']
	m_full_name = "%s %s" % (m_first_name, m_last_name)
		
	return m_full_name, chamber
		

def add_member(data):
	full_name = data[0]
	chamber = data[1]		
	chamber = str(chamber).capitalize()

	if chamber == 'Senate':
		title = "Sen. "
	elif chamber == 'House':
		title = "Rep. "
	else:
		title = ''


	member = Recipient(crp_id = crp_id,
				    agency = "Congress",
				    office_detail = chamber,
				    name = full_name,
				    title = title,
	)	
 	member.save()
 	print "SAVED!"

def add_staff(data, name, title):
	member_name = data[0]
	chamber = data[1]		
	chamber = str(chamber).capitalize()
	if chamber == 'Senate':
		office = "Sen. " + member_name
	elif chamber == 'House':
		office = "Rep. " + member_name
	else:
		office = member_name


	staff = Recipient(crp_id = crp_id,
				    agency = chamber,
				    office_detail = office,
				    name = name,
				    title = title,
	)	
 	staff.save()
 	print staff
 	print "SAVED!"




for line in data:
	if  line['model'] == 'fara.contact':
		approved = line['fields']['approved']
		if approved == 1:
			crp_id = line['fields']['member_id']
			level = line['fields']['contact_level']


			if len(crp_id) == 9:

				if level == "Member":
					if Recipient.objects.filter(crp_id=crp_id, agency="congress").exists():
						print "member in"
					else:	
						response = find(crp_id)
						add_member(response)

				elif level == "Staff":
					name = line['fields']['contact_name_new']
					if Recipient.objects.filter(crp_id=crp_id, name=name).exists():	
						print 'staff in'
					else:
						title = line['fields']['contact_title']
						response = find(crp_id)
						add_staff(response, name, title)

				else:
					print level


			else:
				name = str(line['fields']['contact_name_new'])
				name = name.strip()
				title = line['fields']['contact_title']
				agency = line['fields']['contact_agency']
				office = line['fields']['agency_detail']

				if agency == "Other" or agency == "other":
					agency = ''
				if office == "Other" or office == "other":
					office = ''
				#I want this reserved for members and these don't have crp ids	
				if agency == "Congress":	
					agency = "Congressional"

				crp_id = crp_id[:9]

				if Recipient.objects.filter(crp_id=crp_id, name=name, agency=agency, office_detail=office).exists():
					print "In system"
				else:
					staff = Recipient(crp_id = crp_id,
					    agency = agency,
					    office_detail = office,
					    name = name,
					    title = title,
					)	
				 	staff.save()
				 	print "SAVED  ", name

	if  line['model'] == 'fara.contribution': 
		crp_id = line['fields']['member_id']
		approved = line['fields']['approved']
		if approved == 1:



