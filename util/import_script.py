import json
import csv

from sys import path
from dateutil import parser

from FaraData.models import *


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


# crosswalk_reader = csv.reader(open("client-crosswalk.csv", "rU"))
# crosswalk_reader.next()
# for line in crosswalk_reader:
# 	#[clientreg_id, registration, reg_id, client_id, nclient_id, file_id]
# 	clientreg_id = line[0]
# 	registration_id = line[1]
# 	reg_id = line[2]
# 	client_id = line[3]
# 	nclient_id = line[4]
# 	try:
# 		file_id = line [5]
# 	except:
# 		file_id = "x"
# 	if client_id != None:
# 		client_nclient[client_id] = nclient_id
# 		client_reg[client_id] = reg_id
# 	if registration_id != None:
# 		reg_file[registration_id] = file_id

# print "Cross has been walked!"	

for line in data:
	if line['model'] == 'fara.registration':
		registration_id = line['pk']
		fara_id = line['fields']['registrant']	
		reg_fara[registration_id] = fara_id
		fara_reg[fara_id] = registration_id
		reg_link[registration_id] = line['fields']['source_file']
		file_id = line['fields']['source_file']
		reg_file[registration_id]= file_id

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
	    							zip = line['fields']['zipcode'],
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
print "Loop 3"
# adding a loop to make sure we are not asking for keys that don't exist yet
for line in data:
	if line['model'] == "fara.fee": 
		clientreg_id = line['fields']['client_registration']
		registration = creg_reg_client[clientreg_id][0]
		reg_id = reg_fara[registration]
		
		client_id = creg_reg_client[clientreg_id][1]
		#only works when it is getting assigned 
		nclient_id = client_nclient[client_id]
		
		client_crossing.append([clientreg_id,
					 			registration, 
					 			reg_id, 
					 			client_id, 
					 			nclient_id,
					 			file_id,
		])
		
		client_obj = Client.objects.get(id=nclient_id)
		reg_obj = Registrant.objects.get(reg_id=reg_id)
		
		fee = str(line['fields']['feesretainer']).strip()
		file_id = reg_file[registration]

		if fee == '' or fee == "None":
			fee = False
		elif fee == "x":
			fee = True
		else:
			print fee
			fee = False
		approved = line['fields']['approved']
		if approved == 1:
			approved = True
		else:
			approved = False

		date = line['fields']['date']
		date_obj = datetime.strptime(date, "%m/%d/%Y")

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
			pay_list_reject.append([client_name, client_id, reg_id, fee, line['fields']['amount'], line['fields']['purpose'], line['fields']['dateNEW'], file_id])

		pay_list.append([client_name, client_id, reg_id, fee, line['fields']['amount'], line['fields']['purpose'], line['fields']['dateNEW'], file_id])


	if line['model'] == "fara.expense": 
		clientreg_id = line['fields']['client_registration']
		registration = creg_reg_client[clientreg_id][0]
		reg_id = reg_fara[registration]
		client_id = creg_reg_client[clientreg_id][1]
		nclient_id = client_nclient[client_id]
		link = reg_link[registration]
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
		
		new_date =parser.parse(date, fuzzy=true)
		
		if type(arg) is not datetime.date:
			date = None
		else:
			#Checking to make sure the date is in the range of the document date 
			if new_date > datetime.date(2011, 04, 1) and new_date < datetime.date(2007, 1, 1):
				date = new_date
			else:
				date = None

		if approved == False or amount == '' or amount == None:
			expense_list_reject.append([amount, 
				date, 
				purpose, 
				clientreg_id, 
				nclient_id, 
				approved,
				file_id,
				])

		else:	
			try:
				reg_obj = Registrant.objects.get(reg_id=reg_id)
				disbursement = Disbursement(client = client_obj,
									    registrant = reg_obj,
									    amount = amount,
									    purpose = purpose,
									    # tooo 'effed up for now date = date,
									    link = file_id,
				)
				#disbursement.save()
				
			except:
				print "Save Errorr!!!! client ", client_obj," reg ", reg_obj, amount, purpose, date, file_id

		expense_list.append([amount,
				date,
				purpose,
				clientreg_id,
				nclient_id,
				approved,
				file_id,
		])

	if line['model'] == "fara.contribution":
		if approved == 1:
			amount = line['fields']['amount']
			if amount != None or amount != '':
				amount = float(amount)
				date = line['fields']['date']
				date_obj = datetime.strptime(date, "%m/%d/%Y")
				link = line['pk']# this is the best I can do I can't find anything to link it back
				reg_obj = Registrant.objects.get(reg_id=reg_id)
				
				crp_id = line['fields']['candidate_id']
				if crp_id == None:
					crp_id = ''
				#congressional
				if len(crp_id) == 9:
					if "PAC" in str(line['fields']['recipient_type']):
						recipient = Recipient.objects.get(crp_id=crp_id, name=committee)
					else:
						recipient = Recipient.objects.get(crp_id=crp_id, agency="Congress")
				#non congressional
				else:
					recipient = Recipient.objects.get(crp_id=crp_id, name=committee, office_detail=candidate)

				lobbyist = Lobbyist.objects.get(lobbyist_name = lobbyist)


				contribution = Contribution( amount = models.DecimalField(max_digits=8, decimal_places=2)
										    date = date_obj,
										    link = link,#place holder
										    registrant = registrant,
										    recipient = recipient, 
										    lobbyist = lobbyist,

	if line['model'] == "fara.contact": 

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
	if not isinstance(k, list):
		print k, " what the hell"
	else:
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


