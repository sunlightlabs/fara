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
		stamp_date = d.stamp_date
		reg_id = str(d.reg_id)
		if stamp_date != None:
			stamp_date = stamp_date.strftime("%Y-%m-%d")
			# if doc_dict.has_key(reg_id):
			# 	doc_dict[reg_id].append([stamp_date, doc_id])
			# else:
			doc_dict[reg_id, stamp_date] = doc_id
		else:	
			stupid_list.append([reg_id, doc_id, file_name])



print doc_dict
print stupid_list

def add_element(element):
	try:
		objects = element.objects.filter(link=file_name)
		for p in objects:
			print p.link
			p.link = url
			print p.link
			p.save()
			print "FIXED ", element
	except:
		pass


url = "https://efile.fara.gov/pls/apex/f?p=125:20:1671745255320215::NO:::"
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

		raw_date = info[1]
		stamp_date = datetime.datetime.strptime(raw_date, "%Y%m%d")
		stamp_date = stamp_date.strftime("%Y-%m-%d")
	
		end_date = l.find_all('td',{"headers" : "SUPPLEMENTALEND DATE"})
		end_date = str(end_date)[-16:-6]
		end_date_obj = datetime.datetime.strptime(end_date, "%m/%d/%Y")
		end_date = end_date_obj.strftime("%Y-%m-%d")

		reg_date = (reg_id, end_date)
		#print reg_date

		if doc_dict.has_key(reg_date):
		
			try:
				doc = Document.objects.get(reg_id=reg_id, stamp_date=end_date_obj)
				file_name = str(doc.url)
				try:
					md = MetaData.objects.get(link=file_name)
					md.link = url
					md.save()
					print "FIXED META DATA"
				except:
					pass
				

				#add_element(Contact)
				#add_element(Payment)
				#add_element(Disbursement)
				#add_element(Contribution)

			except:
				pass
			
			try:
				doc = Document.objects.get(reg_id=reg_id, stamp_date=end_date_obj)
				doc.url = url
				doc.save()
				print doc.processed
				print "Here we go!"
			except:
				pass
				#print "NO SAVE", url, end_date

		else:
			pass
			#print "MISS", end_date, url

 
