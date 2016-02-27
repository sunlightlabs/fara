# This Python file uses the following encoding: utf-8
# Totals the amount of arms sales proposed for the previous calendar year


from django.conf import settings 
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from arms_sales.models import Proposed



class Command(BaseCommand):
    def handle(self, *args, **options):
        last_year = str(timezone.now().year-1)
        sales = Proposed.objects.filter(date__contains=last_year)
        total = 0
        for s in sales:
            if s.amount:
                total += s.amount
                print "Adding " + str(s.amount)
        print total