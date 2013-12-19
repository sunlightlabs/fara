import datetime
import re
import time
import logging

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

from fara_feed.models import Document

logging.basicConfig()
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    def handle(self, *args, **options):
        documents = Document.objects.all()
        for d in documents:
            url= d.url
            date = re.findall('\d{8}', url)
            if len(date) == 1:
                date = date[0]
                date = datetime.datetime.strptime(date, "%Y%m%d")

                if datetime.datetime.strftime(d.stamp_date, "%Y-%m-%d") != datetime.datetime.strftime(date, "%Y-%m-%d"):
                    print url
                    print date, "url date"
                    print d.stamp_date, "in system"
                    d.stamp_date = date
                    print d.stamp_date
                    d.save()
            else:
                message = 'bad date parsing ' + url
                logger.error(message)
