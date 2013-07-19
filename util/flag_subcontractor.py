import csv

from FaraData.models import *

all_clients = Client.objects.all()

### From this, I made a list to merge clients and find subcontractor number
# flag_list = []

# for c in all_clients:
# 	name = str(c.client_name)

# 	if "THROUGH" in name.upper():
# 		record = [c.id, c.client_name, 'x']
# 		flag_list.append(record)
# 	else:
# 		record = [c.id, c.client_name, '']
# 		flag_list.append(record)

# writer = csv.writer(open("flagged_clients.csv", 'wb'))
# for f in flag_list:
# 	writer.writerow(f)

# Using edited doc from the previous function



doc = csv.reader(open('flagged_clients_new.csv', "rU"))
doc.next()

new_id_dict = {} # old_id : new_id
subcon_dict = {} # old_id : subcontractor  (This needs to be done first) 


for line in doc:
	original_id = line[0]
	new_id = line[2]
	subcon_id = line[3]

	if new_id != None and new_id != '':
		new_id_dict[int(original_id)] = int(new_id)
		
	if subcon_id != None and subcon_id != '':
		subcon_dict[int(original_id)] = int(subcon_id)

print new_id_dict

all_contacts = Contact.objects.all()
all_disburments = Disbursement.objects.all()
all_payments = Payment.objects.all()

def add_subcontractor():
	print subcon_dict
	print "looping"
	for c in all_payments:
		client_id = int(c.client.id)
		
		if subcon_dict.has_key(client_id):
			reg_id = subcon_dict[client_id]
			contractor = Registrant.objects.get(reg_id = reg_id)
			c.subcontractor = contractor
			print "saved", c.id
			c.save()

	print "loop 2"
	for c in all_disburments:
		client_id = int(c.client.id)
		
		if subcon_dict.has_key(client_id):
			reg_id = subcon_dict[client_id]
			contractor = Registrant.objects.get(reg_id = reg_id)
			c.subcontractor = contractor
			print "saved", c.id
			c.save()

#add_subcontractor()



def replace_clients(model_obj):
	for c in model_obj:
		client_id = int(c.client.id)
		if new_id_dict.has_key(client_id):
			new_id = new_id_dict[client_id]
			n_client = Client.objects.get(id =new_id)
			c.client = n_client
			c.save()
			print "replacing here" 

#replace_clients(all_contacts)
#replace_clients(all_disburments)
#replace_clients(all_payments)

for key in 



