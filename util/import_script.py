import json
import csv

from sys import path
from dateutil import parser
from datetime import datetime

from FaraData.models import *
from fara_feed.models import Document

# list of models:
# fara.registrant
# fara.client
# fara.registration
# fara.clientregistration
# fara.contribution
# fara.contact
# fara.fee
# fara.expense


json_data = open('fara.json')
data = json.load(json_data)
print "Working ..."
count = 0
reg = []
client_list = []
client_id_list = []
pay_list = []
pay_list_reject = []
expense_list = []
expense_list_reject = []
contribution_list = []
contribution_reject = []

#for recipients with bad ids
bad_ids = []
bad_id = csv.reader(open("known_unknowns.csv", "rU"))
for bad in bad_id:
	bad_ids.append(bad[0])

locationfixes = {'" The League of Arab States "':"The League of Arab States", "New Delhi-110 001":"New Delhi", "New Delhi-110 001 ":"New Delhi", "Alberta T5K2GB": "Alberta", "Azerbaijan ": "Azerbaijan", "Bermuda ":"Bermuda", "Brasil":"Brazil", "Cote d'Ivoire": "Cote D'Ivoire", "Ethopia":"Ethiopia", "Isle of Mann":"Isle of Man", "Malta ":"Malta", "Netherlands, Antilles":"Netherlands Antilles", "Republika Srpksa":"Republika Srpska", "Singapore 247729":"Singapore", "Trinidad & Tobago ": "Trinidad and Tobago", "Uganda ":"Uganda", "United Arab Emerates":"United Arab Emirates", "UAE":"United Arab Emirates", "United Kingdim":"United Kingdom", "UK":"United Kingdom"}

client_namereader = csv.reader(open("client-by-FK.csv", "rU"))
client_namereader.next()
client_names = {}
for line in client_namereader:
	old=line[1]
	new=line[2]
	client_names[old]= new

#This is first pass to build cross walk
client_crossing = []
reg_fara = {}
fara_reg = {}
client_reg = {}
reg_client = {}
creg_reg_client = {}
client_nclient ={}
reg_link = {}
cid_name = {}
reg_file = {}

def fix_none(item):
	if item == '':
		return None
	elif item == 'None':
		return None
	else:
		return item

crosswalk_reader = csv.reader(open("client-crosswalk.csv", "rU"))
crosswalk_reader.next()
for line in crosswalk_reader:
	#[clientreg_id, registration, reg_id, client_id, nclient_id, file_id]
	clientreg_id = line[0]
	registration_id = line[1]
	reg_id = line[2]
	client_id = line[3]
	nclient_id = line[4]
	try:
		file_id = line [5]
	except:
		file_id = "x"
	if client_id != None:
		client_nclient[client_id] = nclient_id
		client_reg[client_id] = reg_id
	if registration_id != None:
		reg_file[registration_id] = file_id

print "Cross has been walked!"	

for line in data:
	if line['model'] == 'fara.registration':
		registration_id = line['pk']
		fara_id = line['fields']['registrant']	
		reg_fara[registration_id] = fara_id
		fara_reg[fara_id] = registration_id
		reg_link[registration_id] = line['fields']['source_file']
		file_id = line['fields']['source_file']
		reg_file[registration_id] = file_id

	if line['model'] == 'fara.clientregistration':
		client_id = line['fields']['client']
		registration_id = line['fields']['registration']
		client_reg[client_id] = registration_id
		reg_client[registration_id] = client_id
		cid_name[client_id] = line['fields']['name']
		creg_reg_client[line['pk']] = [registration_id, client_id]
	
print "reg and client done!"

# This is the second pass to build crosswalk, saving reg, client and location models
country_count = 0
countries = {}
for line in data:
	if line['model'] == 'fara.registration':
		reg_id = int(line['fields']['registrant'])
		reg.append([reg_id, line['fields']['name_old'], line['fields']['filing_date'], line['fields']['address'], line['fields']['city'], line['fields']['state'], line['fields']['zipcode'], line['pk']])	

		try:
			entered = Registrant.objects.get(reg_id= reg_id)
			
		except:
			registrant = Registrant(reg_id = reg_id,
									reg_name = line['fields']['name_old'],
	    							address = line['fields']['address'],
	    							city = line['fields']['city'],
	    							state = line['fields']['state'],
	    							zip_code = line['fields']['zipcode'],
			)
			registrant.save()

	if line['model'] == 'fara.clientregistration':
		clientreg_id = line['pk']
		client_id = line['fields']['client']
		country = line['fields']['country']

		
