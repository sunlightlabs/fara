# This Python file uses the following encoding: utf-8
# Backfills proposed sale amounts in dollars for documents already in the database
import requests
import re

from django.conf import settings 
from django.core.management.base import BaseCommand, CommandError

from arms_sales.models import Proposed


class Command(BaseCommand):
    def handle(self, *args, **options):
        base_url = "http://www.dsca.mil/"
        proposed_sales = Proposed.objects.all()
        for p in proposed_sales:
            if p.amount != None and p.amount !=115100000.0:
                pass
            else:
                try:
                    url = p.dsca_url
                    if p.amount == 115100000.0:
                        url = p.pdf_url
                    price_string = requests.get(url).text.split("$")[1][:100]
                    raw_amount = re.compile(r'<[^>]+>').sub('', price_string).split("lion")[0]+"lion"
                    if " million" in raw_amount:
                        p.amount = float(raw_amount.strip(" million"))*1000000
                    elif " billion" in raw_amount:
                        p.amount = float(raw_amount.strip(" billion"))*1000000000
                    else:
                        p.amount = float(amount)
                    p.save()
                except:
                    print p.title+": Could not find a dollar amount"
            print str(p.amount) + ": "+p.title[:45]
        