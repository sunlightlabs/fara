# Run this before  the import script to get recipients ready
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
	try:
		chamber = data['results'][0]['chamber']
		m_first_name =  data['results'][0]['first_name']
		m_last_name = data['results'][0]['last_name']
		m_full_name = "%s %s" % (m_first_name, m_last_name)
		return m_full_name, chamber
	except:
		print "Can't find CRP ID: ", crp_id
		return "ERROR"	

	
		

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

def non_congressional_donation(crp_id, committee, candidate, state_local):
	if Recipient.objects.filter(crp_id=crp_id, name=committee, office_detail=candidate).exists():
					recip = Recipient(crp_id = crp_id,
										name = committee,
										office_detail = candidate,
										state_local = state_local,
					)
					recip.save()
def clean_state(entry):
	entry = entry.strip()
	state_words = ("Dept of State", "State Department", "Department of State", "US Department of State", "U.S. Department of State", "Dept. of State", "Department of State, U.S.")
	if entry in state_words:
		agency = "U.S. Department of State"
		return agency
	else:
		return entry

def add_reg_contact(line):
	name = str(line['fields']['contact_name'])
	name = name.strip()
	title = line['fields']['contact_title']
	agency = line['fields']['contact_agency'].strip()
	crp_id = line['fields']['member_id']
	if agency == "Admin":
		agency =  line['fields']['agency_detail'].strip()
	if agency == None:
		agency = line['fields']['agency_detail']
	if agency != None:
		agency = clean_state(agency)

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
		pass
	else:
		staff = Recipient(crp_id = crp_id,
		    agency = agency,
		    office_detail = office,
		    name = name,
		    title = title,
		)	
	 	staff.save()


# this is for recipients that the other fields depend on 
for line in data:
	if  line['model'] == 'fara.contact':
		approved = line['fields']['approved']
		# pulls out Recipients
		if approved == 1:
			crp_id = line['fields']['member_id']
			level = line['fields']['contact_level']
			if level != None:
				level = str(level).strip().title()

			#Congressional Contact
			if len(crp_id) == 9:
				name = line['fields']['contact_name']
				title = line['fields']['contact_title']
				
				if level != None and level != '':
					if level == "Member" or level == 'Members':
						if Recipient.objects.filter(crp_id=crp_id, agency="Congress").exists():
							pass
						else:	
							response = find(crp_id)
							add_member(response)

					elif level == "Staff":
						if Recipient.objects.filter(crp_id=crp_id, name=name).exists():	
							pass
						else:
							response = find(crp_id)
							add_staff(response, name, title)
					
					else:
						print "Level error", name, level
						response = find(crp_id)
						if Recipient.objects.filter(crp_id=crp_id, name=name).exists():	
							pass
						else:
							if response != 'Error':
								response = find(crp_id)
								add_staff(response, name, title)
							else:
								add_reg_contact(line)	
				# ambiguous congressional contacts
				else:
					print "No Level", name
					response = find(crp_id)
					if Recipient.objects.filter(crp_id=crp_id, name=name).exists():	
						pass
					else:
						response = find(crp_id)
						if response != 'Error':
							add_staff(response, name, title)
						else:
							add_reg_contact(line)

			#non-congressional contacts
			else:
				add_reg_contact(line)

			# pulls out lobbyists
			lobbyist =  line['fields']['lobbyist']
			if lobbyist != None:
				lobbyist.strip()
				if Lobbyist.objects.filter(lobbyist_name=lobbyist).exists():	
					pass
				else:
					lobby= Lobbyist(lobbyist_name = lobbyist)
					lobby.save()


	if  line['model'] == 'fara.contribution': 
		
		# pulls out recipients from contributions
		approved = line['fields']['approved']
		if approved == 1:
			candidate = line['fields']['candidate_name']
			committee = line['fields']['committee']
			if committee == None:
				committee = candidate
			else:
				committee = committee.strip()
			crp_id = line['fields']['candidate_id']
			if crp_id == None:
				crp_id = ''
			
			if str(line['fields']['local']).strip().lower() == "x":
				state_local = True
			else:
				state_local = False

			if len(crp_id) == 9:
				
				if "PAC" in str(line['fields']['recipient_type']):
					# Leadership PAC
					if Recipient.objects.filter(crp_id=crp_id, name=committee).exists():
						pass
					else:
						response = find(crp_id)
						if response == "ERROR":
							non_congressional_donation(crp_id, committee, candidate, state_local)
						else:
							name = response[0]
							chamber = response[1]
							if chamber == 'senate':
								office = "Sen. " + name
							elif chamber == 'house':
								office = "Rep. " + name
							recip = Recipient(crp_id = crp_id,
												name = committee,
												office_detail = office,
							)
							recip.save()

				# Congressional candidate committees	
				else:
					if Recipient.objects.filter(crp_id=crp_id, agency="Congress").exists():
						pass
					else:
						response = find(crp_id)	
						if response == "ERROR":
							non_congressional_donation(crp_id, committee, candidate, state_local)
						else:
							add_member(response)

			else:
				non_congressional_donation(crp_id, committee, candidate, state_local)
			
			# pulls out lobbyists
			lobbyist =  line['fields']['lobbyist']
			if lobbyist != None:
				lobbyist.strip()
				if Lobbyist.objects.filter(lobbyist_name=lobbyist).exists():	
					pass
				else:
					lobby= Lobbyist(lobbyist_name = lobbyist)
					lobby.save()





