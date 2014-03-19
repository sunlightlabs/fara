# This Python file uses the following encoding: utf-8
# Scrapes DSCA TO find proposed arms sales
import requests
import json
import logging
import urllib2
from datetime import datetime, date

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

from arms_sales.models import Proposed
from FaraData.models import Location

logging.basicConfig()
logger = logging.getLogger(__name__)

class Command(BaseCommand):
	def handle(self, *args, **options):
		base_url = "http://www.dsca.mil/"
		results= []
		
		# create list of links to search
		links2archives = []
		year = int(datetime.strftime(datetime.today().date(), "%Y"))
		month = int(datetime.strftime(datetime.today().date(), "%m"))

		if month == 1:
			month_limit = 12
			year_limit = year - 1
		else:
			month_limit = month - 1
			year_limit = year

		# set to 2008 for full records
		while year >= year_limit:
			if year == 2008 and month == 05:
					break
			while month >= month_limit:
				if year == 2008 and month == 05:
					break
				if len(str(month)) < 2:
					month_format = "0" + str(month)
				else:
					month_format = str(month)
				link = "http://www.dsca.mil/major-arms-sales/archives/" + str(year) + month_format
				links2archives.append(link)
				month = month - 1
			month = 12
			year = year - 1

		# find titles and links to pages
		for link in links2archives:
			print "working on ", link
			archive_page = soupify(link)
			archive_body = archive_page.select(".view-content")
			# there are not entries for every month
			try:
				archive_body = archive_body[1]
			except IndexError:
				continue		
			info = archive_body.select(".mas-regions")

			# find info for each
			for profile in info:
				links2pages = profile.find_all("a")
				pagelink = links2pages[0].get("href")
				pagelink = base_url + pagelink
				
				try: 
					existing_record = Proposed.objects.get(dsca_url=pagelink)
					
				except:
					title = links2pages[0].text
					date_p = profile.find_all("div")[-1]
					date_p = date_p.text
					
					if "Defense Security Cooperation Agency\n" in date_p:
						date_p = date_p.replace("Defense Security Cooperation Agency\n", "")

					date = date_p.split(u"–")
					date = date[0]
					date = date.replace("WASHINGTON, ", "")
					date = date.strip()

					if len(date) > 25:
						date = date_p.split("-")
						date = date[0]
						date = date.replace("WASHINGTON, ", "")
						date = date.strip()

					if len(date) > 25:
						date = date_p.split("--")
						date = date[0]
						date = date.replace("WASHINGTON, ", "")
						date = date.strip()

					try:
						date_obj = datetime.strptime(date, "%b %d, %Y")
					except:
						if "Sept." in date or "Sept " in date:
							date = date.replace("Sept", "Sep")

						try:	
							date_obj = datetime.strptime(date, "%b. %d, %Y")
						except:
							pass
						try:
							date_obj = datetime.strptime(date, "%B %d, %Y")
						except: 
							date_obj = None
					
					# looking at individual page
					page = soupify(pagelink)
					print_link = page.select(".print_html")[0].find_all("a")
					print_link = print_link[0].get("href")
					
					# a few don't have pdfs
					try:
						pdf_link = page.select(".file")[0].find_all("a")
					except:
						pdf_link = None

					if pdf_link != None:
						pdf_link = pdf_link[0].get("href")
					
					print_page = soupify(print_link)
					data_text = print_page.select(".print-content")[0] 
					data_text = data_text.text
					record = Proposed(
						    title = title,
						    text = data_text,
						    date = date_obj,
						    dsca_url = pagelink,
						    pdf_url = pdf_link,
						    print_url = print_link,
						)
					
					country = title.split(u"–")
					if len(country) <= 1:
						country = title.split(u"-")
					
					country = country[0]
					country = country.replace("Government of ", "")
					country = country.replace("The ", "")
					country = country.strip()

					cleaning = {"Iraq F":"Iraq", "Republic of Korea":"South Korea", "Republic of Korea (ROK)":"South Korea", "United Arab Emirates (UAE)":"United Arab Emirates", "Taipei Economic and Cultural Representative Office in the United States":"Taiwan", "Kingdom of Morocco":"Morocco"}
					if cleaning.has_key(country):
						country = cleaning[country]

					try:
						matching_loc = Location.objects.get(location=country)
						loc_id = int(matching_loc.id)
						record.location_id = loc_id
					except:
						matching_loc = None
					
					record.save()

					#save to amazon
					try:
						file_name = "arms_pdf/" + str(record.id) + ".pdf"
						pdf_link = str(pdf_link)
						u = urllib2.urlopen(pdf_link)
						localFile = default_storage.open(file_name, 'w')
						localFile.write(u.read())
						localFile.close() 

					except:
						print 'not working'
						message = 'bad upload ' + title
						logger.error(message)
							
					results.append({"title":title, "date":date, "link": pagelink, "pdf_link":pdf_link, "print_link":print_link, "text": data_text})
					print title	
		# print "saving"
		# f = open('proposed_arms_sales.json', 'w')
		# data = json.dumps(results, separators=(',',':'))
		# f.write(data)
		# f.close()	

def soupify(url):
	page = requests.get(url)
	text = page.text
	soupy = BeautifulSoup(text)
	return soupy

