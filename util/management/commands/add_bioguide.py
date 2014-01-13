import requests
import csv
import datetime

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

from FaraData.models import Recipient
from fara.local_settings import apikey

knownIDs = {}
failures = []

class Command(BaseCommand):
	def handle(self, *args, **options):
		recipients = Recipient.objects.filter(crp_id__isnull=False)
		filename = "data/CRP_ID_issues" + str(datetime.date.today()) + ".csv"
		writer = csv.writer(open(filename, 'wb'))
		writer.writerow(["id", "crp_id", "title", "name", "agency", "office", "local"])

		for person in recipients:
			crp = person.crp_id
			if person.bioguide_id != None:
				pass
			elif crp == "":
				pass
			elif knownIDs.has_key(crp):
				bioguide = knownIDs[crp]
				person.bioguide_id = bioguide
				person.save()
			else:
				if crp[:1] != "N":
					writer.writerow([person.id, person.crp_id, person.title, person.name, person.agency, person.office_detail, person.state_local])
				elif crp not in failures: 
					bio = find_bio(crp)
					if bio != None:
						person.bioguide_id = bio
						person.save()
					else:
						writer.writerow([person.id, person.crp_id, person.title, person.name, person.agency, person.office_detail, person.state_local])

def find_bio(crp):
	query_params = { 'crp_id': crp,
					'apikey': apikey,
	               }

	# it defaults to currently in office, so need this one too
	old_query_params = {'crp_id': crp,
					'in_office': 'false',
					'apikey': apikey,
	               }

	endpoint = 'http://congress.api.sunlightfoundation.com/legislators'
	response = requests.get(endpoint, params=query_params)
	response_old = requests.get(endpoint, params=old_query_params)
	response_url = response.url

	results = []

	data = response.json()
	old_data = response_old.json()

	bioguide_id = read_response(data, crp)
	
	if bioguide_id == None:
		bioguide_id = read_response(old_data, crp)

	return bioguide_id


def read_response(data, crp):
	for d in data["results"]:
		bioguide_id = d['bioguide_id']
		if len(bioguide_id) > 1:
			knownIDs[crp]= bioguide_id
			return bioguide_id
		else:
			failures.append(crp)
			return None