#adding locatons
		if locationfixes.has_key(country):
			country = locationfixes[country] 
		if countries.has_key(country):
			location_id = countries[country]
		else:
			country_count += 1
			countries[country] = country_count
			location_id = country_count

		try:
			entered = Location.objects.get(location= country)

		except:
			try:
				alsoentered = Location.objects.get(location=reg_id)
			except:
				print line['fields']['name'], client_id, cid_name[client_id]
				if (country == '' or country == None) and Location(location=reg_id).exists== False:
					location = Location(location = reg_id,
									country_grouping = line['fields']['name'],
									region = "Unidentified",
					)
					location.save()
					entered = location
				else:	
					location = Location(location = country,
										country_grouping = country,
										region = "x"
					)
					location.save()
					entered = location

# adding clients
		client_name = line['fields']['name']
		client_name = client_names[client_name]
		loc = Location.objects.get(location=entered)


		if line['fields']['client'] not in client_id_list:
			client_id_list.append(line['fields']['client'])

			try:
				client = Client(client_name = client_name,
    							address1 = line['fields']['address'],
    							city = line['fields']['city'], 
    							state = line['fields']['state'],
    							zip_code = line['fields']['zipcode'],
    							location = loc,
				)
				#save client and make an id object mapping 
				client.save()
				nclient_id = client.id
				client_nclient[client_id] = nclient_id

			except:
				print line, " SAVE ERROR \n" 

		client_list.append([client_id, 
						line['fields']['name'], 
						line['fields']['address'], 
						line['fields']['city'], 
						line['fields']['state'], 
						country, 
						line['fields']['contact_summary'], 
						line['fields']['registration'], 
						line['fields']['client'], 
						line['fields']['approved'],
						line['pk'],
		])
		client_crossing.append([clientreg_id, 
								line['fields']['registration'], 
								reg_id, 
								line['fields']['client'], 
								nclient_id, 
								file_id])
# end of client and location loop

#functions to process contacts
def clean_state(entry):
	entry = entry.strip()
	state_words = ("Dept of State", "State Department", "Department of State", "US Department of State", "U.S. Department of State", "Dept. of State", "Department of State, U.S.")
	if entry in state_words:
		agency = "U.S. Department of State"
		return agency
	else:
		return entry

def find_reg_contact(line):
	try:
		agency = str(line['fields']['contact_agency']).strip()
	except:
		agency = None

	try:
		office = str(line['fields']['agency_detail'])
	except:
		office = None

	if agency == "Admin":
		agency =  line['fields']['agency_detail'].strip()
	if agency == None:
		agency = line['fields']['agency_detail']
	if agency != None:
		agency = clean_state(agency)
	if agency == "Congress":
		agency = "Congressional"
	if agency == "Other" or agency == "other":
		agency = ''
	if office == "Other" or office == "other":
		office = ''
	#This reserved for members
	if agency == "Congress":	
		agency = "Congressional"

	crp_id = line['fields']['member_id']
	crp_id = crp_id[:9]
	crp_id = fix_none(crp_id)
	agency = fix_none(agency)
	office = fix_none(office)
	
	name = str(line['fields']['contact_name'])
	if name != None:
		name = name.strip()
		name = fix_none(name)
	
	title = line['fields']['contact_title']
	if title != None:
		title.strip()
		title = fix_none(title)

	if name == None and title != None:
		name = title

	if crp_id != None:
		if len(crp_id) == 9:
			if office != None:
				if office[4:] == name and office != '' and office != None:
					recip_obj = Recipient.objects.get(crp_id=crp_id, agency="Congress")# member
					return recip_obj
				else:
					try:
						recip_obj = Recipient.objects.get(crp_id=crp_id, name=name)
						return recip_obj
					except:
						print line, "what is going on?1"
						return None
			else:
				try:
					recip_obj = Recipient.objects.get(crp_id=crp_id, name=name)
					return recip_obj
				except:
					print line, "what is going on?2"
					return None


	# this is because of the title error, it shouldn't be needed in the future
	else:
		try:
			recip_obj = Recipient.objects.get(crp_id=crp_id, name=name, agency=agency, office_detail=office)
			return recip_obj
		except:
			if name != None:
				name =  name[:149]
				print "deal with this later", line
			
			staff = Recipient(crp_id = crp_id,
			    agency = agency,
			    office_detail = office,
			    name = name,
			    title = title,
			)	
		 	staff.save()
		 	print "added fresh recip", (crp_id, name, agency, office)
		 	return staff


