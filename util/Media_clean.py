from FaraData.models import *

def de_dupe(model_obj):
	for c in model_obj:
		if new_id_dict.has_key(c.id):
			c.delete()
			print c.id, c.client_name

#de_dupe(Client.objects.all())
def find_media(rec):
	media_words = ["reporter", "Reporter", "Journalist", "journalist", "writer", "Writer", "editor", "Editor", "press", "Press"]

	def add_media(record):
		if record.agency != None and record.agency != '':
			agency = str(record.agency)
			if len(agency) < 2:
				record.agency = "Media"
				record.save()
				print record
		else:
			record.agency = "Media"
			record.save()
			print record



	if  title != None:
		for word in media_words:
			if word in title:
				add_media(rec)
	if  name != None:
		for word in media_words:
			if word in name:
				add_media(rec)
	if office_detail != None:
		for word in media_words:
			if word in office_detail:
				add_media(rec)

# all_recip = Recipient.objects.all()

# for rec in all_recip:
# 	title = rec.title
# 	name =  rec.name
# 	office_detail = rec.office_detail
	# find_media(rec)

all_contacts = Contact.objects.all()
for c in all_contacts:
	recips = c.recipient.all()
	for rec in recips:
		name = rec.name

		# split media
		
		if name != None:
			if rec.title != None:
				name = name + rec.title

			if int(rec.id) > 159530:
				if len(name) >45 and "Editor" not in name and "Assistant" not in name and  "Reporter" not in name:

					count = 0

					if "Associated Press" in name:
						obj = Recipient.objects.get(id=146333)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "Politico" in name:
						obj = Recipient.objects.get(id=159564)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "Reuters" in name:
						obj = Recipient.objects.get(id=146322)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "Bloomberg" in name:
						obj = Recipient.objects.get(id=146331)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "Financial Times" in name or "FT," in name or "Financia" in name:
						obj = Recipient.objects.get(id=146300)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "LA Times" in name or "Los Angeles Times" in name:
						obj = Recipient.objects.get(id=159535)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "Voice of America" in name:
						obj = Recipient.objects.get(id=159403)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "Wall Street Journal" in name or "WSJ" in name:
						obj = Recipient.objects.get(id=146332)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "Washington Post" in name:
						obj = Recipient.objects.get(id=146321)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "Al Jazeera" in name:
						obj = Recipient.objects.get(id=157990)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "CNN" in name:
						obj = Recipient.objects.get(id=159538)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "PR-Newswire" in name:
						obj = Recipient.objects.get(id=159549)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "FP," in name or "Foreign Policy" in name:
						obj = Recipient.objects.get(id=146335)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "Huffington" in name:
						obj = Recipient.objects.get(id=159542)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "NBC" in name:
						if "CNBC" in name:
							obj = Recipient.objects.get(id=159570)
						else:
							obj = Recipient.objects.get(id=159575)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "MSNBC" in name:
						obj = Recipient.objects.get(id=159576)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "Time," in name:
						obj = Recipient.objects.get(id=159594)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "Merger Markets" in name:
						obj = Recipient.objects.get(id=159534)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "NPR" in name or "National Public Radio" in name:
						obj = Recipient.objects.get(id=159533)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "Christian Science" in name:
						obj = Recipient.objects.get(id=146301)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "Fortune" in name:
						obj = Recipient.objects.get(id=159537)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "New York Times" in name:
						obj = Recipient.objects.get(id=146226)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "ABC" in name:
						obj = Recipient.objects.get(id=159540)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1
					if "Newsweek" in name:
						obj = Recipient.objects.get(id=146220)
						print obj.name
						#c.recipient.add(obj)
						count =+ 1


					if count > .5:
						recipient = rec.id
						recip_obj = Recipient.objects.get(id=recipient)
						print recipent
						try:
							recip_obj.delete()
							print "deleted-     ", recip_obj
						except:
							print "deletion error", recip_obj

						print c.id, "Did it work?"
						print "\n\n"

	

