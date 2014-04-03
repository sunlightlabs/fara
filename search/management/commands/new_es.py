

#filter by metadata in the last 2 days 
import os
from elasticsearch import Elasticsearch

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings 

from fara_feed.management.commands.create_feed import add_file
from fara_feed.models import Document
from FaraData.models import Registrant

es = Elasticsearch(**settings.ES_CONFIG)

class Command(BaseCommand):
	help = "Puts all the new itemized data into elastic search"
	can_import_settings = True

	def handle(self, *args, **options):
	







if metadata.processed == True:
    spread_sheets.make_file(form)
    