print "Loop 3"
#Adding a septate loop to make sure we are not asking for keys that don't exist yet
#Loop 3 contains: Contacts, Payment, Disbursement, Contributions

for line in data:
	if line['model'] == "fara.contact":
		if line['fields']['approved'] == 1:
			creg = line['fields']['client_registration']
			reg_id = creg_reg_client[creg][0]
			cid = creg_reg_client[creg][1]
			file_id = reg_file[reg_id] 
			file_id = str(file_id)

			nclient = client_nclient[cid]
			client_obj = Client.objects.get(id=nclient)

			fara_id = reg_fara[reg_id]
			reg_obj = Registrant.objects.get(reg_id=fara_id)

			lobbyist = line['fields']['lobbyist']
			if lobbyist != None and lobbyist != '':
				lobbyist.strip()
				lobby_obj = Lobbyist.objects.get(lobbyist_name = lobbyist)
			else:
				lobby_obj = None

			date = line['fields']['date']
			try:
				date_obj = datetime.strptime(date, "%Y-%m-%d")
			except:
				date_obj = None

			contact_type = line['fields']['contact_type']
			if contact_type == None or contact_type == '':
				contact_type = "U"
			contact_type = str(contact_type)
			contact_type = contact_type.strip()
			contact_type = contact_type.upper()
			options_tup = ('P', 'E', 'M', 'O', 'U')
			if contact_type not in options_tup:
				contact_type = 'U'
			
			description = str(line['fields']['issues'])
			if description == '':
				description = None

			name = line['fields']['contact_name']
			if name != None:
				name = name.strip()

				weird = ["B", "Ph", "G", "C", "J", "Fr", "Re", "None"]
				if name in weird and line['fields']['contact_name_new'] != None:
					name = line['fields']['contact_name_new']

			title = line['fields']['contact_title']
			if title != None:
				title =  title.strip()
			
			level = line['fields']['contact_level']
			if level != None:
				level = level.title()

			#logic to filter recipients

			crp_id = line['fields']['member_id']
			if crp_id != None:
				crp_id = crp_id.strip()

			try:
				office = str(line['fields']['agency_detail'])
			except:
				office = None

			try:
				agency = str(line['fields']['contact_agency']).strip()
			except:
				agency = None			
			if agency == "Admin":
				agency =  line['fields']['agency_detail'].strip()
			if agency == None:
				agency = line['fields']['agency_detail']
			if agency != None:
				agency = clean_state(agency)
			if agency == "Other" or agency == "other":
				agency = None

			agency = fix_none(agency)
			office = fix_none(office)
			name = fix_none(name)
			title = fix_none(title)
			if name == None and title != None:
					name = title

			crp_id = fix_none(crp_id)
			if crp_id != None:
				crp_id = crp_id.replace('&', '')
				crp_id = crp_id.replace('=', '')
			# fixes the wrong Connie Mack
			if crp_id == "N00001800":
				crp_id = "N00026425"

			# shouldn't need this again, it is for the name in the title problem
			error_list =["Georgian President", "Jodi Herman", "Katharine Bluhm", "Zahir Janmohahed", "Benjamin Gilman"]
			
			if agency == None and office == None and name == None and title == None and crp_id == None:
				recip_obj = None
