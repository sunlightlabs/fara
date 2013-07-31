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
	file_name = d.url
	if file_name[:4] != "http":
		doc_id = str(d.id)
		#stamp_date = d.stamp_date
		reg_id = str(d.reg_id)
		file_name = str(file_name)

		stamp_date = re.findall(r'\d{8}', file_name)
		for stamp in stamp_date:
			stamp_date = stamp[:4] + "-" + stamp[4:6]
			doc_dict[reg_id, stamp_date] = doc_id
		

		# #Second round- stamp date
		# if stamp_date != None:
		# 	stamp_date = stamp_date.strftime("%Y-%m")
		# 	# if doc_dict.has_key(reg_id):
		# 	# 	doc_dict[reg_id].append([stamp_date, doc_id])
		# 	# else:
		# 	doc_dict[reg_id, stamp_date] = doc_id
		# else:	
		# 	stupid_list.append([reg_id, doc_id, file_name])

		# First round had the supplemental end in file name, remaining have stamp date
		# if stamp_date != None:
		# 	stamp_date = stamp_date.strftime("%Y-%m-%d")
		# 	# if doc_dict.has_key(reg_id):
		# 	# 	doc_dict[reg_id].append([stamp_date, doc_id])
		# 	# else:
		# 	doc_dict[reg_id, stamp_date] = doc_id
		# else:	
		# 	stupid_list.append([reg_id, doc_id, file_name])


print doc_dict
print stupid_list

def add_element(element):
	try:
		objects = element.objects.filter(link=file_name)
		for p in objects:
			print p.link
			p.link = url
			print p.link
			#p.save()
			print "FIXED ", element
	except:
		print "pass"

def doj_files():
	# this changes it is just the search results for the period I am looking at
	url = "https://efile.fara.gov/pls/apex/f?p=125:20:5285552019544927::NO:RP::&cs=3A8FB8A611EFC05ECC57393808F3C577B"
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

			stamp_date = l.find_all('td',{"headers" : "SUPPLEMENTALEND DATE"})
			stamp_date = str(stamp_date)[-16:-6]
			print stamp_date
			
			try:	
				stamp_date_obj = datetime.datetime.strptime(stamp_date, "%m/%d/%Y")
				stamp_date = stamp_date_obj.strftime("%Y-%m")
			except:
				raw_date = info[1]
				stamp_date_obj = datetime.datetime.strptime(raw_date, "%Y%m%d")
				stamp_date = stamp_date_obj.strftime("%Y-%m")


			reg_date = (reg_id, stamp_date)
			print reg_date
			#print reg_date

			if doc_dict.has_key(reg_date):
				print "Match!"
				try:
					doc = Document.objects.get(id=doc_dict[reg_id, stamp_date])
					file_name = str(doc.url)
					try:
						md = MetaData.objects.get(link=file_name)
						md.link = url
						md.processed = True
						md.notes = "Legacy Data"
						#md.save()
						print "FIXED META DATA"
					except:
						md = MetaData(link = url,
							processed = True,
							notes = "Legacy Data",
							)
						md.save()

					add_element(Contact)
					add_element(Payment)
					add_element(Disbursement)
					add_element(Contribution)

				except:
					pass
				
				try:
					doc = Document.objects.get(id=doc_dict[reg_id, stamp_date])
					doc.url = url
					#doc.save()
					print doc.processed
					print "Here we go!"
				except:
					pass
					print "NO SAVE", url, stamp_date

			else:
				pass
				#print "MISS", end_date, url
#doj_files()

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


 
