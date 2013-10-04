from django.core.management.base import BaseCommand, CommandError
from FaraData.models import *


class Command(BaseCommand):
    can_import_settings = True

    help = "Runs methods in FaraData models that aggregate totals"

    def handle(self, *args, **options):
    	