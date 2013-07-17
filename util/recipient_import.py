# Run this before  the import script to get recipients ready
# this adds a few extra records that I delete in the clean_recip.py
import json
import csv
import requests

from sys import path

from FaraData.models import *

json_data = open('fara.json')
data = json.load(json_data)
print "Working ..."

bad_ids = []
bad_id = csv.reader(open("known_unknowns.csv", "rU"))
for bad in bad_id:
	bad_ids.append(bad[0])

# did this to some fields so that the function returns the right number of outputs	
def no_none(item):
	if item == 'None' or item == 'none' or item == None:
		return ''
	else:
		return item
#ultimately not saving blank strings
def fix_none(item):
	if item == '':
		return None
	else:
		return item


known_ids = {}
def find(crp_id):
	if str(crp_id) in bad_ids:
		return "ERROR"
	
	elif known_ids.has_key(crp_id): 
		return ([known_ids[crp_id][0], known_ids[crp_id][1], crp_id])

	else:
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
			m_full_name = no_none(m_full_name)
			chamber = no_none(chamber)
			known_ids[crp_id] = [m_full_name, chamber]

			return (m_full_name, chamber, crp_id)

		except:
			print "Can't find CRP ID, not in bad list: ", crp_id
			bad_ids.append(crp_id)
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
		title = 'Hon.'
	crp_id = data[2]

	if Recipient.objects.filter(crp_id = crp_id, agency = "Congress", name = full_name).exists():
		pass
	else:
		member = Recipient(crp_id = crp_id,
					    agency = "Congress",
					    office_detail = chamber,
					    name = full_name,
					    title = title,
		)	
	 	member.save()
 	

def add_staff(data, name, title): 
	#print "data= ", data, 'name= ', name, 'title= ', title
	member_name = data[0]
	chamber = data[1]		
	chamber = str(chamber).capitalize()
	
	if chamber == 'Senate':
		office = "Sen. " + member_name
	
	if chamber == 'House':
		office = "Rep. " + member_name
	
	if chamber == "Congress":
		chamber = "Congressional"
	
	try:
		crp_id = data[2]
		if crp_id == '':
			crp_id = None
	except:
		print "Where did you come from? ", data, name, title 
		crp_id = None

	if 'office' not in locals():
			office = ''
	office = no_none(office)

	if office == name and office != '':
		add_member(data)
	
	elif office[4:] == name and office != '':
		add_memeber(data)
	

	else:
		name = fix_none(name)
		title = fix_none(title)
		office = fix_none(office)

		if Recipient.objects.filter(crp_id = crp_id, name = name).exists():
			pass
		
		elif crp_id != None and name != None:
			if len(crp_id) == 9 and ('(' in name or 'Sen. ' in name or 'Rep. ' in name):
				if "Staff" not in name:
					add_member(data)
			else:
				staff = Recipient(crp_id = crp_id,
							    agency = chamber,
							    office_detail = office,
							    name = name,
							    title = title,
				)	
			 	staff.save()
	 	else:
			staff = Recipient(crp_id = crp_id,
						    agency = chamber,
						    office_detail = office,
						    name = name,
						    title = title,
			)	
		 	staff.save()

def non_congressional_donation(crp_id, committee, candidate, state_local, com_type):	
	crp_id = crp_id[:9]
	crp_id = fix_none(crp_id)
	# capitalization was causing dupes
	committee = committee.upper()
	committee = committee.strip()
	committee = fix_none(committee)
	candidate = fix_none(candidate)		
	
	if candidate == None and (com_type != None or com_type != ''):
		candidate = com_type

	if Recipient.objects.filter(crp_id=crp_id, name=committee, office_detail=candidate).exists():
		pass
	elif crp_id == None and committee == None and candidate == None:
		pass

	else:			
		recip = Recipient(crp_id = crp_id,
							name = committee,
							office_detail = candidate,
							state_local = state_local,
		)
		recip.save()
		#print "non-congressional-donation", recip

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
	title = line['fields']['contact_title']
	name = no_none(name)
	name = name.strip()
	if name == '' and title != '' and title != None:
		name = title

	agency = line['fields']['contact_agency'].strip()
	crp_id = line['fields']['member_id']

	if agency == "Admin":
		agency =  line['fields']['agency_detail'].strip()
	if agency == None:
		agency = line['fields']['agency_detail']
	if agency != None:
		agency = clean_state(agency)
	if agency == "Congress":
		agency = "Congressional"

	office = line['fields']['agency_detail']

	if agency == "Other" or agency == "other":
		agency = ''
	if office == "Other" or office == "other":
		office = ''
	#I want this reserved for members and these don't have crp ids	
	if agency == "Congress":	
		agency = "Congressional"

	crp_id = crp_id[:9]
	crp_id = fix_none(crp_id)
	agency = fix_none(agency)
	office = fix_none(office)
	name = fix_none(name)
	title = fix_none(title)

	if Recipient.objects.filter(crp_id=crp_id, name=name, agency=agency, office_detail=office).exists():
		pass
	elif agency == None and office == None and name == None and title == None and crp_id == None:
		pass
	else:
		staff = Recipient(crp_id = crp_id,
		    agency = agency,
		    office_detail = office,
		    name = name,
		    title = title,
		)	
	 	staff.save()
	 	#print "reg-contact: ", staff

