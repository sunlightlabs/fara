# this corrects a registrant id error
from django.core.management.base import BaseCommand, CommandError

from FaraData.models import Registrant, Client, Payment, Contact, Disbursement, Gift, Contribution


class Command(BaseCommand):
	def handle(self, pythonpath, verbosity, traceback, settings):

		cleared = {}
		
		#wrong id, correct id, name
		incorrect_regs = (
					[3375, 3718, 'Holland & Knight LLP'], 
					[2579, 2759, 'WHITE & CASE LLP'],
					)

		
		#check that clients are correctly identified
		for i in incorrect_regs:
			
			original_id = i[0]
			new_id = i[1]
			name = i[2]
			try:
				reg = Registrant.objects.get(reg_id=original_id)
			
			except:
				reg = None
			
			if reg != None:
				if reg.reg_name == name:
					cleared[original_id] = new_id
				else:
					print "Name error", 1
			else:
				print "Name error", 2


		#go through records  to replace where they are pointing
		for cleared_id in cleared.keys():
			#Registrant.clients m2m
			old_reg = Registrant.objects.get(reg_id=cleared_id)
			new_id = cleared[cleared_id]
			new_reg = Registrant.objects.get(reg_id=new_id)
			
			# make sure new clients are accounted for, splintered means the doc we are going to erase
			splintered_clients_list =[]
			for client in old_reg.clients.all():
				splintered_clients_list.append(client)

			existing_clients = new_reg.clients.all()
			for client in splintered_clients_list:
				if client not in existing_clients:
					new_reg.clients.add(client)

			#Gift.client m2m
			gifts = Gift.objects.filter(registrant__reg_id= cleared_id)
			for g in gifts:
				g.registrant = new_reg
				g.save()

			#Contact.client fk
			contacts = Contact.objects.filter(registrant__reg_id= cleared_id)
			for c in contacts:
				c.registrant = new_reg
				c.save()
				print "contact -saving ", new_reg, "replacing ", old_reg, c.id

			#Payment.client fk
			payments = Payment.objects.filter(registrant__reg_id= cleared_id)
			for p in payments:
				p.registrant = new_reg
				p.save()
				print "payemnt -saving ", new_reg, "replacing ", old_reg, p.id
			#Disbursement.client fk
			dis = Disbursement.objects.filter(registrant__reg_id= cleared_id)
			for d in dis:
				d.registrant = new_reg
				d.save()
				print "dis -saving ", new_reg, "replacing ", old_regt, d.id
			#ClientReg.client_id fk
			client_reg = ClientReg.objects.filter(registrant__reg_id= cleared_id)
			for cr in client_reg:
				cr.registrant = new_reg
				cr.save()
				print "client reg, replacing ", old_reg, " with ", new_reg, cr.id

			#Contributions
			for contrib in Contribution.objects.filter(registrant__reg_id= cleared_id):
				contrib.registrant = new_reg
				contrib.save()
				print "contribution ", old_reg, " with ", new_reg, contrib.id

		# #looking for dupes that were in active and terminated categories 
		# for r in Registrant.objects.all():
		# 	for c in r.clients.all():
		# 		if c in r.terminated_clients.all():
		# 			r.terminated_clients.remove(c)
		# 			print r, r.reg_id, "Has dupe - ", c
		# 			#r.save()

		#get rid of bad regs
		for cleared_id in cleared.keys():
			bad_reg = Registrant.objects.get(reg_id=cleared_id) 
			bad_reg.delete()




