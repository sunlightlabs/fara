# This Python file uses the following encoding: utf-8
# adding location to proposed arms sales
import requests
import json
from datetime import datetime, date

from django.core.management.base import BaseCommand, CommandError
#from django.core.files.storage import default_storage

from arms_sales.models import Proposed
from FaraData.models import Location

class Command(BaseCommand):
	def handle(self, *args, **options):
		proposals =  Proposed.objects.all()
		for proposal in proposals:
			if proposal.location == None or proposal.location == '':
				title = proposal.title
				country = title.split(u"–")

				if len(country) <= 1:
					country = title.split(u"-")
				country = country[0]
				country = country.replace("Government of ", "")
				country = country.replace("Kingdom of ", "")
				country = country.replace("The ", "")
				country = country.strip()

				cleaning = {"Iraq F":"Iraq", "Republic of Korea":"South Korea", "Republic of Korea (ROK)":"South Korea", "United Arab Emirates (UAE)":"United Arab Emirates", "Taipei Economic and Cultural Representative Office in the United States":"Taiwan"}
				if cleaning.has_key(country):
					country = cleaning[country]

				try:
					matching_loc = Location.objects.get(location=country)
					loc_id = int(matching_loc.id)
					proposal.location_id = loc_id
					print "added loc %s" % (country)
				except:
					matching_loc = None
					print country, "NOT FOUND"
				
				proposal.location = country

				proposal.save()
				#if matching_loc == None:
				