#### hand fixed
			elif name == "House Way & Means Committee, Subcommittee of Select Revenue Measures" or name == "House Way and Means Committee and Subcommittee of Select Revenue Measures":
				recip_obj = Recipient.objects.get(name="Subcommittee of Select Revenue Measures")
			elif name == "Maurice Hinchey" or name == "Glenn Thompson":
				Recipient.objects.get(crp_id=crp_id, agency="Congress")

			# shouldn't need this again, it is for the name in the title problem
			elif name in error_list:
				recip_obj = Recipient.objects.get(name=name)
			elif name == "[Unidentified assistant] - Office of the Assistant Secretary of Commerce for Trade Promotion and Director General, U.S. and Foreign Commercial Service":
				recip_obj = Recipient.objects.get(name="Office of the Assistant Secretary of Commerce")
			elif name == "American Media/Editorial Writers" or name =="American Media":
				recip_obj = Recipient.objects.get(name= "American Media/Editorial Writers")
			
			else:
				if crp_id != None:
					
					if len(crp_id) == 9:
						# Congressional contacts
						member_terms = ["Member", "Members", "Senator" , "Senate" , "House Member", "House Members", "Membermember", "Representative", "Representatives"]
						if level in member_terms:
							try:
								recip_obj = Recipient.objects.get(crp_id=crp_id, agency="Congress")# member
							except:
								recip_obj = Recipient.objects.get(crp_id = crp_id, name = name)# staff

						elif "Staff" in level:
							try:
								recip_obj = Recipient.objects.get(crp_id = crp_id, name = name)# staff
							except:
								recip_obj = find_reg_contact(line)
						# uncoded congressional contacts
						else:
							if office == None:
								office = ''
							if name == None:
								name = ''
							if '(' in name or 'Sen. ' in name or 'Rep. ' in name:
								if "Staff" not in name:
									recip_obj = Recipient.objects.get(crp_id=crp_id, agency="Congress")# member
								else:
									try:
										recip_obj = Recipient.objects.get(crp_id = crp_id, name = name)# staff
									except:
										recip_obj = find_reg_contact(line)
							elif office == name and office != '':
								recip_obj = Recipient.objects.get(crp_id=crp_id, agency="Congress")# member
							elif office[4:] == name and office != '':
								recip_obj = Recipient.objects.get(crp_id=crp_id, agency="Congress")# member
							else:
								try:
									name = fix_none(name)
									recip_obj = Recipient.objects.get(crp_id = crp_id, name = name)# staff
								except:
									recip_obj = find_reg_contact(line)

					#non-congressional contacts
					else:
						recip_obj = find_reg_contact(line)
				else:
					recip_obj = find_reg_contact(line)

			contact = Contact(client = client_obj,
							registrant = reg_obj,
							contact_type = contact_type,
							description = description,
							date = date_obj,
							link = file_id,
			)
			contact.save()

			if lobby_obj != None:
				contact.lobbyist.add(lobby_obj)
				pass
			if recip_obj != None:
				contact.recipient.add(recip_obj)
				pass
	
	if line['model'] == "fara.registration":

		reg_id = int(line['fields']['registrant'])
		file_id = line['fields']['source_file']
		date = line['fields']['filing_date']
		try:
			date_obj = datetime.strptime(date, "%Y-%m-%d")
		except:
			date_obj = None
			print "bad date"

		doc = Document(url = file_id,
			    reg_id = reg_id,
			    doc_type = "Supplemental",
			    stamp_date =  date_obj,
		)
		doc.save()
		
	if line['model'] == "fara.fee": 
		clientreg_id = line['fields']['client_registration']
		registration = creg_reg_client[clientreg_id][0]
		reg_id = reg_fara[registration]
		client_id = creg_reg_client[clientreg_id][1]
		nclient_id = client_nclient[client_id]
		
		client_obj = Client.objects.get(id=nclient_id)
		reg_obj = Registrant.objects.get(reg_id=reg_id)
		
		fee = str(line['fields']['feesretainer']).strip()
		file_id = reg_file[registration]

		if fee == '' or fee == "None":
			fee = False
		elif fee == "x":
			fee = True
		else:
			fee = False
		
		approved = line['fields']['approved']
		if approved == 1:
			approved = True
		else:
			approved = False

		date = line['fields']['dateNEW']
		
		try:
			date_obj = datetime.strptime(date, "%Y-%m-%d")
		except:
			date_obj = None

		if approved == True:
			if line['fields']['amount'] == '' or line['fields']['amount'] == None:
				pay_list_reject.append([client_name, client_id, reg_id, fee, line['fields']['amount'], line['fields']['purpose'], line['fields']['dateNEW'], file_id])
			else:
				payment = Payment(client = client_obj,
		 		  					registrant = reg_obj,
								    fee = fee,
								    amount = line['fields']['amount'],
								    purpose = line['fields']['purpose'],
								    date = date_obj,
								    link = file_id, 
				)
		# Only save this once, there is not a good way to check if it has been added before
				payment.save()

		else:
			client_name = cid_name[client_id]
			pay_list_reject.append((client_name, client_id, reg_id, fee, line['fields']['amount'], line['fields']['purpose'], line['fields']['dateNEW'], file_id))

		pay_list.append((client_name, client_id, reg_id, fee, line['fields']['amount'], line['fields']['purpose'], line['fields']['dateNEW'], file_id))


	if line['model'] == "fara.expense": 
		clientreg_id = line['fields']['client_registration']
		registration = creg_reg_client[clientreg_id][0]
		reg_id = reg_fara[registration]
		client_id = creg_reg_client[clientreg_id][1]
		nclient_id = client_nclient[client_id]
		file_id = reg_file[registration]

		amount = line['fields']['amount']
		date = line['fields']['date']
		purpose = line['fields']['purpose']

		reg_obj = Registrant.objects.get(reg_id=reg_id)

		try:
			nclient_id = client_nclient[client_id]
			client_obj = Client.objects.get(id=nclient_id)
		
		except:
			name = cid_name[client_id]
			client_obj = Client.objects.get(client_name=name)
			print "lookup by name"

		approved = int(line['fields']['approved'])

		if approved == 1:
			approved = True
		else:
			approved = False
		
		try:
			new_date =parser.parse(date, fuzzy=True)
			
			if type(new_date) is not datetime.date:
				date = None
			else:
				#Checking to make sure the date is in the range of the document that wwere in the old system
				if new_date > datetime.date(2011, 04, 1) and new_date < datetime.date(2007, 1, 1):
					date = new_date
				else:
					date = None
		except:
			date = None

		if approved == False or amount == '' or amount == None:
			expense_list_reject.append((amount, 
				date, 
				purpose, 
				clientreg_id, 
				nclient_id, 
				approved,
				file_id,
				))

		else:	
			try:
				reg_obj = Registrant.objects.get(reg_id=reg_id)
				disbursement = Disbursement(client = client_obj,
									    registrant = reg_obj,
									    amount = amount,
									    purpose = purpose,
									    date = date,
									    link = file_id,
				)
				disbursement.save()
				
			except:
				print "Save Errorr!!!! client ", client_obj," reg ", reg_obj, amount, purpose, date, file_id

		expense_list.append((amount,
				date,
				purpose,
				clientreg_id,
				nclient_id,
				approved,
				file_id,
		))

	# this takes forever
	if line['model'] == "fara.contribution":
		approved = line['fields']['approved']
		if approved == 1:
			amount = line['fields']['amount']
			if amount != None or amount != '':
				amount = float(amount)
				
				date = line['fields']['date']
				if date != None:
					date_obj = datetime.strptime(date, "%Y-%m-%d")
				else:
					date_obj = None

				line_num = line['pk']
				reg_obj = Registrant.objects.get(reg_id=reg_id)
				registration = line['fields']['registration']
				file_id = reg_file[registration]
				lobbyist = str(line['fields']['lobbyist'])
				
				candidate = line['fields']['candidate_name']
				if candidate == '':
					candidate = None
				
				committee = line['fields']['committee']
				if committee == None:
					committee = candidate
				else:
					committee = committee.strip()

				crp_id = line['fields']['candidate_id']
				if crp_id != None:
					crp_id = crp_id.replace('&', '')
					crp_id = crp_id.replace('=', '')
				
					#congressional
					if crp_id in bad_ids:
						if committee == None:
							committee = ''

						com_type= line['fields']['recipient_type']
						if candidate == None and (com_type != None or com_type != ''):
							candidate = com_type
						
						try:
							recipient = Recipient.objects.get(crp_id=crp_id, name=committee, office_detail=candidate)
						except:
							try: 
								recipient = Recipient.objects.get(crp_id=crp_id, name=committee)
							except:
								try:
									recipient = Recipient.objects.get(crp_id=crp_id)	
								except:
									if committee == None or committee == '':
										print "messed up", line
									else:
										recipient = Recipient.objects.get(name=committee)

					elif crp_id == 'N00013870' and committee == 'DLA Piper PAC':
						print "messed up- ", line

					else: 
						if len(crp_id) == 9:
							#Leasership PACs
							if "PAC" in str(line['fields']['recipient_type']):
								recipient = Recipient.objects.get(crp_id=crp_id, name=committee)
							#Members of Congress
							else:
								recipient = Recipient.objects.get(crp_id=crp_id, agency="Congress")

					#non congressional
						else:
							com_type= line['fields']['recipient_type']
							if (candidate == None or candidate == '') and (com_type != None or com_type != ''):
								candidate = com_type

							if crp_id == '':
								crp_id = None

							if candidate == '':
								candidate = None
							
							if Recipient.objects.filter(crp_id=crp_id, name=committee, office_detail=candidate).exists():
								if crp_id == None and committee == None and candidate == None:
									pass
								else:
									recipient = Recipient.objects.get(crp_id=crp_id, name=committee, office_detail=candidate)
							else:
								try:
									recipient = Recipient.objects.get(crp_id=crp_id, name=committee)
								except:
									try:
										recipient = Recipient.objects.get(crp_id=crp_id)
									except:
										try:
											recipient = Recipient.objects.get(name=committee, office_detail=com_type)
										except:
											recipients = Recipient.objects.get(name=committee)

								
				if lobbyist != None and lobbyist != '' and lobbyist != "None":
					lobbyist = Lobbyist.objects.get(lobbyist_name = lobbyist)
				else:
					lobbyist = None

				try:
					contribution = Contribution(amount = amount,
											    date = date_obj,
											    link = file_id,
											    registrant = reg_obj,
											    recipient = recipient, 
											    lobbyist = lobbyist,
					)
					contribution.save()

				except:
					print "FAIL line------", line
				
			else:
				contribution_reject.append((amount, date, file_id, reg_id, recipient.name, lobbyist, line_num))
		else:
			contribution_reject.append((amount, date, file_id, reg_id, recipient.name, lobbyist, line_num))
		
		contribution_list.append((amount, date, file_id, reg_id, recipient.name, lobbyist, line_num))