# this is for recipients that the other fields depend on 
for line in data:
	if line['model'] == 'fara.contact':
		approved = line['fields']['approved']
		# pulls out Recipients
		if approved == 1:
			crp_id = line['fields']['member_id']
			#these are easy to make copy and paste errors
			crp_id = crp_id.replace('&', '')
			crp_id = crp_id.replace('=', '')
			crp_id = no_none(crp_id)
			# fixes the wrong Connie Mack
			if crp_id == "N00001800":
					crp_id = "N00026425"

			level = line['fields']['contact_level']
			if level != None:
				level = str(level)
				level = level.title()

			name = line['fields']['contact_name']
			name = no_none(name)
			name = name.strip()
			title = line['fields']['contact_title']
			if name == '' and title != '' and title != None:
				name = title

			weird = ["B", "Ph", "G", "C", "J", "Fr", "Re", "None"]
			if name in weird and line['fields']['contact_name_new'] != None:
				name = line['fields']['contact_name_new']

			#Congressional Contact
			if len(crp_id) == 9:
				title = line['fields']['contact_title']
				title = no_none(title)
				title =  title.strip()

				member_terms = ["Member", "Members", "Senator" , "Senate" , "House Member", "House Members", "Membermember", "Representative", "Representatives"]
				if level != None and level != '':
					if level in member_terms:
						if Recipient.objects.filter(crp_id=crp_id, agency="Congress").exists():
							pass
						else:	
							response = find(crp_id)
							if response == 'Error':
								chamber = line['fields']['agency_detail']
								member_name = line['fields']['members_office_contacted']
								print "add staff -2 "
								add_staff([member_name, chamber, crp_id], name, title)
							else:
								add_member(response)
							
					elif "Staff" in level:
						if Recipient.objects.filter(crp_id=crp_id, name=name).exists():	
							pass
						else:
							response = find(crp_id)
							if response == 'Error':
								chamber = line['fields']['agency_detail']
								member_name = line['fields']['members_office_contacted']
								print "add staff -1"
								add_staff([member_name, chamber, crp_id], name, title)

							elif response == None:
								print line, " What?"
							else:
								print "add staff 0"
								add_staff(response, name, title)
					
					else:
						print "Level error", level
						if Recipient.objects.filter(crp_id=crp_id, name=name).exists():	
							pass
						else:
							response = find(crp_id)
							if response == 'Error':
								add_reg_contact(line)	
							else:
								print "add staff 1"
								add_staff(response, name, title)

				# uncoded congressional contacts
				else:
					if Recipient.objects.filter(crp_id=crp_id, name=name).exists():	
						pass
					else:
						response = find(crp_id)
						if response == 'Error':
							add_reg_contact(line)
						else:
							print "add staff 2"
							add_staff(response, name, title)

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
			candidate = no_none(candidate)
			
			committee = line['fields']['committee']
			committee = no_none(committee)
			if committee == '':
				committee = candidate
			else:
				committee = committee.strip()
			
			crp_id = line['fields']['candidate_id']
			if crp_id == None:
				crp_id = ''
			#these are easy to make copy and paste errors
			crp_id = crp_id.replace('&', '')
			crp_id = crp_id.replace('=', '')

			if str(line['fields']['local']).strip().lower() == "x":
				state_local = True
			else:
				state_local = False

			if len(crp_id) == 9:
				
				if "PAC" in str(line['fields']['recipient_type']):
					# Leadership PAC
					# too many capitalization errors making dupes for PACs
					committee = committee.upper()

					if Recipient.objects.filter(crp_id=crp_id, name=committee).exists():
						pass
					else:
						response = find(crp_id)
						if response == "ERROR":
							com_type = line['fields']['recipient_type']
							non_congressional_donation(crp_id, committee, candidate, state_local, com_type)
						else:
							name = response[0]
							chamber = response[1]
							if chamber == 'senate':
								office = "Sen. " + name
							elif chamber == 'house':
								office = "Rep. " + name

							if office == name:
								add_member(response)
							else:
								committee = fix_none(committee)	
								office = fix_none(office)

								if Recipient.objects.filter(crp_id = crp_id, name = committee, agency = "Leadership PAC", office_detail = office,).exists():
									pass
								else:
									#adding leadership PAC
									recip = Recipient(crp_id = crp_id,
														name = committee,
														agency = "Leadership PAC",
														office_detail = office,
									)
									#recip.save()
									

				# Congressional candidate committees	
				else:
					if Recipient.objects.filter(crp_id=crp_id, agency="Congress").exists():
						pass
					else:
						response = find(crp_id)	
						if response == "ERROR":
							com_type= line['fields']['recipient_type']
							non_congressional_donation(crp_id, committee, candidate, state_local, com_type)
						else:
							add_member(response)

			else:
				com_type= line['fields']['recipient_type']
				non_congressional_donation(crp_id, committee, candidate, state_local, com_type)
			
			# pulls out lobbyists
			lobbyist =  line['fields']['lobbyist']
			if lobbyist != None:
				lobbyist.strip()
				if Lobbyist.objects.filter(lobbyist_name=lobbyist).exists():	
					pass
				else:
					lobby= Lobbyist(lobbyist_name = lobbyist)
					lobby.save()

#Special case:
recip = Recipient(crp_id = None,
				name = 'Subcommittee of Select Revenue Measures',
				agency = "House",
				office_detail = "House Way & Means Committee",
)
#recip.save()

writer = csv.writer(open('clean_crp_info.csv','wb'))
writer.writerow(['crp id', 'full_name', 'chamber'])

for key in known_ids.keys():
	for k in known_ids[key]:
		row = [str(known_ids[key][2]), str(known_ids[key][0]), str(known_ids[key][1])]
		writer.writerow(row)
		
json_data.close()



