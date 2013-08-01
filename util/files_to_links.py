# USE THE EASY ONE INSTEAD

# crosswalking files to links
import datetime
import re

from bs4 import BeautifulSoup
import urllib
import urllib2

from fara_feed.models import Document
from FaraData.models import *


all_docs = Document.objects.all()
doc_dict = {}
stupid_list = []


for d in all_docs:
	if d.stamp_date == None:
		stamp_date = re.findall(r'\d{8}', str(d.url))
		stamp = stamp_date[0]
		stamp_date = stamp[4:6] + "/" + stamp[-2:] + "/" + stamp[:4]
		try:
			stamp_date_obj = datetime.datetime.strptime(stamp_date, "%m/%d/%Y")
			d.stamp_date = stamp_date_obj
			print d
			d.save()

			print d.stamp_date, d, "saved"
			
		except:
			print "FAIL", d 	

for d in all_docs:
	file_name =  d.url
	if file_name[:4] != "http":
		doc_id = str(d.id)
		#stamp_date = d.stamp_date
		reg_id = str(d.reg_id)
		file_name = str(file_name)

		stamp_date = re.findall(r'\d{8}', file_name)
		# creates dict of the documents that need matching
		for stamp in stamp_date:
			stamp_date = stamp[:4] + "-" + stamp[4:6]
			doc_dict[reg_id, stamp_date] = doc_id
		

print doc_dict
print stupid_list

def add_element(element, reg_date, url):
	doc_id = doc_dict[reg_date]
	doc = Document.objects.get(id=doc_id)
	link = doc.url
	print "url ", url 


	try:
		objects = element.objects.filter(link=link)
		for p in objects:
			p.link = url
			#p.save()
			print "FIXED ", element, p.link, p.id, p
	except:
		print "no"

def doj_files():
	# this changes it is just the search results for the period I am looking at
	url = "https://efile.fara.gov/pls/apex/f?p=125:20:386060883259454::NO:::"
	page = urllib2.urlopen(url).read()
	page = BeautifulSoup(page)
	filings = page.find("table", {"class" : "t14Standard"})

	for l in filings.find_all('tr'):
		row = str(l)
		url = str(re.findall(r'href="(.*?)"', row))
		url = re.sub("\['",'', re.sub("'\]", '', url))
		link = str(url)
		if url[:4] == "http":
			#print url
			info = re.findall( r'-(.*?)-', url)
			reg_id = re.sub('-','', url[25:29])
			reg_id = re.sub('S','', reg_id)
			reg_id = str(reg_id)
		
			# end_date = l.find_all('td',{"headers" : "SUPPLEMENTALEND DATE"})
			# end_date = str(end_date)[-16:-6]
			# end_date_obj = datetime.datetime.strptime(end_date, "%m/%d/%Y")
			# end_date = end_date_obj.strftime("%Y-%m-%d")

			stamp_date = l.find_all('td',{"headers" : "STAMPED/RECIEVED"})
			stamp_date = str(stamp_date)[-16:-6]

			
			try:	
				stamp_date_obj = datetime.datetime.strptime(stamp_date, "%m/%d/%Y")
				stamp_date = stamp_date_obj.strftime("%Y-%m")
			except:
				raw_date = info[1]
				stamp_date_obj = datetime.datetime.strptime(raw_date, "%Y%m%d")
				stamp_date = stamp_date_obj.strftime("%Y-%m")

			reg_date = (reg_id, stamp_date)

			if doc_dict.has_key(reg_date):
				print "Match!"
				add_element(Contact, reg_date, url)
				add_element(Payment, reg_date, url)
				add_element(Disbursement, reg_date, url)
				add_element(Contribution, reg_date, url)


				try:
					doc = Document.objects.get(id=doc_dict[reg_id, stamp_date])
					file_name = str(doc.url)

				except:
					pass


				if MetaData.objects.filter(link=file_name).exists():
					md = MetaData.objects.get(link=file_name)
					md.link = url
					md.processed = True
					md.notes = "Legacy Data"
					md.save()
					print "FIXED META DATA"
				else:
					if MetaData.objects.filter(link=url).exists():
						pass


					md = MetaData(link = url,
						processed = True,
						notes = "Legacy Data",
						)
					md.save()
					print "new md"	
				
				try:
					doc = Document.objects.get(id=doc_dict[reg_id, stamp_date])
					if Document.objects.filter(url = url).exists():
						print "Dupe", url
					else:
						doc.url = url
						#doc.save()
						print doc.processed
						print "Here we go!"
				except:
					print "NO SAVE", url, stamp_date

			else:
				pass
doj_files()


def deduper():
	urls = []
	dupes = []
	for d in all_docs:
		if d.url in urls:
			print "dupe-- ", d.url, d.processed
			dupes.append(d.url)
		else:
			urls.append(d.url)
		
	for u in dupes:
		docs = Document.objects.filter(url=u)
		for d in docs:
			if d.processed == True:
				print "Keep this ", d.url, d.processed
			else:
				print "Chuck this ", d.url, d.processed
				#look at the list before deleting 
				#d.delete()
#deduper()

 
