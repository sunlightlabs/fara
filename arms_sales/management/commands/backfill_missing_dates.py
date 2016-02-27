# This Python file uses the following encoding: utf-8
# Scrapes DSCA TO find proposed arms sales
import requests
import json
import logging
import urllib2
from datetime import datetime, date

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings 

from arms_sales.models import Proposed

class Command(BaseCommand):
    def handle(self, *args, **options):
        sales = Proposed.objects.filter(date = None).all()
        for sale in sales:
            try:
                d = sale.text.split(" -")[0].split("WASHINGTON, ")[1].strip()
            except:
                d = sale.text.split(" -")[0].split("Washington, ")[1].strip()
            if "Sept." in d or "Sept " in d:
                    d = d.replace("Sept", "Sep")
            d = str(d)
            print d
            try:
                date_obj = datetime.strptime(d, "%b %d, %Y")
            except:
                try:    
                    date_obj = datetime.strptime(d, "%b. %d, %Y")
                except:
                    try:    
                        date_obj = datetime.strptime(d, "%b, %d, %Y")
                    except:
                        try:
                            date_obj = datetime.strptime(d, "%B %d, %Y")
                        except: 
                            print d
                            date_obj = None
            try:
                sale.date = date_obj
                sale.save()
                print "New date is: " + sale.date
            except:
                pass