print "WRITING               ...................................."

dupes = []
writer = csv.writer(open('client-crosswalk.csv','wb'))
writer.writerow(["clientreg_id", "registration", "reg_id", "client_id", "nclient_id", "file_id"])
for k in client_crossing:	
		if k not in dupes:
			writer.writerow(k)
			dupes.append(k)
														
regwriter = csv.writer(open('registrant.csv','wb'))
for k in reg:
		regwriter.writerow(k)

clientwriter = csv.writer(open('client.csv','wb'))
for k in client_list:
	if not isinstance(k, list):
		print k, " what the hell"
	else:
		clientwriter.writerow(k)

writer = csv.writer(open('location.csv','wb'))
for k in countries.keys():
    writer.writerow([countries[k], k])

c_id = []
writer = csv.writer(open('client-by-id.csv','wb'))
for k in client_list:
	if k[8] not in c_id:
		writer.writerow(k)
		c_id.append(k[8])	

writer = csv.writer(open('Payment-fee.csv','wb'))
writer.writerow(['client', 'registrant', 'fee', 'amount', 'purpose', 'date'])
for k in pay_list:	
		writer.writerow(k)

writer = csv.writer(open('Pay_list_reject.csv','wb'))
writer.writerow(['client_name', 'client_id', 'reg_id', 'fee', 'amount', 'purpose', 'dateNEW', 'link'])
for k in pay_list:	
		writer.writerow(k)	

writer = csv.writer(open('expense_list_reject.csv','wb'))
writer.writerow(['amount', 'date', 'purpose', 'clientreg_id', 'nclient_id', 'approved', 'file_id'])
for k in pay_list:	
		writer.writerow(k)	

writer = csv.writer(open('expense_list.csv','wb'))
writer.writerow(['amount', 'date', 'purpose', 'clientreg_id', 'nclient_id', 'approved', 'file_id'])
for k in pay_list:	
		writer.writerow(k)	
json_data.close()

writer = csv.writer(open('contribution_list.csv','wb'))
writer.writerow(['amount', 'date', 'file_id', 'reg_id', 'recipient.name', 'lobbyist', 'line'])
for k in contribution_list:	
		writer.writerow(k)	
json_data.close()

writer = csv.writer(open('contribution_reject.csv','wb'))
writer.writerow(['amount', 'date', 'file_id', 'reg_id', 'recipient.name', 'lobbyist', 'line'])
for k in pay_list:	
		writer.writerow(k)	
json_data.close()










