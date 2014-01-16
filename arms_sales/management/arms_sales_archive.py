# This Python file uses the following encoding: utf-8
# Scrapes DSCA TO find proposed arms sales
import requests
import datetime
import json

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage

class Command(BaseCommand):
	def handle(self, *args, **options):
		base_url = "http://www.dsca.mil/"
		results= []
		
		# create list of links to search
		links2archives = []
		#year = int(datetime.datetime.strftime(datetime.date.today(), "%Y"))
		#month = int(datetime.datetime.strftime(datetime.date.today(), "%m"))
		year= 2013
		month = 01
		while year >= 2008:
			if year == 2008 and month == 05:
					break
			while month > 0:
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
				info = archive_body[1].select(".mas-regions")
			except IndexError:
				break
			
	
			# find info for each
			for profile in info:
				links2pages = profile.find_all("a")
				print 1
				pagelink = links2pages[0].get("href")
				pagelink = base_url + pagelink
				print 2
				title = links2pages[0].text
				print 3
				date_p = profile.find_all("div")[-1]
				date_p = date_p.text
				date = date_p.split(u" – ")
				print 4
				date = date[0]
				date = date.replace("WASHINGTON, ", "")

				# looking at individual page
				page = soupify(pagelink)
				print 5
				print_link = page.select(".print_html")[0].find_all("a")
				print 6
				print_link = print_link[0].get("href")
				print 7
				# a few don't have pdfs
				try:
					pdf_link = page.select(".file")[0].find_all("a")
				except:
					pdf_link = None
				print 8
				if pdf_link != None:
					pdf_link = pdf_link[0].get("href")
				
				print_page = soupify(print_link)
				print 9
				text = print_page.select(".print-content")[0] 

				results.append({"title":title, "date":date, "link": link, "pdf_link":pdf_link, "print_link":print_link, "text": text})
				print title	
		print "saving"
		f = open('proposed_arms_sales.json', 'w')
		data = json.dumps(results, separators=(',',':'))
		f.write(data)
		f.close()	

def soupify(url):
	page = requests.get(url)
	text = page.text
	soupy = BeautifulSoup(text)
	return soupy

# find ".mas-regions"
# find href to the page, the text will be the title
	#title could give location

# look to the pages for PDF and print friendly page
	# text could be extracted from print friendly page