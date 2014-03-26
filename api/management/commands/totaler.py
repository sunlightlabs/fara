import json
import datetime


from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum

from FaraData.models import Contact, Registrant, MetaData, Payment
from fara_feed.models import Document

class Command(BaseCommand):
	help = "Creates data for the 2013 totals page."
	can_import_settings = True

	def handle(self, *args, **options):
		registrants = Registrant.objects.all()
		results = []
		for r in registrants:
			reg_id = r.reg_id
			registrant ={}
			if Document.objects.filter(processed=True,reg_id=reg_id,doc_type__in=['Supplemental','Amendment'],stamp_date__range=(datetime.date(2013,1,1), datetime.date.today())).exists():
				doc_list = []
				registrant["reg_name"] = r.reg_name
				registrant['reg_id'] = r.reg_id
				for doc in Document.objects.filter(processed=True,reg_id=reg_id,doc_type__in=['Supplemental','Amendment'],stamp_date__range=(datetime.date(2013,1,1), datetime.date.today())):
					doc_list.append(doc.url)
				
				docs_2013 = []
				s13 = 0
				for doc in doc_list:
					md = MetaData.objects.get(link=doc)
					end_date = md.end_date
					if end_date != None:
						if datetime.date(2013,1,1) < md.end_date < datetime.date(2013,12,31):
							docs_2013.append(doc)
							if "Supplemental" in doc:
								s13 = s13 + 1
							if "Registration" in doc:
								s13 = s13 + 1

				if s13 == 2:
					complete_records13 = True
					registrant['complete_records13'] = True
				else:
					registrant['complete_records13'] = s13

				if Payment.objects.filter(link__in=docs_2013):
					payments2013 = Payment.objects.filter(link__in=docs_2013).aggregate(total_pay=Sum('amount'))
					payments2013 = float(payments2013['total_pay'])
					registrant['payments2013'] = payments2013

				if Contact.objects.filter(registrant=reg_id,recipient__agency__in=["Congress", "House", "Senate"]).exists():
					registrant['federal_lobbying'] = True
					
				if Contact.objects.filter(registrant=reg_id,recipient__agency="U.S. Department of State").exists():
					registrant['state_dept_lobbying'] = True
					
				if Contact.objects.filter(registrant=reg_id,recipient__agency="Media").exists():
					registrant['pr'] = True
					
				if s13 != 0:
					results.append(registrant)
		
		print "starting"
		with open("api/computations/reg13.json", 'w') as f:
			results = json.dumps({'results':results}, separators=(',',':'))
			f.write(results)
		
		# save to file


