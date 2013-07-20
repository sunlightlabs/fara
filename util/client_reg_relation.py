# forgot to do this on import

from FaraData.models import *
from fara_feed.models import Document

#adding meta data
all_docs = Document.objects.all()
for d in all_docs:
	file_id =  d.url
	if str(d.url)[:4] == "http":
		print file_id
		d.processed = False
		d.save()
		print "working"

	else:
		d.processed = True
		d.save()
		print "working"
		


# this takes out all clients in the system
# all_reg = Registrant.objects.all()
# for r in all_reg:
# 	clients =  r.clients.all()
# 	for client in clients:
# 		r.clients.remove(client)

reg_client_dict = {}

# add them all to terminated clients- the current connections will be confirmed as active as the next two years' worth of records is added

def find_connections(model_objects):
	for c in model_objects:
		
		client_obj = c.client
		reg_obj = c.registrant
		
		reg_id = int(c.registrant.reg_id)
		client_id = int(c.client.id)

		if reg_client_dict.has_key(reg_id):
			if client_id in reg_client_dict[reg_id]:
				pass
			else:
				reg_client_dict[reg_id].append(client_id)
				
				clients =  reg_obj.terminated_clients
				client_list = []
				for client in clients.all():
					client_list.append(client.id)

				if client_obj.id in client_list:
					pass
				else:
					reg_obj.terminated_clients.add(client_obj)
					print "adding 1 ", reg_id, reg_client_dict[reg_id]

		else:
			reg_client_dict[reg_id] = [client_id]
			
			clients =  reg_obj.terminated_clients
			client_list = []
			for client in clients.all():
				client_list.append(client.id)

			if client_obj.id in client_list:
				pass
			else:
				reg_obj.terminated_clients.add(client_obj)
				print "adding 2 ", reg_id, reg_client_dict[reg_id]


# all_contacts = Contact.objects.all()
# all_disburments = Disbursement.objects.all()
# all_payments = Payment.objects.all()

# find_connections(all_payments)
# find_connections(all_contacts)
# find_connections(all_disburments)



