import datetime

from django.core.management.base import BaseCommand, CommandError

from FaraData import spread_sheets
from fara_feed.models import Document

class Command(BaseCommand):
    help = "Creates one zipfile of spreadsheets for each form to buckets."
    can_import_settings = True
        
    def handle(self, *args, **options):
    	docs = Document.objects.filter(doc_type__in=['Supplemental', 'Registration', 'Amendment', 'Exhibit AB' ], processed=True, uploaded=True, stamp_date__range=(datetime.date(2012,1,1), datetime.date.today()),)
    	for d in docs:
    		form_id = d.id
    		spread_sheets.make_file(form_id)