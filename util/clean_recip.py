
#  Use this to get rid of the "R" error, I just do it by hand
# the rest are tests and print statements to look for mis-categorized information
import re
from FaraData.models import Recipient, Contribution, Payment, Disbursement, Contact

all_recips = Recipient.objects.all()
everything = []

all_clients = Client.objects.all()
for cl in all_clients:
	cl.delete()

all_contribs = Contribution.objects.all()
for a clean start
for c in all_contribs:
	c.delete()
print "deleted contribs"

all_payments = Payment.objects.all()
for p in all_payments:
	p.delete()
print "deleted payments"

all_disbursements = Disbursement.objects.all()
for d in all_disbursements:
	d.delete()
print "deleted disbursements"

all_contacts = Contact.objects.all()
for con in all_contacts:
	con.delete()
print "deleted_contacts"

name_dict = {}

for r in all_recips:
	# I hand delete these or re-save them
	if r.agency == "R":
		print "the r problem-- ", r.id
		agency = Recipient(agency='')
		#agency.save()
	
	crp_id = r.crp_id 
	agency = r.agency
	office_detail = r.office_detail
	name = r.name

	record = (crp_id, agency, office_detail, name)

	# Improved import, did not catch any dupes!
	if record in everything:
		print r.id, "{dupe}"
		m = Recipient.objects.get(id=r.id)
		#m.delete()

	# Improved import, did not catch any blanks!
	elif (crp_id == None or crp_id == '') and (agency == None or agency == '') and (office_detail == None or office_detail == '') and (name == None or name == ''):
		if r.title == None or r.title == '':
			print r.id, " blank", name
			#r.delete()
		
		#only  a few records like this
		else:
			recip = Recipient(id = r.id, name = r.title)
			recip.save()
				
	# improved import did not catch any of these
	if r.agency == "Congress" and office_detail == name:
		
		if Recipient.objects.filter(crp_id=crp_id, agency="Congress"):
			print "delete -- ", r
			#r.delete()
			pass

		else:
			name = r.name[:5]
			if name == "Rep. ":
				office_detail = "House"
			if name == "Sen. ":
				office_detail = "Senate"
			name = r.title[5:]

			recip = Recipient(id = r.id,
								crp_id = r.crp_id,
								agency = "Congress",
								office_detail = office_detail,
								name = name,
								title= title,
			)

			print "I would like to re-save this  -- ", recip

# getting rid of congressional dupes	
	try:
		#these look ok, just PACs with key characters
		name = str(name)
		if len(crp_id) == 9 and '(' in name or 'Sen. ' in name or 'Rep. ' in name:
			if "Staff" not in name:
				print "delete?   ", name, crp_id
				#r.delete()
	
	#this did not work as well
		if len(crp_id) == 9 and '(' in r.title:
	
			staff_list = ["staff", "Staff", 'office', 'Office', 'aide', 'Aide', 'Legislative Assistant', 'Ann LeMa', 'Advisor', 'Jason Edgar', 'Jayme White', "Amy O'Donnell", 'Lee Slater', 'offices', 'Counsel', 'Legislative', 'Scheduler', 'liaison', 'assistant', 'Assistant', 'CoS', 'LD ', 'Director', 'LA,', 'Fellow', 'Leg.', 'Huffman', 'Policy', "Secretary"]
			clean = True
			for word in staff_list:
				if word in r.title:
					clean = False

			if clean == True:
				#print " Can I axe this too-? ", r.name, r.crp_id, r.title
				pass

			# this is looking good too
			if ("Rep. (" in r.title) or ("Senator (" in r.title):
				if "accompanied" in r.title or "Policy Advisor" in r.name:
					pass
				else:
					#r.delete()
					"still need to delete--- ", r
			
			# This seems like too wide of a net
			if len(crp_id) == 9 and ('Sen. ' in r.title or 'Rep. ' in r.title) and r.agency != "Congress":
				staff_list = ["staff", "Staff", 'office', 'Office', 'aide', 'Aide', 'Legislative Assistant', 'Ann LeMa', 'Advisor', 'Jason Edgar', 'Jayme White', "Amy O'Donnell", 'Lee Slater', 'offices', 'Counsel', 'Legislative', 'Scheduler', 'liaison', 'assistant', 'Assistant', 'CoS', 'LD ', 'Director', 'LA,', 'Fellow', 'Leg.', 'Huffman', 'Policy']
				clean = True
				for word in staff_list:
					if word in r.title:
						clean = False
						
				if clean == True:
					print " Can I axe this too???- ", r.name, r.crp_id, r.title
	except:
		pass
	
	if r.agency == "Congress" and (r.title == None or r.title == ''):
		# had deleted 5 or so weird None entries
		print "IS this really a PAC?    ", r, r.id

		if Recipient.objects.filter(crp_id=crp_id, agency="Leadership PAC", name=r.name).exists():
			print "can just delete"

		else:
			new_r = Recipient(id = r.id,
						name = r.name,
						agency = "Leadership PAC",
						office_detail = r.office_detail,
						crp_id = r.crp_id,
			)
			#new_r.save()
			print "need to re-save???", r

	if name_dict.has_key(name):
		name_dict[name].append(crp_id)




	everything.append(record)	
